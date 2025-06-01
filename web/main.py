from flask import Flask, jsonify, request, render_template, redirect, flash, url_for, session
import numpy as np
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import mysql.connector
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.manifold import TSNE

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # tetap sama

# Konfigurasi koneksi database MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kecelakaan_data' # Asumsi nama database tetap
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# Fungsi K-Medoids (logika inti K-Medoids tidak berubah, hanya data inputnya)
def k_medoids(data, k=3, max_iter=100, log_progress=False):
    """
    K-Medoids clustering algorithm with detailed logging for simulation visualization.
    
    Args:
        data: numpy array of data points
        k: number of clusters to form
        max_iter: maximum number of iterations
        log_progress: whether to log detailed progress for visualization
    
    Returns:
        medoids: numpy array of medoid data points
        clusters: list of lists containing indexes of data points in each cluster
        logs: list of log messages (if log_progress=True)
        iterations: list of iteration data (if log_progress=True)
    """
    logs = []
    iterations = []
    
    m, n = data.shape
    if m == 0:  # Handle empty data
        if log_progress:
            logs.append("Error: Empty data set provided.")
            return np.array([]), [[] for _ in range(k)], logs, iterations
        return np.array([]), [[] for _ in range(k)]
        
    if m < k:  # Handle case where data points are less than k
        if log_progress:
            logs.append(f"Warning: Number of data points ({m}) is less than k ({k}).")
            logs.append("Assigning each point to its own cluster and padding with empty clusters if needed.")
        
        # Assign each point to its own cluster, pad if necessary
        medoid_indices = np.arange(m)
        medoids = data[medoid_indices]
        clusters = [[i] for i in range(m)]
        
        # Pad clusters and medoids if k > m
        for _ in range(k - m):
            clusters.append([])
        
        if log_progress:
            iter_data = {
                "medoids": [{"original_index": idx, "cluster": i} for i, idx in enumerate(medoid_indices)],
                "clusters": clusters,
                "total_cost": 0
            }
            iterations.append(iter_data)
            return medoids, clusters, logs, iterations
            
        return medoids, clusters

    # Initialize medoids randomly
    medoid_indices = np.random.choice(m, k, replace=False)
    medoids = data[medoid_indices]
    
    if log_progress:
        logs.append(f"Initialized {k} random medoids with indices: {medoid_indices.tolist()}")
    
    total_cost = 0
    
    for iter_num in range(max_iter):
        if log_progress:
            logs.append(f"Iteration {iter_num + 1}/{max_iter}")
        
        # Assign points to clusters
        clusters = [[] for _ in range(k)]
        current_cost = 0
        
        for i, point in enumerate(data):
            distances = [np.linalg.norm(point - medoid) for medoid in medoids]
            if not distances:
                if log_progress:
                    logs.append(f"Warning: No valid distances calculated for point {i}.")
                continue
                
            cluster_index = np.argmin(distances)
            clusters[cluster_index].append(i)
            current_cost += min(distances)
        
        if log_progress:
            logs.append(f"Assigned {m} points to {k} clusters with distribution: {[len(c) for c in clusters]}")
            logs.append(f"Current total cost: {current_cost:.4f}")
            
        # Select new medoids
        new_medoid_indices = []
        
        for i, cluster_indices_list in enumerate(clusters):
            if not cluster_indices_list:  # Empty cluster
                if log_progress:
                    logs.append(f"Warning: Cluster {i} is empty. Keeping previous medoid.")
                new_medoid_indices.append(medoid_indices[i])
                continue
            
            cluster_points_arr = data[cluster_indices_list]
            
            # Calculate cost for each point in the cluster to be the medoid
            costs = []
            for idx, p in enumerate(cluster_points_arr):
                cost = sum(np.linalg.norm(p - other_p) for other_p in cluster_points_arr)
                costs.append(cost)
                
            if not costs:  # Should not happen if cluster_points_arr is not empty
                if log_progress:
                    logs.append(f"Warning: Failed to calculate costs for cluster {i}. Using fallback.")
                new_medoid_indices.append(medoid_indices[i])
                continue

            new_medoid_local_idx = np.argmin(costs)
            new_medoid_global_idx = cluster_indices_list[new_medoid_local_idx]
            new_medoid_indices.append(new_medoid_global_idx)
            
            if log_progress:
                logs.append(f"Selected new medoid for cluster {i}: point {new_medoid_global_idx} with cost {min(costs):.4f}")

        if not new_medoid_indices or len(new_medoid_indices) != k:
            # Fallback if something went wrong, e.g. all clusters became empty
            if log_progress:
                logs.append("Error: Invalid medoid selection. Re-initializing medoids.")
            medoid_indices = np.random.choice(m, k, replace=False)
            medoids = data[medoid_indices]
            continue

        # Store current iteration data for visualization
        if log_progress:
            iter_data = {
                "medoids": [{"original_index": idx, "cluster": i} for i, idx in enumerate(new_medoid_indices)],
                "clusters": [c.copy() for c in clusters],
                "total_cost": current_cost
            }
            iterations.append(iter_data)
            
        # Check convergence
        if set(medoid_indices) == set(new_medoid_indices):
            if log_progress:
                logs.append(f"Converged after {iter_num + 1} iterations.")
            break
            
        medoid_indices = new_medoid_indices
        medoids = data[medoid_indices]
        total_cost = current_cost
    
    if log_progress:
        logs.append(f"Final total cost: {total_cost:.4f}")
        return medoids, clusters, logs, iterations
            
    return medoids, clusters

# Fungsi untuk memproses data dan menjalankan K-medoids dengan data baru
def process_data_for_k_medoids(df_combined, k=3, max_iter=100, columns_to_use=None, log_progress=False):
    """
    Process data and run K-Medoids clustering algorithm.
    
    Args:
        df_combined: DataFrame containing the data
        k: number of clusters to form
        max_iter: maximum number of iterations
        columns_to_use: specific columns to use for clustering (if None, defaults will be used)
        log_progress: whether to log detailed progress for visualization
        
    Returns:
        df_combined: DataFrame with cluster assignments
        medoids: numpy array of medoid data points
        logs: list of log messages (if log_progress=True)
        iterations: list of iteration data (if log_progress=True)
    """
    # Default columns for clustering
    if columns_to_use is None:
        columns_to_use = [
            'jumlah_kecelakaan', 'jumlah_meninggal', 'jumlah_luka_berat', 'jumlah_luka_ringan',
            'kendaraan_roda_dua', 'kendaraan_roda_4', # 'kendaraan_lebih_roda_4', 'kendaraan_lainnya',
            'jalan_berlubang', 'jalan_jalur_dua', 'jalan_tikungan', 'jalanan_sempit'
        ]
    
    # Ensure all requested columns exist and fill NaN
    for col in columns_to_use:
        if col not in df_combined.columns:
            df_combined[col] = 0  # Or use an alternative imputation method
    df_combined[columns_to_use] = df_combined[columns_to_use].fillna(0)

    if df_combined.empty or df_combined[columns_to_use].empty:
        df_combined['cluster'] = 0
        if log_progress:
            return df_combined, np.array([]), [], []
        return df_combined, np.array([])

    data_for_clustering = df_combined[columns_to_use].values
    
    # Normalize data (Min-Max Scaling)
    min_vals = np.min(data_for_clustering, axis=0)
    max_vals = np.max(data_for_clustering, axis=0)
    range_vals = max_vals - min_vals
    
    # Avoid division by zero if all values in a column are the same
    range_vals[range_vals == 0] = 1 
    data_normalized = (data_for_clustering - min_vals) / range_vals
    
    # Run K-Medoids clustering
    if log_progress:
        medoids, clusters, logs, iterations = k_medoids(data_normalized, k, max_iter, log_progress=True)
    else:
        medoids, clusters = k_medoids(data_normalized, k, max_iter)
    
    # Assign clusters to data points
    df_combined['cluster'] = 0  # Default cluster
    for i, cluster_indices_list in enumerate(clusters):
        for point_idx in cluster_indices_list:
            df_combined.iloc[point_idx, df_combined.columns.get_loc('cluster')] = i
    
    if log_progress:
        # Calculate feature importance for each cluster
        feature_importance = []
        for i in range(k):
            cluster_data = df_combined[df_combined['cluster'] == i]
            if not cluster_data.empty:
                cluster_features = []
                for col in columns_to_use:
                    cluster_features.append({
                        'name': col,
                        'value': cluster_data[col].mean()
                    })
                
                feature_importance.append({
                    'cluster': i,
                    'features': cluster_features
                })
        
        # Convert normalized medoids back to original scale
        original_medoids = medoids * range_vals + min_vals
        
        # Add normalized data to iterations for visualization
        for iter_data in iterations:
            for medoid in iter_data['medoids']:
                idx = medoid['original_index']
                medoid['normalized_values'] = data_normalized[idx].tolist()
                medoid['original_values'] = data_for_clustering[idx].tolist()
                medoid['feature_names'] = columns_to_use
                
        return df_combined, medoids, logs, iterations, feature_importance
        
    return df_combined, medoids

# Fungsi untuk klasifikasi tingkat keparahan (bisa disesuaikan)
def classify_severity(value):
    if value < 5: return 'Aman'       # Contoh threshold baru
    elif value < 10: return 'Waspada'
    elif value < 15: return 'Siaga'
    else: return 'Awas'

# Fungsi untuk mendapatkan koordinat gampong dari DB
def get_gampong_coordinates_from_db(nama_gampong):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT ko.latitude, ko.longitude
            FROM koordinat ko
            JOIN gampong g ON ko.gampong_id = g.id
            WHERE g.nama_gampong = %s
        """, (nama_gampong,))
        coord = cursor.fetchone()
        if coord and coord['latitude'] is not None and coord['longitude'] is not None:
            return [float(coord['latitude']), float(coord['longitude'])]
    except mysql.connector.Error as err:
        app.logger.error(f"Database error in get_gampong_coordinates_from_db: {err}")
    finally:
        cursor.close()
        conn.close()
    # Default coordinate (misalnya pusat Lhokseumawe atau Aceh)
    return [5.1794, 97.1328] # Contoh default (Lhokseumawe)

# Fungsi untuk membuat peta klaster baru
def create_cluster_map_new(df_clustered):
    aceh_center = [4.6, 96.7] # Koordinat pusat Aceh (perkiraan)
    m = folium.Map(location=aceh_center, zoom_start=9)
    
    folium.TileLayer('openstreetmap').add_to(m)
    folium.TileLayer('stamenterrain', attr='Stamen Terrain').add_to(m)
    
    marker_cluster_group = MarkerCluster(name='Klaster Kecelakaan').add_to(m)
    
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'pink']
    
    if df_clustered.empty:
        folium.LayerControl().add_to(m)
        return m

    for idx, row in df_clustered.iterrows():
        try:
            gampong_name = row.get('nama_gampong', 'Tidak Diketahui')
            lat = row.get('latitude')
            lon = row.get('longitude')

            if lat is None or lon is None:
                # Coba ambil dari DB jika tidak ada di dataframe (seharusnya sudah ada dari join)
                coords_db = get_gampong_coordinates_from_db(gampong_name)
                lat, lon = coords_db[0], coords_db[1]
            
            if lat is None or lon is None: # Still None, skip
                app.logger.warning(f"Skipping {gampong_name} due to missing coordinates.")
                continue

            lat = float(lat)
            lon = float(lon)

            cluster_id = int(row.get('cluster', 0))
            color = colors[cluster_id % len(colors)]
            
            # Hitung total kasus untuk popup dan radius (contoh)
            total_kasus = row.get('jumlah_kecelakaan', 0)
            total_korban = row.get('jumlah_meninggal', 0) + row.get('jumlah_luka_berat', 0) + row.get('jumlah_luka_ringan', 0)
            combined_total = total_kasus + total_korban
            severity_status = classify_severity(combined_total)

            popup_content = f"""
            <div style="width: 280px;">
                <h4 style="margin:0;padding:0;color:{color}">
                    {gampong_name} (Tahun: {row.get('tahun', 'N/A')})
                </h4>
                <p style="margin:5px 0;">
                    <b>Klaster:</b> {cluster_id}<br>
                    <b>Tingkat Keparahan:</b> <span style="color:{'red' if severity_status == 'Awas' else 'orange' if severity_status == 'Siaga' else 'blue'}">{severity_status}</span><br>
                    <b>Total Kasus Kecelakaan:</b> {total_kasus}<br>
                    <b>Total Korban:</b> {total_korban} (M: {row.get('jumlah_meninggal',0)}, LB: {row.get('jumlah_luka_berat',0)}, LR: {row.get('jumlah_luka_ringan',0)})
                </p>
                <h5 style="margin:10px 0 5px 0;">Detail Kendaraan Terlibat</h5>
                <ul style="margin:0;padding-left:15px;font-size:0.9em;">
                    <li>Roda 2: {row.get('kendaraan_roda_dua', 0)}</li>
                    <li>Roda 4: {row.get('kendaraan_roda_4', 0)}</li>
                    <li>Roda >4: {row.get('kendaraan_lebih_roda_4', 0)}</li>
                    <li>Lainnya: {row.get('kendaraan_lainnya', 0)}</li>
                </ul>
                <h5 style="margin:10px 0 5px 0;">Kondisi Jalan (Jumlah Kasus)</h5>
                <ul style="margin:0;padding-left:15px;font-size:0.9em;">
                    <li>Berlubang: {row.get('jalan_berlubang', 0)}</li>
                    <li>Jalur Dua: {row.get('jalan_jalur_dua', 0)}</li>
                    <li>Tikungan: {row.get('jalan_tikungan', 0)}</li>
                    <li>Sempit: {row.get('jalanan_sempit', 0)}</li>
                </ul>
            </div>
            """
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=max(5, min(combined_total / 2, 15)), # Skala radius
                popup=folium.Popup(popup_content, max_width=300),
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                tooltip=f"{gampong_name} - Klaster {cluster_id}"
            ).add_to(marker_cluster_group)
        except Exception as e:
            app.logger.error(f"Error adding marker for {row.get('nama_gampong', 'unknown')}: {e}")
            app.logger.error(f"Row data: {row.to_dict()}")
    
    folium.LayerControl().add_to(m)
    return m

# --- Helper untuk mengambil data gabungan ---
def get_combined_data(tahun_filter=None, gampong_filter=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            g.id as gampong_id, g.nama_gampong,
            kec.tahun, kec.jumlah_kecelakaan,
            ko.jumlah_meninggal, ko.jumlah_luka_berat, ko.jumlah_luka_ringan,
            jk.kendaraan_roda_dua, jk.kendaraan_roda_4, jk.kendaraan_lebih_roda_4, jk.kendaraan_lainnya,
            kjp.jalan_berlubang, kjp.jalan_jalur_dua, kjp.jalan_tikungan, kjp.jalanan_sempit,
            koord.latitude, koord.longitude
        FROM gampong g
        LEFT JOIN kecelakaan kec ON g.id = kec.gampong_id
        LEFT JOIN korban ko ON g.id = ko.gampong_id AND (kec.tahun IS NULL OR kec.tahun = ko.tahun)
        LEFT JOIN jenis_kendaraan jk ON g.id = jk.gampong_id AND (kec.tahun IS NULL OR kec.tahun = jk.tahun)
        LEFT JOIN kondisi_jalan kjp ON g.id = kjp.gampong_id AND (kec.tahun IS NULL OR kec.tahun = kjp.tahun)
        LEFT JOIN koordinat koord ON g.id = koord.gampong_id
        WHERE 1=1
    """
    params = []
    if tahun_filter and tahun_filter != 'all':
        query += " AND kec.tahun = %s" # Filter utama di tabel kecelakaan
        params.append(tahun_filter)
    if gampong_filter and gampong_filter != 'all':
        query += " AND g.nama_gampong = %s"
        params.append(gampong_filter)
    
    # Group by untuk memastikan satu baris per gampong-tahun jika ada multiple entries di sub-tabel (seharusnya tidak jika data bersih)
    # Atau handle join dengan lebih hati-hati jika ada multiple tahun per gampong di tabel selain kecelakaan
    # Untuk sementara, asumsikan data per gampong-tahun konsisten atau kita ambil yang terkait dengan kec.tahun
    # query += " GROUP BY g.id, kec.tahun" # Mungkin diperlukan jika ada duplikasi setelah join

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    df = pd.DataFrame(data)
    # Fill NaN values that might result from LEFT JOINs, especially for features used in clustering
    numeric_cols = ['jumlah_kecelakaan', 'jumlah_meninggal', 'jumlah_luka_berat', 'jumlah_luka_ringan',
                    'kendaraan_roda_dua', 'kendaraan_roda_4', 'kendaraan_lebih_roda_4', 'kendaraan_lainnya',
                    'jalan_berlubang', 'jalan_jalur_dua', 'jalan_tikungan', 'jalanan_sempit']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0
            
    if 'latitude' in df.columns:
         df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    if 'longitude' in df.columns:
         df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    return df

# Authentication functions
def login_required(f):
    """Decorator to require login for admin routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Silakan login terlebih dahulu untuk mengakses halaman admin.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def check_credentials(username, password):
    """Check if credentials are valid (both should be 'admin')"""
    return username == 'admin' and password == 'admin'

# Route untuk dashboard utama
@app.route('/')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Total kecelakaan
        cursor.execute("SELECT SUM(jumlah_kecelakaan) as total FROM kecelakaan")
        total_kecelakaan = cursor.fetchone()['total'] or 0
        
        # Total korban meninggal
        cursor.execute("SELECT SUM(jumlah_meninggal) as total FROM korban")
        total_meninggal = cursor.fetchone()['total'] or 0
        
        # Gampong paling rawan (contoh: jumlah kecelakaan > 10)
        cursor.execute("""
            SELECT COUNT(DISTINCT g.id) as total
            FROM gampong g
            JOIN kecelakaan k ON g.id = k.gampong_id
            WHERE k.jumlah_kecelakaan > 10 
        """) # Angka 10 bisa disesuaikan
        gampong_rawan = cursor.fetchone()['total'] or 0

        # Data untuk chart ringkasan kecelakaan (misal: total per tahun)
        cursor.execute("""
            SELECT tahun, SUM(jumlah_kecelakaan) as total_per_tahun
            FROM kecelakaan
            GROUP BY tahun
            ORDER BY tahun
        """)
        kecelakaan_summary_raw = cursor.fetchall()
        kecelakaan_summary_labels = [str(r['tahun']) for r in kecelakaan_summary_raw]
        kecelakaan_summary_data = [int(r['total_per_tahun']) for r in kecelakaan_summary_raw]

        # Data untuk chart ringkasan korban (misal: total meninggal, luka berat, ringan)
        cursor.execute("""
            SELECT 
                SUM(jumlah_meninggal) as total_meninggal,
                SUM(jumlah_luka_berat) as total_luka_berat,
                SUM(jumlah_luka_ringan) as total_luka_ringan
            FROM korban
        """)
        korban_summary_raw = cursor.fetchone()
        korban_summary_labels = ['Meninggal', 'Luka Berat', 'Luka Ringan']
        korban_summary_data = [
            int(korban_summary_raw['total_meninggal'] or 0),
            int(korban_summary_raw['total_luka_berat'] or 0),
            int(korban_summary_raw['total_luka_ringan'] or 0)
        ]
        
        # Ambil data gabungan untuk peta klaster di dashboard
        df_combined = get_combined_data() # Tanpa filter untuk dashboard
        
        map_html = None
        if not df_combined.empty:
            try:
                # Pastikan kolom 'tahun' ada untuk proses_data_for_k_medoids jika diperlukan
                if 'tahun' not in df_combined.columns and 'kec.tahun' in df_combined.columns:
                     df_combined.rename(columns={'kec.tahun': 'tahun'}, inplace=True)
                elif 'tahun' not in df_combined.columns: # Jika tidak ada sama sekali, buat kolom dummy atau log error
                     df_combined['tahun'] = datetime.now().year # Placeholder

                df_clustered, _ = process_data_for_k_medoids(df_combined.copy(), k=3) # k=3 default
                cluster_map_obj = create_cluster_map_new(df_clustered)
                map_html = cluster_map_obj._repr_html_() if cluster_map_obj else None
            except Exception as e:
                app.logger.error(f"Error generating cluster map for dashboard: {e}")
                map_html = "<p>Error memuat peta klaster.</p>"
        else:
            map_html = "<p>Tidak ada data untuk ditampilkan di peta.</p>"

    except mysql.connector.Error as err:
        app.logger.error(f"Database error in dashboard: {err}")
        flash(f"Database error: {err}", "danger")
        # Set default values on error
        total_kecelakaan, total_meninggal, gampong_rawan = 0, 0, 0
        kecelakaan_summary_labels, kecelakaan_summary_data = [], []
        korban_summary_labels, korban_summary_data = [], []
        map_html = "<p>Error mengambil data dari database.</p>"
    finally:
        cursor.close()
        conn.close()
        
    return render_template('dashboard.html',
                         total_kecelakaan=total_kecelakaan,
                         total_meninggal=total_meninggal, # Menggantikan total_anak
                         gampong_rawan=gampong_rawan,     # Menggantikan klaster_berbahaya
                         kecelakaan_summary_labels=json.dumps(kecelakaan_summary_labels),
                         kecelakaan_summary_data=json.dumps(kecelakaan_summary_data),
                         korban_summary_labels=json.dumps(korban_summary_labels),
                         korban_summary_data=json.dumps(korban_summary_data),
                         map_html=map_html)

# --- Chart Creation Functions (Adapted/New) ---
def create_pie_chart_summary(labels, values, title="Ringkasan"):
    if not values or sum(values) == 0: return None
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3
    )])
    fig.update_layout(title_text=title, margin=dict(t=40, b=0, l=0, r=0))
    return fig.to_html(full_html=False)

def create_bar_chart_summary(labels, values, title="Tren Tahunan", yaxis_title="Jumlah"):
    if not values: return None
    fig = go.Figure(data=[go.Bar(x=labels, y=values)])
    fig.update_layout(title_text=title, yaxis_title=yaxis_title, margin=dict(t=40, b=0, l=0, r=0))
    return fig.to_html(full_html=False)

# --- Routes for Visualizations (Adapted) ---
@app.route('/statistik_kecelakaan')
@login_required
def statistik_kecelakaan():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Data kecelakaan per gampong
    cursor.execute("""
        SELECT g.nama_gampong, SUM(k.jumlah_kecelakaan) as total_kecelakaan
        FROM gampong g
        JOIN kecelakaan k ON g.id = k.gampong_id
        GROUP BY g.nama_gampong
        ORDER BY total_kecelakaan DESC
        LIMIT 15
    """)
    gampong_data = cursor.fetchall()
    gampong_labels = [r['nama_gampong'] for r in gampong_data]
    gampong_values = [r['total_kecelakaan'] for r in gampong_data]
    bar_chart_gampong = create_bar_chart_summary(gampong_labels, gampong_values, "Total Kecelakaan per Gampong (Top 15)", "Jumlah Kecelakaan")

    # Data kecelakaan per tahun
    cursor.execute("""
        SELECT tahun, SUM(jumlah_kecelakaan) as total_kecelakaan
        FROM kecelakaan
        GROUP BY tahun
        ORDER BY tahun
    """)
    tahun_data = cursor.fetchall()
    tahun_labels = [str(r['tahun']) for r in tahun_data]
    tahun_values = [r['total_kecelakaan'] for r in tahun_data]
    line_chart_tahun = create_bar_chart_summary(tahun_labels, tahun_values, "Total Kecelakaan per Tahun", "Jumlah Kecelakaan") # Using bar for consistency

    cursor.close()
    conn.close()
    
    return render_template('statistik_kecelakaan.html', # Template baru mungkin diperlukan
                           bar_chart_gampong=bar_chart_gampong,
                           line_chart_tahun=line_chart_tahun)

@app.route('/statistik_korban')
@login_required
def statistik_korban():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Data korban per jenis (M, LB, LR)
    cursor.execute("""
        SELECT 
            SUM(jumlah_meninggal) as total_meninggal,
            SUM(jumlah_luka_berat) as total_luka_berat,
            SUM(jumlah_luka_ringan) as total_luka_ringan
        FROM korban
    """)
    korban_totals_raw = cursor.fetchone()
    korban_labels = ['Meninggal', 'Luka Berat', 'Luka Ringan']
    korban_values = [
        korban_totals_raw['total_meninggal'] or 0, 
        korban_totals_raw['total_luka_berat'] or 0, 
        korban_totals_raw['total_luka_ringan'] or 0
    ]
    pie_chart_korban = create_pie_chart_summary(korban_labels, korban_values, "Distribusi Korban")

    # Data korban per tahun (total korban)
    cursor.execute("""
        SELECT tahun, 
               SUM(jumlah_meninggal + jumlah_luka_berat + jumlah_luka_ringan) as total_korban
        FROM korban
        GROUP BY tahun
        ORDER BY tahun
    """)
    korban_tahun_data = cursor.fetchall()
    korban_tahun_labels = [str(r['tahun']) for r in korban_tahun_data]
    korban_tahun_values = [r['total_korban'] for r in korban_tahun_data]
    line_chart_korban_tahun = create_bar_chart_summary(korban_tahun_labels, korban_tahun_values, "Total Korban per Tahun", "Jumlah Korban")

    cursor.close()
    conn.close()

    return render_template('statistik_korban.html', # Template baru mungkin diperlukan
                           pie_chart_korban=pie_chart_korban,
                           line_chart_korban_tahun=line_chart_korban_tahun)


# Route untuk peta interaktif
@app.route('/peta')
@login_required
def peta_interaktif_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Ambil daftar tahun dan gampong untuk filter
    cursor.execute("SELECT DISTINCT tahun FROM kecelakaan ORDER BY tahun DESC")
    tahun_list = [row['tahun'] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT nama_gampong FROM gampong ORDER BY nama_gampong")
    gampong_list = [row['nama_gampong'] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return render_template('peta.html', # Asumsi template peta.html bisa diadaptasi
                         tahun_list=tahun_list,
                         gampong_list=gampong_list) # Ganti kecamatan_list

# API untuk data peta dengan filter (menggunakan get_combined_data)
@app.route('/api/peta_data') # URL diubah agar lebih jelas
@login_required
def api_peta_data():
    tahun = request.args.get('tahun', 'all')
    gampong_nama = request.args.get('gampong', 'all') # ganti dari kecamatan
    k_clusters = int(request.args.get('k', 3))
    
    df_combined = get_combined_data(tahun_filter=tahun, gampong_filter=gampong_nama)
    
    if df_combined.empty:
        return jsonify({'error': 'No data found for the selected filters.'}), 404
        
    df_clustered, _ = process_data_for_k_medoids(df_combined.copy(), k=k_clusters)
    
    # Siapkan hasil dalam format yang mungkin diharapkan frontend (atau frontend perlu adaptasi)
    # Ini adalah penyederhanaan dari format lama
    result_list = []
    for idx, row in df_clustered.iterrows():
        gampong_data = {
            'nama_gampong': row.get('nama_gampong'),
            'tahun': row.get('tahun'),
            'latitude': row.get('latitude'),
            'longitude': row.get('longitude'),
            'cluster': row.get('cluster'),
            'jumlah_kecelakaan': row.get('jumlah_kecelakaan', 0),
            'jumlah_meninggal': row.get('jumlah_meninggal', 0),
            'jumlah_luka_berat': row.get('jumlah_luka_berat', 0),
            'jumlah_luka_ringan': row.get('jumlah_luka_ringan', 0),
            # Tambahkan data lain jika perlu untuk popup peta
        }
        gampong_data['status_keparahan'] = classify_severity(
            gampong_data['jumlah_kecelakaan'] + 
            gampong_data['jumlah_meninggal'] + 
            gampong_data['jumlah_luka_berat'] +
            gampong_data['jumlah_luka_ringan']
        )
        result_list.append(gampong_data)
        
    return jsonify(result_list)


# --- CRUD Operations ---
# Helper untuk mengambil semua gampong (untuk dropdown)
def get_all_gampong_names():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nama_gampong FROM gampong ORDER BY nama_gampong")
    gampongs = cursor.fetchall()
    cursor.close()
    conn.close()
    return gampongs

# Route utama untuk manajemen data
@app.route('/data', methods=['GET'])
@login_required
def manage_data_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Data Gampong
        cursor.execute("SELECT * FROM gampong ORDER BY nama_gampong")
        gampong_data = cursor.fetchall()

        # Data Kecelakaan (dengan nama gampong)
        cursor.execute("""
            SELECT k.*, g.nama_gampong 
            FROM kecelakaan k JOIN gampong g ON k.gampong_id = g.id 
            ORDER BY g.nama_gampong, k.tahun DESC
        """)
        kecelakaan_data = cursor.fetchall()

        # Data Korban
        cursor.execute("""
            SELECT ko.*, g.nama_gampong 
            FROM korban ko JOIN gampong g ON ko.gampong_id = g.id
            ORDER BY g.nama_gampong, ko.tahun DESC
        """)
        korban_data = cursor.fetchall()
        
        # Data Jenis Kendaraan
        cursor.execute("""
            SELECT jk.*, g.nama_gampong
            FROM jenis_kendaraan jk JOIN gampong g ON jk.gampong_id = g.id
            ORDER BY g.nama_gampong, jk.tahun DESC
        """)
        jenis_kendaraan_data = cursor.fetchall()

        # Data Kondisi Jalan
        cursor.execute("""
            SELECT kj.*, g.nama_gampong
            FROM kondisi_jalan kj JOIN gampong g ON kj.gampong_id = g.id
            ORDER BY g.nama_gampong, kj.tahun DESC
        """)
        kondisi_jalan_data = cursor.fetchall()

        # Data Koordinat
        cursor.execute("""
            SELECT koord.*, g.nama_gampong
            FROM koordinat koord JOIN gampong g ON koord.gampong_id = g.id
            ORDER BY g.nama_gampong
        """)
        koordinat_data = cursor.fetchall()

    except mysql.connector.Error as e:
        flash(f"Database error: {e}", "danger")
        gampong_data, kecelakaan_data, korban_data, jenis_kendaraan_data, kondisi_jalan_data, koordinat_data = [], [], [], [], [], []
    finally:
        cursor.close()
        conn.close()

    all_gampongs_for_dropdown = get_all_gampong_names()

    return render_template('data.html', # Template data.html perlu diupdate besar-besaran
                           gampong_data=gampong_data,
                           kecelakaan_data=kecelakaan_data,
                           korban_data=korban_data,
                           jenis_kendaraan_data=jenis_kendaraan_data,
                           kondisi_jalan_data=kondisi_jalan_data,
                           koordinat_data=koordinat_data,
                           all_gampongs=all_gampongs_for_dropdown)

# --- CRUD Endpoints untuk setiap tabel ---
# Gampong CRUD
@app.route('/data/gampong/add', methods=['POST'])
@login_required
def add_gampong():
    if request.method == 'POST':
        try:
            # Gampong.id bukan AI, jadi harus di-supply atau punya mekanisme sendiri
            # Untuk contoh ini, kita asumsikan ID di-supply atau auto-generate jika tidak ada
            gampong_id = request.form.get('gampong_id') # Jika ID manual
            nama_gampong = request.form['nama_gampong']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            # Jika gampong_id tidak disupply dan bukan AI, ini akan error.
            # Skema create_tables_improved.sql: gampong.id INT PRIMARY KEY (bukan AI)
            # dummy_inserts_aceh.sql: INSERT INTO gampong (id, nama_gampong) VALUES (1, 'Batuphat'); (ID disupply)
            if not gampong_id:
                 flash('ID Gampong harus diisi manual.', 'danger')
                 return redirect(url_for('manage_data_page'))

            cursor.execute("INSERT INTO gampong (id, nama_gampong) VALUES (%s, %s)", 
                           (gampong_id, nama_gampong))
            conn.commit()
            flash('Data Gampong berhasil ditambahkan!', 'success')
        except mysql.connector.Error as err:
            flash(f'Database Error: {err}', 'danger')
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('manage_data_page'))

@app.route('/data/gampong/edit/<int:id>', methods=['POST'])
@login_required
def edit_gampong(id):
    if request.method == 'POST':
        try:
            nama_gampong = request.form['nama_gampong']
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE gampong SET nama_gampong = %s WHERE id = %s", (nama_gampong, id))
            conn.commit()
            flash('Data Gampong berhasil diperbarui!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('manage_data_page'))

@app.route('/data/gampong/delete/<int:id>', methods=['POST'])
@login_required
def delete_gampong(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM gampong WHERE id = %s", (id,))
        conn.commit()
        flash('Data Gampong berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    return redirect(url_for('manage_data_page'))

@app.route('/api/gampong_statistics/<int:gampong_id>')
@login_required
def get_gampong_statistics(gampong_id):
    """
    Get comprehensive statistics for a specific Gampong including yearly trends
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get Gampong info
        cursor.execute("SELECT * FROM gampong WHERE id = %s", (gampong_id,))
        gampong_info = cursor.fetchone()
        
        if not gampong_info:
            return jsonify({'error': 'Gampong not found'}), 404
        
        # Get yearly statistics for kecelakaan
        cursor.execute("""
            SELECT tahun, jumlah_kecelakaan 
            FROM kecelakaan 
            WHERE gampong_id = %s 
            ORDER BY tahun ASC
        """, (gampong_id,))
        kecelakaan_data = cursor.fetchall()
        
        # Get yearly statistics for korban
        cursor.execute("""
            SELECT tahun, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan 
            FROM korban 
            WHERE gampong_id = %s 
            ORDER BY tahun ASC
        """, (gampong_id,))
        korban_data = cursor.fetchall()
        
        # Get yearly statistics for jenis kendaraan
        cursor.execute("""
            SELECT tahun, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya 
            FROM jenis_kendaraan 
            WHERE gampong_id = %s 
            ORDER BY tahun ASC
        """, (gampong_id,))
        kendaraan_data = cursor.fetchall()
        
        # Get yearly statistics for kondisi jalan
        cursor.execute("""
            SELECT tahun, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit 
            FROM kondisi_jalan 
            WHERE gampong_id = %s 
            ORDER BY tahun ASC
        """, (gampong_id,))
        jalan_data = cursor.fetchall()
        
        # Calculate summary statistics
        total_kecelakaan = sum([item['jumlah_kecelakaan'] for item in kecelakaan_data])
        total_korban = sum([item['jumlah_meninggal'] + item['jumlah_luka_berat'] + item['jumlah_luka_ringan'] for item in korban_data])
        total_meninggal = sum([item['jumlah_meninggal'] for item in korban_data])
        
        # Get coordinate data
        cursor.execute("SELECT latitude, longitude FROM koordinat WHERE gampong_id = %s", (gampong_id,))
        koordinat = cursor.fetchone()
        
        statistics = {
            'gampong_info': gampong_info,
            'summary': {
                'total_kecelakaan': total_kecelakaan,
                'total_korban': total_korban,
                'total_meninggal': total_meninggal,
                'years_recorded': len(set([item['tahun'] for item in kecelakaan_data]))
            },
            'yearly_data': {
                'kecelakaan': kecelakaan_data,
                'korban': korban_data,
                'kendaraan': kendaraan_data,
                'jalan': jalan_data
            },
            'koordinat': koordinat
        }
        
        return jsonify(statistics)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Kecelakaan CRUD (Contoh, lainnya serupa)
@app.route('/data/kecelakaan/add', methods=['POST'])
@login_required
def add_kecelakaan():
    if request.method == 'POST':
        try:
            gampong_id = request.form['gampong_id']
            jumlah_kecelakaan = request.form['jumlah_kecelakaan']
            tahun = request.form['tahun']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (%s, %s, %s)",
                           (gampong_id, jumlah_kecelakaan, tahun))
            conn.commit()
            flash('Data Kecelakaan berhasil ditambahkan!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('manage_data_page'))

@app.route('/data/kecelakaan/edit/<int:id>', methods=['POST'])
@login_required
def edit_kecelakaan(id):
    if request.method == 'POST':
        try:
            gampong_id = request.form['gampong_id'] # Seharusnya tidak diedit jika FK, atau handle dengan hati-hati
            jumlah_kecelakaan = request.form['jumlah_kecelakaan']
            tahun = request.form['tahun']
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""UPDATE kecelakaan SET gampong_id = %s, jumlah_kecelakaan = %s, tahun = %s 
                              WHERE id = %s""", (gampong_id, jumlah_kecelakaan, tahun, id))
            conn.commit()
            flash('Data Kecelakaan berhasil diperbarui!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('manage_data_page'))


@app.route('/data/kecelakaan/delete/<int:id>', methods=['POST'])
@login_required
def delete_kecelakaan(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kecelakaan WHERE id = %s", (id,))
        conn.commit()
        flash('Data Kecelakaan berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    return redirect(url_for('manage_data_page'))

# TODO: Tambahkan endpoint CRUD serupa untuk:
# - korban
# - jenis_kendaraan
# - kondisi_jalan
# - koordinat
# Ini akan membuat file sangat panjang, jadi saya hanya contohkan gampong dan kecelakaan.
# Polanya akan sama: add (INSERT), edit (UPDATE by ID), delete (DELETE by ID).

# Korban CRUD
@app.route('/data/korban/add', methods=['POST'])
@login_required
def add_korban():
    if request.method == 'POST':
        try:
            gampong_id = request.form['gampong_id']
            jumlah_meninggal = request.form['jumlah_meninggal']
            jumlah_luka_berat = request.form['jumlah_luka_berat']
            jumlah_luka_ringan = request.form['jumlah_luka_ringan']
            tahun = request.form['tahun']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) 
                              VALUES (%s, %s, %s, %s, %s)""",
                           (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun))
            conn.commit()
            flash('Data Korban berhasil ditambahkan!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('manage_data_page'))

@app.route('/data/korban/edit/<int:id>', methods=['POST'])
@login_required
def edit_korban(id):
    if request.method == 'POST':
        try:
            gampong_id = request.form['gampong_id']
            jumlah_meninggal = request.form['jumlah_meninggal']
            jumlah_luka_berat = request.form['jumlah_luka_berat']
            jumlah_luka_ringan = request.form['jumlah_luka_ringan']
            tahun = request.form['tahun']
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""UPDATE korban SET gampong_id = %s, jumlah_meninggal = %s, jumlah_luka_berat = %s, 
                              jumlah_luka_ringan = %s, tahun = %s 
                              WHERE id = %s""", 
                           (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun, id))
            conn.commit()
            flash('Data Korban berhasil diperbarui!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('manage_data_page'))

@app.route('/data/korban/delete/<int:id>', methods=['POST'])
@login_required
def delete_korban(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM korban WHERE id = %s", (id,))
        conn.commit()
        flash('Data Korban berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    return redirect(url_for('manage_data_page'))

# Jenis Kendaraan CRUD
@app.route('/data/jenis_kendaraan/add', methods=['POST'])
@login_required
def add_jenis_kendaraan():
    if request.method == 'POST':
        try:
            gampong_id = request.form['gampong_id']
            kendaraan_roda_dua = request.form['kendaraan_roda_dua']
            kendaraan_roda_4 = request.form['kendaraan_roda_4']
            kendaraan_lebih_roda_4 = request.form['kendaraan_lebih_roda_4']
            kendaraan_lainnya = request.form['kendaraan_lainnya']
            tahun = request.form['tahun']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4,
                              kendaraan_lebih_roda_4, kendaraan_lainnya, tahun)
                              VALUES (%s, %s, %s, %s, %s, %s)""",
                           (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun))
            conn.commit()
            flash('Data Jenis Kendaraan berhasil ditambahkan!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('manage_data_page'))

@app.route('/data/jenis_kendaraan/edit/<int:id>', methods=['POST'])
@login_required
def edit_jenis_kendaraan(id):
    if request.method == 'POST':
        try:
            gampong_id = request.form['gampong_id']
            kendaraan_roda_dua = request.form['kendaraan_roda_dua']
            kendaraan_roda_4 = request.form['kendaraan_roda_4']
            kendaraan_lebih_roda_4 = request.form['kendaraan_lebih_roda_4']
            kendaraan_lainnya = request.form['kendaraan_lainnya']
            tahun = request.form['tahun']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""UPDATE jenis_kendaraan SET gampong_id = %s, kendaraan_roda_dua = %s,
                              kendaraan_roda_4 = %s, kendaraan_lebih_roda_4 = %s, kendaraan_lainnya = %s, tahun = %s
                              WHERE id = %s""",
                           (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun, id))
            conn.commit()
            flash('Data Jenis Kendaraan berhasil diperbarui!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('manage_data_page'))

@app.route('/data/jenis_kendaraan/delete/<int:id>', methods=['POST'])
@login_required
def delete_jenis_kendaraan(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jenis_kendaraan WHERE id = %s", (id,))
        conn.commit()
        flash('Data Jenis Kendaraan berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    return redirect(url_for('manage_data_page'))

# Kondisi Jalan CRUD
@app.route('/data/kondisi_jalan/add', methods=['POST'])
@login_required
def add_kondisi_jalan():
    if request.method == 'POST':
        try:
            gampong_id = request.form['gampong_id']
            jalan_berlubang = request.form['jalan_berlubang']
            jalan_jalur_dua = request.form['jalan_jalur_dua']
            jalan_tikungan = request.form['jalan_tikungan']
            jalanan_sempit = request.form['jalanan_sempit']
            tahun = request.form['tahun']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua,
                              jalan_tikungan, jalanan_sempit, tahun)
                              VALUES (%s, %s, %s, %s, %s, %s)""",
                           (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun))
            conn.commit()
            flash('Data Kondisi Jalan berhasil ditambahkan!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('manage_data_page'))

@app.route('/data/kondisi_jalan/edit/<int:id>', methods=['POST'])
@login_required
def edit_kondisi_jalan(id):
    if request.method == 'POST':
        try:
            gampong_id = request.form['gampong_id']
            jalan_berlubang = request.form['jalan_berlubang']
            jalan_jalur_dua = request.form['jalan_jalur_dua']
            jalan_tikungan = request.form['jalan_tikungan']
            jalanan_sempit = request.form['jalanan_sempit']
            tahun = request.form['tahun']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""UPDATE kondisi_jalan SET gampong_id = %s, jalan_berlubang = %s,
                              jalan_jalur_dua = %s, jalan_tikungan = %s, jalanan_sempit = %s, tahun = %s
                              WHERE id = %s""",
                           (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun, id))
            conn.commit()
            flash('Data Kondisi Jalan berhasil diperbarui!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('manage_data_page'))

@app.route('/data/kondisi_jalan/delete/<int:id>', methods=['POST'])
@login_required
def delete_kondisi_jalan(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kondisi_jalan WHERE id = %s", (id,))
        conn.commit()
        flash('Data Kondisi Jalan berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    return redirect(url_for('manage_data_page'))

# Koordinat CRUD
@app.route('/data/koordinat/add', methods=['POST'])
@login_required
def add_koordinat():
    if request.method == 'POST':
        try:
            gampong_id = request.form['gampong_id']
            latitude = request.form['latitude']
            longitude = request.form['longitude']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO koordinat (gampong_id, latitude, longitude)
                              VALUES (%s, %s, %s)""",
                           (gampong_id, latitude, longitude))
            conn.commit()
            flash('Data Koordinat berhasil ditambahkan!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('manage_data_page'))

@app.route('/data/koordinat/edit/<int:id>', methods=['POST'])
@login_required
def edit_koordinat(id):
    if request.method == 'POST':
        try:
            gampong_id = request.form['gampong_id']
            latitude = request.form['latitude']
            longitude = request.form['longitude']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""UPDATE koordinat SET gampong_id = %s, latitude = %s, longitude = %s
                              WHERE id = %s""",
                           (gampong_id, latitude, longitude, id))
            conn.commit()
            flash('Data Koordinat berhasil diperbarui!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('manage_data_page'))

@app.route('/data/koordinat/delete/<int:id>', methods=['POST'])
@login_required
def delete_koordinat(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM koordinat WHERE id = %s", (id,))
        conn.commit()
        flash('Data Koordinat berhasil dihapus.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    return redirect(url_for('manage_data_page'))


# Route untuk detail wilayah (gampong)
@app.route('/detail/<nama_gampong>')
@login_required
def detail_gampong(nama_gampong):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    gampong_detail = None
    kecelakaan_hist = []
    korban_hist = []
    map_html_detail = None

    try:
        # Detail Gampong
        cursor.execute("SELECT * FROM gampong WHERE nama_gampong = %s", (nama_gampong,))
        gampong_info = cursor.fetchone()
        if not gampong_info:
            flash("Gampong tidak ditemukan.", "warning")
            return redirect(url_for('dashboard'))
        
        gampong_id = gampong_info['id']

        # Riwayat Kecelakaan
        cursor.execute("""
            SELECT tahun, jumlah_kecelakaan 
            FROM kecelakaan 
            WHERE gampong_id = %s ORDER BY tahun DESC
        """, (gampong_id,))
        kecelakaan_hist = cursor.fetchall()

        # Riwayat Korban
        cursor.execute("""
            SELECT tahun, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan
            FROM korban
            WHERE gampong_id = %s ORDER BY tahun DESC
        """, (gampong_id,))
        korban_hist = cursor.fetchall()

        # Data untuk peta detail (hanya gampong ini)
        df_gampong = get_combined_data(gampong_filter=nama_gampong)
        if not df_gampong.empty:
            # Tidak perlu clustering untuk detail satu gampong, cukup tampilkan lokasinya
            # Atau jika ingin menunjukkan 'cluster' gampong tsb relatif thd lainnya:
            df_all_for_clustering_context = get_combined_data()
            if not df_all_for_clustering_context.empty:
                 df_clustered_all, _ = process_data_for_k_medoids(df_all_for_clustering_context.copy(), k=3)
                 # Ambil cluster untuk gampong spesifik ini
                 gampong_clustered_info = df_clustered_all[df_clustered_all['nama_gampong'] == nama_gampong]
                 if not gampong_clustered_info.empty:
                     # Buat peta hanya dengan marker gampong ini, tapi dengan info cluster
                     map_obj = create_cluster_map_new(gampong_clustered_info)
                     map_html_detail = map_obj._repr_html_()

        # Chart untuk histori kecelakaan
        kecelakaan_labels = [str(k['tahun']) for k in kecelakaan_hist]
        kecelakaan_values = [k['jumlah_kecelakaan'] for k in kecelakaan_hist]
        chart_kecelakaan_hist = create_bar_chart_summary(kecelakaan_labels, kecelakaan_values, f"Histori Jumlah Kecelakaan di {nama_gampong}")

        # Chart untuk histori korban
        korban_labels = [str(k['tahun']) for k in korban_hist]
        korban_meninggal_values = [k['jumlah_meninggal'] for k in korban_hist]
        # ... bisa tambahkan line lain untuk luka berat/ringan jika pakai line chart multi-series
        chart_korban_hist = create_bar_chart_summary(korban_labels, korban_meninggal_values, f"Histori Korban Meninggal di {nama_gampong}")


    except mysql.connector.Error as e:
        flash(f"Database error: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return render_template('detail.html', # Template detail.html perlu diadaptasi
                           gampong_nama=nama_gampong,
                           gampong_info=gampong_info,
                           kecelakaan_hist=kecelakaan_hist,
                           korban_hist=korban_hist,
                           map_html_detail=map_html_detail,
                           chart_kecelakaan_hist=chart_kecelakaan_hist,
                           chart_korban_hist=chart_korban_hist
                           )

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle login for admin dashboard access
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if check_credentials(username, password):
            session['logged_in'] = True
            session['username'] = username
            flash('Login berhasil! Selamat datang di dashboard admin.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah! Silakan coba lagi.', 'danger')
            return render_template('login.html')
    
    # If user is already logged in, redirect to dashboard
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    """
    Handle user logout
    """
    session.clear()
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('login'))

# Public Dashboard Page
@app.route('/public')
def public_dashboard():
    """
    Public dashboard for citizens to view general data and graphs
    """
    try:
        # Get year filter from query parameters
        selected_year = request.args.get('year', 'all')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get list of years for filter dropdown
        cursor.execute("SELECT DISTINCT tahun FROM kecelakaan ORDER BY tahun DESC")
        years = [row['tahun'] for row in cursor.fetchall()]
        
        # Build base query for accident data filtering
        year_filter = ""
        params = []
        if selected_year and selected_year != 'all':
            year_filter = " WHERE tahun = %s"
            params.append(selected_year)
        
        # Get accident summary data
        cursor.execute("""
            SELECT 
                COUNT(*) as total_accidents,
                SUM(jumlah_kecelakaan) as total_count
            FROM kecelakaan
        """ + year_filter, params)
        accident_summary = cursor.fetchone()
        
        # Get victim summary data
        cursor.execute("""
            SELECT 
                SUM(jumlah_meninggal) as total_deaths,
                SUM(jumlah_luka_berat) as total_serious_injuries,
                SUM(jumlah_luka_ringan) as total_minor_injuries
            FROM korban
        """ + year_filter, params)
        victim_summary = cursor.fetchone()
        
        # Combine summary data
        summary = {
            'total_accidents': accident_summary['total_count'] if accident_summary else 0,
            'total_deaths': victim_summary['total_deaths'] if victim_summary else 0,
            'total_serious_injuries': victim_summary['total_serious_injuries'] if victim_summary else 0,
            'total_minor_injuries': victim_summary['total_minor_injuries'] if victim_summary else 0
        }
        
        # Get accidents by year
        cursor.execute("""
            SELECT 
                tahun, 
                SUM(jumlah_kecelakaan) as total
            FROM kecelakaan
            GROUP BY tahun
            ORDER BY tahun
        """)
        accidents_by_year = cursor.fetchall()
        
        # Get victims by year
        cursor.execute("""
            SELECT 
                tahun,
                SUM(jumlah_meninggal) as deaths,
                SUM(jumlah_luka_berat) as serious,
                SUM(jumlah_luka_ringan) as minor
            FROM korban
            GROUP BY tahun
            ORDER BY tahun
        """)
        victims_by_year = cursor.fetchall()
        
        # Get vehicle types
        cursor.execute("""
            SELECT 
                SUM(kendaraan_roda_dua) as roda_dua,
                SUM(kendaraan_roda_4) as roda_empat,
                SUM(kendaraan_lebih_roda_4) as lebih_roda_empat,
                SUM(kendaraan_lainnya) as lainnya
            FROM jenis_kendaraan
        """ + year_filter, params)
        vehicle_types = cursor.fetchone()
        
        # Get high risk areas
        cursor.execute("""
            SELECT 
                g.nama_gampong,
                SUM(k.jumlah_kecelakaan) as accidents,
                SUM(korban.jumlah_meninggal) as deaths,
                SUM(korban.jumlah_luka_berat) as serious,
                SUM(korban.jumlah_luka_ringan) as minor
            FROM gampong g
            JOIN kecelakaan k ON g.id = k.gampong_id
            JOIN korban ON g.id = korban.gampong_id AND k.tahun = korban.tahun
        """ + year_filter + """
            GROUP BY g.id, g.nama_gampong
            ORDER BY accidents DESC
            LIMIT 5
        """, params)
        high_risk_areas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('public_dashboard.html',
                              years=years,
                              summary=summary,
                              accidents_by_year=accidents_by_year,
                              victims_by_year=victims_by_year,
                              vehicle_types=vehicle_types,
                              high_risk_areas=high_risk_areas)
                              
    except Exception as e:
        app.logger.error(f"Error in public dashboard: {e}")
        return render_template('public_dashboard.html', 
                              error=str(e),
                              years=[],
                              summary={},
                              accidents_by_year=[],
                              victims_by_year=[],
                              vehicle_types={},
                              high_risk_areas=[])

# K-Medoids Simulation Page
@app.route('/kmedoids')
@login_required
def kmedoids_page():
    """
    Render the K-Medoids simulation page with proper error handling
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Ambil daftar tahun untuk dropdown filter
        cursor.execute("SELECT DISTINCT tahun FROM kecelakaan ORDER BY tahun DESC")
        tahun_list = [row['tahun'] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return render_template('kmedoids.html', tahun_list=tahun_list)
    except Exception as e:
        app.logger.error(f"Error loading K-Medoids page: {e}")
        # Include error message and hide_sections flag to prevent JavaScript errors
        return render_template('kmedoids.html', 
                              tahun_list=[], 
                              error=str(e), 
                              hide_sections=True)

# API untuk simulasi K-Medoids dengan detail proses
@app.route('/api/kmedoids_simulation', methods=['POST'])
@login_required
def kmedoids_simulation_api():
    try:
        # Parse request parameters
        data = request.json
        k = int(data.get('k', 3))
        max_iter = int(data.get('max_iter', 100))
        year_filter = data.get('year', 'all')
        selected_features = data.get('features', [])
        
        # Validate parameters
        if k < 2:
            return jsonify({'error': 'Number of clusters (k) must be at least 2'}), 400
        if max_iter < 10:
            return jsonify({'error': 'Maximum iterations must be at least 10'}), 400
        if not selected_features or len(selected_features) < 2:
            return jsonify({'error': 'At least 2 features must be selected'}), 400
            
        # Fetch data from database with optimized query
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT DISTINCT
                g.id as gampong_id,
                g.nama_gampong,
                kec.tahun,
                COALESCE(kec.jumlah_kecelakaan, 0) as jumlah_kecelakaan,
                COALESCE(ko.jumlah_meninggal, 0) as jumlah_meninggal,
                COALESCE(ko.jumlah_luka_berat, 0) as jumlah_luka_berat,
                COALESCE(ko.jumlah_luka_ringan, 0) as jumlah_luka_ringan,
                COALESCE(jk.kendaraan_roda_dua, 0) as kendaraan_roda_dua,
                COALESCE(jk.kendaraan_roda_4, 0) as kendaraan_roda_4,
                COALESCE(jk.kendaraan_lebih_roda_4, 0) as kendaraan_lebih_roda_4,
                COALESCE(jk.kendaraan_lainnya, 0) as kendaraan_lainnya,
                COALESCE(kjp.jalan_berlubang, 0) as jalan_berlubang,
                COALESCE(kjp.jalan_jalur_dua, 0) as jalan_jalur_dua,
                COALESCE(kjp.jalan_tikungan, 0) as jalan_tikungan,
                COALESCE(kjp.jalanan_sempit, 0) as jalanan_sempit,
                koord.latitude,
                koord.longitude
            FROM gampong g
            LEFT JOIN kecelakaan kec ON g.id = kec.gampong_id
            LEFT JOIN korban ko ON g.id = ko.gampong_id AND kec.tahun = ko.tahun
            LEFT JOIN jenis_kendaraan jk ON g.id = jk.gampong_id AND kec.tahun = jk.tahun
            LEFT JOIN kondisi_jalan kjp ON g.id = kjp.gampong_id AND kec.tahun = kjp.tahun
            LEFT JOIN koordinat koord ON g.id = koord.gampong_id
            WHERE kec.jumlah_kecelakaan IS NOT NULL
        """
        
        params = []
        if year_filter and year_filter != 'all':
            query += " AND kec.tahun = %s"
            params.append(year_filter)
            
        cursor.execute(query, tuple(params))
        raw_data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not raw_data:
            return jsonify({'error': 'No data found for the selected filters'}), 404
            
        # Create DataFrame from data
        df = pd.DataFrame(raw_data)
        
        # Ensure selected features exist in DataFrame
        for feature in selected_features:
            if feature not in df.columns:
                df[feature] = 0
                
        # Run K-Medoids with detailed logging
        start_time = time.time()
        df_clustered, medoids, logs, iterations, feature_importance = process_data_for_k_medoids(
            df.copy(), 
            k=k, 
            max_iter=max_iter, 
            columns_to_use=selected_features, 
            log_progress=True
        )
        execution_time = time.time() - start_time
        
        # Generate t-SNE visualization if data is large enough
        tsne_results = []
        if len(df) >= 5:  # Need at least 5 points for meaningful t-SNE
            try:
                # Only use selected features for t-SNE
                tsne_data = df[selected_features].values
                
                # Normalize data
                min_vals = np.min(tsne_data, axis=0)
                max_vals = np.max(tsne_data, axis=0)
                range_vals = max_vals - min_vals
                range_vals[range_vals == 0] = 1
                tsne_data_norm = (tsne_data - min_vals) / range_vals
                
                # Apply t-SNE
                tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(df) - 1))
                tsne_result = tsne.fit_transform(tsne_data_norm)
                
                # Create result for visualization
                for i, (x, y) in enumerate(tsne_result):
                    cluster = df_clustered.iloc[i]['cluster']
                    tsne_results.append({
                        'index': i,
                        'x': float(x),
                        'y': float(y),
                        'cluster': int(cluster),
                        'label': df.iloc[i]['nama_gampong']
                    })
            except Exception as e:
                app.logger.error(f"Error generating t-SNE: {e}")
          # Prepare result
        result = {
            'input_data': df.to_dict('records'),
            'results': {
                'k': k,
                'num_data_points': len(df),
                'execution_time': execution_time,
                'medoids': medoids.tolist() if isinstance(medoids, np.ndarray) else medoids,
                'logs': logs,
                'iterations': iterations,
                'feature_importance': feature_importance,
                'tsne_results': tsne_results,
                'year_filter': year_filter,
                'selected_features': selected_features
            }
        }
        
        return jsonify(result)
    
    except mysql.connector.Error as e:
        app.logger.error(f"Database error in K-Medoids simulation: {e}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        app.logger.error(f"Error in K-Medoids simulation: {e}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    finally:
        # Ensure database connection is closed
        try:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
        except:
            pass

        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
