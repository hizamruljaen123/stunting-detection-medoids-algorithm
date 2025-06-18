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
    """    # Default columns for clustering
    if columns_to_use is None:
        columns_to_use = [
            'jumlah_kecelakaan', 'jumlah_meninggal', 'luka_berat', 'luka_ringan',
            'kendaraan_roda_dua', 'kendaraan_roda_4', 'kendaraan_lebih_roda_4', 'kendaraan_lainnya',
            'jalan_berlubang', 'jalan_jalur_dua'
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

# Fungsi untuk klasifikasi tingkat keparahan (disesuaikan dengan kategori korban baru)
def classify_severity(value):
    if value < 8: return 'Aman'       # Threshold yang disesuaikan dengan luka berat/ringan
    elif value < 15: return 'Waspada'
    elif value < 25: return 'Siaga'
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
            total_meninggal = row.get('jumlah_meninggal', 0)
            total_luka_berat = row.get('luka_berat', 0)
            total_luka_ringan = row.get('luka_ringan', 0)
            total_korban = total_meninggal + total_luka_berat + total_luka_ringan
            combined_total = total_kasus + total_korban
            severity_status = classify_severity(combined_total)

            popup_content = f"""
            <div style="width: 300px;">
                <h4 style="margin:0;padding:0;color:{color}">
                    {gampong_name} (Tahun: {row.get('tahun', 'N/A')})
                </h4>
                <p style="margin:5px 0;">
                    <b>Klaster:</b> {cluster_id}<br>
                    <b>Tingkat Keparahan:</b> <span style="color:{'red' if severity_status == 'Awas' else 'orange' if severity_status == 'Siaga' else 'blue'}">{severity_status}</span><br>
                    <b>Total Kasus Kecelakaan:</b> {total_kasus}
                </p>
                <h5 style="margin:10px 0 5px 0;">Ringkasan Korban</h5>
                <ul style="margin:0;padding-left:15px;font-size:0.9em;">
                    <li>Meninggal: {total_meninggal}</li>
                    <li>Luka Berat: {total_luka_berat}</li>
                    <li>Luka Ringan: {total_luka_ringan}</li>
                    <li><b>Total Korban: {total_korban}</b></li>
                </ul>
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
    
    # Check if new columns exist first
    cursor.execute("SHOW COLUMNS FROM korban LIKE 'luka_berat'")
    has_luka_berat = cursor.fetchone() is not None
    
    cursor.execute("SHOW COLUMNS FROM korban LIKE 'luka_ringan'")
    has_luka_ringan = cursor.fetchone() is not None
    
    if has_luka_berat and has_luka_ringan:
        # Use new columns if they exist
        query = """
            SELECT
                g.id as gampong_id, g.nama_gampong,
                kec.tahun, kec.jumlah_kecelakaan,
                ko.jumlah_meninggal, ko.luka_berat, ko.luka_ringan,
                jk.kendaraan_roda_dua, jk.kendaraan_roda_4, jk.kendaraan_lebih_roda_4, jk.kendaraan_lainnya,
                kjp.jalan_berlubang, kjp.jalan_jalur_dua,
                koord.latitude, koord.longitude
            FROM gampong g
            LEFT JOIN kecelakaan kec ON g.id = kec.gampong_id
            LEFT JOIN korban ko ON g.id = ko.gampong_id AND (kec.tahun IS NULL OR kec.tahun = ko.tahun)
            LEFT JOIN jenis_kendaraan jk ON g.id = jk.gampong_id AND (kec.tahun IS NULL OR kec.tahun = jk.tahun)
            LEFT JOIN kondisi_jalan kjp ON g.id = kjp.gampong_id AND (kec.tahun IS NULL OR kec.tahun = kjp.tahun)
            LEFT JOIN koordinat koord ON g.id = koord.gampong_id
            WHERE 1=1
        """
    else:
        # Fallback to old structure
        query = """
            SELECT
                g.id as gampong_id, g.nama_gampong,
                kec.tahun, kec.jumlah_kecelakaan,
                ko.jumlah_meninggal,
                jk.kendaraan_roda_dua, jk.kendaraan_roda_4, jk.kendaraan_lebih_roda_4, jk.kendaraan_lainnya,
                kjp.jalan_berlubang, kjp.jalan_jalur_dua,
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
    # query += " GROUP BY g.id, kec.tahun" # Mungkin diperlukan jika ada duplikasi setelah join

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    df = pd.DataFrame(data)
    
    # Fill NaN values that might result from LEFT JOINs, especially for features used in clustering
    basic_cols = ['jumlah_kecelakaan', 'jumlah_meninggal',
                  'kendaraan_roda_dua', 'kendaraan_roda_4', 'kendaraan_lebih_roda_4', 'kendaraan_lainnya',
                  'jalan_berlubang', 'jalan_jalur_dua']
    
    # Add new columns if they exist, otherwise create them with sample data
    if 'luka_berat' not in df.columns:
        # Generate sample data based on deaths
        if 'jumlah_meninggal' in df.columns:
            df['luka_berat'] = df['jumlah_meninggal'] * 1.5  # Sample: 1.5x deaths
        else:
            df['luka_berat'] = 0
    
    if 'luka_ringan' not in df.columns:
        # Generate sample data based on deaths
        if 'jumlah_meninggal' in df.columns:
            df['luka_ringan'] = df['jumlah_meninggal'] * 2.3  # Sample: 2.3x deaths
        else:
            df['luka_ringan'] = 0
    
    numeric_cols = basic_cols + ['luka_berat', 'luka_ringan']
    
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
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get available years for filter
        cursor.execute("SELECT DISTINCT tahun FROM kecelakaan ORDER BY tahun DESC")
        available_years = [str(row['tahun']) for row in cursor.fetchall()]
        selected_year_map = request.args.get('year_map', 'all')
<<<<<<< HEAD

=======
        
        # Get k-medoids parameters from query parameters
        k_clusters = int(request.args.get('k', 3))
        max_iterations = int(request.args.get('max_iter', 100))
        
>>>>>>> main
        # Total kecelakaan
        cursor.execute("SELECT SUM(jumlah_kecelakaan) as total FROM kecelakaan")
        total_kecelakaan = cursor.fetchone()['total'] or 0

        # Gampong paling rawan (contoh: jumlah kecelakaan > 10)
        cursor.execute("""
            SELECT COUNT(DISTINCT g.id) as total
            FROM gampong g
            JOIN kecelakaan k ON g.id = k.gampong_id
            WHERE k.jumlah_kecelakaan > 10 
        """)
        gampong_rawan = cursor.fetchone()['total'] or 0

        # Data untuk chart distribusi jenis kendaraan
        if selected_year_map and selected_year_map != 'all':
            cursor.execute("""
                SELECT 
                    SUM(COALESCE(kendaraan_roda_dua,0)) as roda_dua,
                    SUM(COALESCE(kendaraan_roda_4,0)) as roda_4,
                    SUM(COALESCE(kendaraan_lebih_roda_4,0)) as lebih_roda_4,
                    SUM(COALESCE(kendaraan_lainnya,0)) as lainnya
                FROM jenis_kendaraan
                WHERE tahun = %s
            """, (selected_year_map,))
        else:
            cursor.execute("""
                SELECT 
                    SUM(COALESCE(kendaraan_roda_dua,0)) as roda_dua,
                    SUM(COALESCE(kendaraan_roda_4,0)) as roda_4,
                    SUM(COALESCE(kendaraan_lebih_roda_4,0)) as lebih_roda_4,
                    SUM(COALESCE(kendaraan_lainnya,0)) as lainnya
                FROM jenis_kendaraan
            """)
        kendaraan_row = cursor.fetchone()
        jenis_kendaraan_labels = ["Roda 2", "Roda 4", "> Roda 4", "Lainnya"]
        jenis_kendaraan_data = [int(kendaraan_row['roda_dua'] or 0), int(kendaraan_row['roda_4'] or 0), int(kendaraan_row['lebih_roda_4'] or 0), int(kendaraan_row['lainnya'] or 0)]

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

<<<<<<< HEAD
        # Ambil data gabungan untuk peta klaster di dashboard
        df_combined = get_combined_data() # Tanpa filter untuk dashboard
=======
        # Data untuk chart ringkasan korban
        cursor.execute("""
            SELECT SUM(jumlah_meninggal) as total_meninggal
            FROM korban
        """)
        korban_summary_raw = cursor.fetchone()
        korban_summary_labels = ['Meninggal']
        korban_summary_data = [int(korban_summary_raw['total_meninggal'] or 0)]

        # Ambil data gabungan untuk peta klaster
        df_combined = get_combined_data()

>>>>>>> main
        map_html = None
        if not df_combined.empty:
            try:
                if 'tahun' not in df_combined.columns and 'kec.tahun' in df_combined.columns:
                    df_combined.rename(columns={'kec.tahun': 'tahun'}, inplace=True)
                elif 'tahun' not in df_combined.columns:
                    df_combined['tahun'] = datetime.now().year
<<<<<<< HEAD
=======

                # Apply year filter if specified
>>>>>>> main
                if selected_year_map and selected_year_map != 'all':
                    df_combined = df_combined[df_combined['tahun'].astype(str) == selected_year_map]
                if not df_combined.empty:
                    df_clustered, cluster_logs = process_data_for_k_medoids(df_combined.copy(), k=k_clusters, max_iter=max_iterations, log_progress=True)
                    cluster_map_obj = create_cluster_map_new(df_clustered)
                    map_html = cluster_map_obj._repr_html_() if cluster_map_obj else None
                else:
                    map_html = "<p>Tidak ada data untuk tahun yang dipilih.</p>"
            except Exception as e:
                app.logger.error(f"Error generating cluster map for dashboard: {e}")
                map_html = "<p>Error memuat peta klaster.</p>"
        else:
            map_html = "<p>Tidak ada data untuk ditampilkan di peta.</p>"
    except mysql.connector.Error as err:
        app.logger.error(f"Database error in dashboard: {err}")
        flash(f"Database error: {err}", "danger")
<<<<<<< HEAD
        total_kecelakaan, gampong_rawan = 0, 0
        jenis_kendaraan_labels, jenis_kendaraan_data = [], []
        kecelakaan_summary_labels, kecelakaan_summary_data = [], []
        map_html = "<p>Error mengambil data dari database.</p>"
=======
        total_kecelakaan, total_meninggal, gampong_rawan = 0, 0, 0
        kecelakaan_summary_labels, kecelakaan_summary_data = [], []
        korban_summary_labels, korban_summary_data = [], []
        available_years = []
        selected_year_map = 'all'
        k_clusters = 3
        max_iterations = 100
        map_html = None
>>>>>>> main
    finally:
        cursor.close()
        conn.close()
    return render_template('dashboard.html',
        total_kecelakaan=total_kecelakaan,
        gampong_rawan=gampong_rawan,
        jenis_kendaraan_labels=json.dumps(jenis_kendaraan_labels),
        jenis_kendaraan_data=json.dumps(jenis_kendaraan_data),
        kecelakaan_summary_labels=json.dumps(kecelakaan_summary_labels),
        kecelakaan_summary_data=json.dumps(kecelakaan_summary_data),
        map_html=map_html,
        available_years=available_years,
        selected_year_map=selected_year_map,
        k_clusters=k_clusters,
        max_iterations=max_iterations
    )

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

<<<<<<< HEAD
    # Data korban per tahun (semua kategori korban)
    cursor.execute("""
        SELECT tahun,
               SUM(jumlah_meninggal) as total_meninggal,
               SUM(luka_berat) as total_luka_berat,
               SUM(luka_ringan) as total_luka_ringan,
               SUM(jumlah_meninggal + luka_berat + luka_ringan) as total_korban
=======
    # Data korban meninggal
    cursor.execute("""
        SELECT SUM(jumlah_meninggal) as total_meninggal
        FROM korban
    """)
    korban_totals_raw = cursor.fetchone()
    korban_labels = ['Meninggal']
    korban_values = [korban_totals_raw['total_meninggal'] or 0]
    pie_chart_korban = create_pie_chart_summary(korban_labels, korban_values, "Total Korban Meninggal")

    # Data korban meninggal per tahun
    cursor.execute("""
        SELECT tahun, SUM(jumlah_meninggal) as total_korban
>>>>>>> main
        FROM korban
        GROUP BY tahun
        ORDER BY tahun
    """)
    korban_tahun_data = cursor.fetchall()
    korban_tahun_labels = [str(r['tahun']) for r in korban_tahun_data]
    korban_tahun_values = [r['total_korban'] for r in korban_tahun_data]
<<<<<<< HEAD
    line_chart_korban_tahun = create_bar_chart_summary(korban_tahun_labels, korban_tahun_values, "Total Korban per Tahun", "Jumlah Korban")

    # Statistik tambahan: Top 10 total korban per gampong
    cursor.execute("""
        SELECT g.nama_gampong, 
               SUM(k.jumlah_meninggal + k.luka_berat + k.luka_ringan) as total_korban
        FROM korban k
        JOIN gampong g ON k.gampong_id = g.id
        GROUP BY g.nama_gampong
        ORDER BY total_korban DESC
        LIMIT 10
    """)
    korban_gampong_data = cursor.fetchall()
    korban_gampong_labels = [r['nama_gampong'] for r in korban_gampong_data]
    korban_gampong_values = [r['total_korban'] for r in korban_gampong_data]
    bar_chart_korban_gampong = create_bar_chart_summary(korban_gampong_labels, korban_gampong_values, "Top 10 Total Korban per Gampong", "Jumlah Korban")

    # Chart untuk distribusi kategori korban (meninggal, luka berat, luka ringan)
    cursor.execute("""
        SELECT SUM(jumlah_meninggal) as total_meninggal,
               SUM(luka_berat) as total_luka_berat,
               SUM(luka_ringan) as total_luka_ringan
        FROM korban
    """)
    kategori_korban_row = cursor.fetchone()
    kategori_korban_labels = ["Meninggal", "Luka Berat", "Luka Ringan"]
    kategori_korban_values = [
        int(kategori_korban_row['total_meninggal'] or 0),
        int(kategori_korban_row['total_luka_berat'] or 0),
        int(kategori_korban_row['total_luka_ringan'] or 0)
    ]
    pie_chart_kategori_korban = create_pie_chart_summary(kategori_korban_labels, kategori_korban_values, "Distribusi Kategori Korban")

    # Statistik tambahan: Korban per jenis kendaraan (join dengan jenis_kendaraan)
    cursor.execute("""
        SELECT
            SUM(jk.kendaraan_roda_dua * k.jumlah_meninggal) as roda_dua,
            SUM(jk.kendaraan_roda_4 * k.jumlah_meninggal) as roda_4,
            SUM(jk.kendaraan_lebih_roda_4 * k.jumlah_meninggal) as lebih_roda_4,
            SUM(jk.kendaraan_lainnya * k.jumlah_meninggal) as lainnya
        FROM korban k
        JOIN jenis_kendaraan jk ON k.gampong_id = jk.gampong_id AND k.tahun = jk.tahun
    """)
    korban_kendaraan_row = cursor.fetchone()
    korban_kendaraan_labels = ["Roda 2", "Roda 4", "> Roda 4", "Lainnya"]
    korban_kendaraan_values = [
        int(korban_kendaraan_row['roda_dua'] or 0),
        int(korban_kendaraan_row['roda_4'] or 0),
        int(korban_kendaraan_row['lebih_roda_4'] or 0),
        int(korban_kendaraan_row['lainnya'] or 0)
    ]
    pie_chart_korban_kendaraan = create_pie_chart_summary(korban_kendaraan_labels, korban_kendaraan_values, "Distribusi Korban per Jenis Kendaraan")

    # Statistik tambahan: Korban per kondisi jalan (join dengan kondisi_jalan)
    cursor.execute("""
        SELECT
            SUM(kj.jalan_berlubang * k.jumlah_meninggal) as jalan_berlubang,
            SUM(kj.jalan_jalur_dua * k.jumlah_meninggal) as jalan_jalur_dua
        FROM korban k
        JOIN kondisi_jalan kj ON k.gampong_id = kj.gampong_id AND k.tahun = kj.tahun
    """)
    korban_jalan_row = cursor.fetchone()
    korban_jalan_labels = ["Jalan Berlubang", "Jalan Jalur Dua"]
    korban_jalan_values = [
        int(korban_jalan_row['jalan_berlubang'] or 0),
        int(korban_jalan_row['jalan_jalur_dua'] or 0)
    ]
    pie_chart_korban_jalan = create_pie_chart_summary(korban_jalan_labels, korban_jalan_values, "Distribusi Korban per Kondisi Jalan")

    cursor.close()
    conn.close()    
    return render_template('statistik_korban.html',
                           line_chart_korban_tahun=line_chart_korban_tahun,
                           bar_chart_korban_gampong=bar_chart_korban_gampong,
                           pie_chart_kategori_korban=pie_chart_kategori_korban,
                           pie_chart_korban_kendaraan=pie_chart_korban_kendaraan,
                           pie_chart_korban_jalan=pie_chart_korban_jalan)
=======
    line_chart_korban_tahun = create_bar_chart_summary(korban_tahun_labels, korban_tahun_values, "Total Korban Meninggal per Tahun", "Jumlah Korban Meninggal")

    cursor.close()
    conn.close()

    return render_template('statistik_korban.html',
                           pie_chart_korban=pie_chart_korban,
                           line_chart_korban_tahun=line_chart_korban_tahun)
>>>>>>> main


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
            # Tambahkan data lain jika perlu untuk popup peta
        }
        gampong_data['status_keparahan'] = classify_severity(
            gampong_data['jumlah_kecelakaan'] +
            gampong_data['jumlah_meninggal']
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
            SELECT tahun, jumlah_meninggal
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
            SELECT tahun, jalan_berlubang, jalan_jalur_dua
            FROM kondisi_jalan
            WHERE gampong_id = %s
            ORDER BY tahun ASC
        """, (gampong_id,))
        jalan_data = cursor.fetchall()
        
        # Calculate summary statistics
        total_kecelakaan = sum([item['jumlah_kecelakaan'] for item in kecelakaan_data])
        total_korban = sum([item['jumlah_meninggal'] for item in korban_data])
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

@app.route('/data/korban/add', methods=['POST'])
@login_required
def add_korban():
    if request.method == 'POST':
        try:
            gampong_id = request.form['gampong_id']
            jumlah_meninggal = request.form.get('jumlah_meninggal', 0)
            luka_berat = request.form.get('luka_berat', 0)
            luka_ringan = request.form.get('luka_ringan', 0)
            tahun = request.form['tahun']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if luka_berat and luka_ringan columns exist
            cursor.execute("SHOW COLUMNS FROM korban LIKE 'luka_berat'")
            has_luka_berat = cursor.fetchone() is not None
            
            if has_luka_berat:
                cursor.execute("""INSERT INTO korban (gampong_id, jumlah_meninggal, luka_berat, luka_ringan, tahun)
                                  VALUES (%s, %s, %s, %s, %s)""",
                               (gampong_id, jumlah_meninggal, luka_berat, luka_ringan, tahun))
            else:
                cursor.execute("""INSERT INTO korban (gampong_id, jumlah_meninggal, tahun)
                                  VALUES (%s, %s, %s)""",
                               (gampong_id, jumlah_meninggal, tahun))            
            conn.commit()
            
            # Check if it's an AJAX request
            if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Data Korban berhasil ditambahkan!'})
            
            flash('Data Korban berhasil ditambahkan!', 'success')
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
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
            jumlah_meninggal = request.form.get('jumlah_meninggal', 0)
            luka_berat = request.form.get('luka_berat', 0)
            luka_ringan = request.form.get('luka_ringan', 0)
            tahun = request.form['tahun']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if luka_berat and luka_ringan columns exist
            cursor.execute("SHOW COLUMNS FROM korban LIKE 'luka_berat'")
            has_luka_berat = cursor.fetchone() is not None
            
            if has_luka_berat:
                cursor.execute("""UPDATE korban SET gampong_id = %s, jumlah_meninggal = %s, 
                                  luka_berat = %s, luka_ringan = %s, tahun = %s
                                  WHERE id = %s""",
                               (gampong_id, jumlah_meninggal, luka_berat, luka_ringan, tahun, id))
            else:
                cursor.execute("""UPDATE korban SET gampong_id = %s, jumlah_meninggal = %s, tahun = %s
                                  WHERE id = %s""",
                               (gampong_id, jumlah_meninggal, tahun, id))            
            conn.commit()
            
            # Check if it's an AJAX request
            if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Data Korban berhasil diperbarui!'})
            
            flash('Data Korban berhasil diperbarui!', 'success')
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': f'Error: {str(e)}'})
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
            SELECT tahun, jumlah_meninggal
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
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
<<<<<<< HEAD
        # Filter tahun
        cursor.execute("SELECT DISTINCT tahun FROM kecelakaan ORDER BY tahun DESC")
        available_years = [str(row['tahun']) for row in cursor.fetchall()]
        selected_year_map = request.args.get('year_map', 'all')

        # Peta (gunakan get_combined_data dan create_cluster_map_new)
        df_combined = get_combined_data(tahun_filter=selected_year_map)
=======
        # Get available years for filter
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT DISTINCT tahun FROM kecelakaan ORDER BY tahun DESC")
        available_years = [str(row['tahun']) for row in cursor.fetchall()]
        
        # Get parameters from query string
        selected_year_map = request.args.get('year_map', 'all')
        k_clusters = int(request.args.get('k', 3))
        max_iterations = int(request.args.get('max_iter', 100))
        
        # Total kecelakaan
        cursor.execute("SELECT SUM(jumlah_kecelakaan) as total FROM kecelakaan")
        total_kecelakaan = cursor.fetchone()['total'] or 0
        
        # Total korban meninggal
        cursor.execute("SELECT SUM(jumlah_meninggal) as total FROM korban")
        total_meninggal = cursor.fetchone()['total'] or 0
        
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

        # Data untuk chart ringkasan korban
        cursor.execute("""
            SELECT SUM(jumlah_meninggal) as total_meninggal
            FROM korban
        """)
        korban_summary_raw = cursor.fetchone()
        korban_summary_labels = ['Meninggal']
        korban_summary_data = [int(korban_summary_raw['total_meninggal'] or 0)]

        # Ambil data gabungan untuk peta klaster
        df_combined = get_combined_data()

>>>>>>> main
        map_html = None
        if not df_combined.empty:
            try:
                if 'tahun' not in df_combined.columns and 'kec.tahun' in df_combined.columns:
                    df_combined.rename(columns={'kec.tahun': 'tahun'}, inplace=True)
                elif 'tahun' not in df_combined.columns:
                    df_combined['tahun'] = datetime.now().year
<<<<<<< HEAD
                if selected_year_map and selected_year_map != 'all':
                    df_combined = df_combined[df_combined['tahun'].astype(str) == selected_year_map]
                if not df_combined.empty:
                    df_clustered, _ = process_data_for_k_medoids(df_combined.copy(), k=3)
=======

                # Apply year filter if specified
                if selected_year_map and selected_year_map != 'all':
                    df_combined = df_combined[df_combined['tahun'].astype(str) == selected_year_map]

                if not df_combined.empty:
                    df_clustered, cluster_logs = process_data_for_k_medoids(df_combined.copy(), k=k_clusters, max_iter=max_iterations, log_progress=True)
>>>>>>> main
                    cluster_map_obj = create_cluster_map_new(df_clustered)
                    map_html = cluster_map_obj._repr_html_() if cluster_map_obj else None
                else:
                    map_html = "<p>Tidak ada data untuk tahun yang dipilih.</p>"
            except Exception as e:
<<<<<<< HEAD
=======
                app.logger.error(f"Error generating cluster map for public dashboard: {e}")
>>>>>>> main
                map_html = "<p>Error memuat peta klaster.</p>"
        else:
            map_html = "<p>Tidak ada data untuk ditampilkan di peta.</p>"

<<<<<<< HEAD
        # Statistik kecelakaan per tahun
        cursor.execute("""
            SELECT tahun, SUM(jumlah_kecelakaan) as total_kecelakaan
            FROM kecelakaan
            GROUP BY tahun
            ORDER BY tahun
        """)
        kecelakaan_tahun_data = cursor.fetchall()
        kecelakaan_tahun_labels = [str(r['tahun']) for r in kecelakaan_tahun_data]
        kecelakaan_tahun_values = [r['total_kecelakaan'] for r in kecelakaan_tahun_data]
        line_chart_kecelakaan_tahun = create_bar_chart_summary(kecelakaan_tahun_labels, kecelakaan_tahun_values, "Total Kecelakaan per Tahun", "Jumlah Kecelakaan")

        # Statistik kecelakaan per gampong (Top 15)
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
        bar_chart_kecelakaan_gampong = create_bar_chart_summary(gampong_labels, gampong_values, "Total Kecelakaan per Gampong (Top 15)", "Jumlah Kecelakaan")        # Statistik korban per tahun (semua kategori)
        cursor.execute("""
            SELECT tahun, 
                   SUM(jumlah_meninggal + luka_berat + luka_ringan) as total_korban
            FROM korban
            GROUP BY tahun
            ORDER BY tahun
        """)
        korban_tahun_data = cursor.fetchall()
        korban_tahun_labels = [str(r['tahun']) for r in korban_tahun_data]
        korban_tahun_values = [r['total_korban'] for r in korban_tahun_data]
        line_chart_korban_tahun = create_bar_chart_summary(korban_tahun_labels, korban_tahun_values, "Total Korban per Tahun", "Jumlah Korban")

        # Statistik korban per gampong (Top 10)
        cursor.execute("""
            SELECT g.nama_gampong, 
                   SUM(k.jumlah_meninggal + k.luka_berat + k.luka_ringan) as total_korban
            FROM korban k
            JOIN gampong g ON k.gampong_id = g.id
            GROUP BY g.nama_gampong
            ORDER BY total_korban DESC
            LIMIT 10
        """)
        korban_gampong_data = cursor.fetchall()
        korban_gampong_labels = [r['nama_gampong'] for r in korban_gampong_data]
        korban_gampong_values = [r['total_korban'] for r in korban_gampong_data]
        bar_chart_korban_gampong = create_bar_chart_summary(korban_gampong_labels, korban_gampong_values, "Top 10 Total Korban per Gampong", "Jumlah Korban")

        # Statistik korban per jenis kendaraan
        cursor.execute("""
            SELECT
                SUM(jk.kendaraan_roda_dua * k.jumlah_meninggal) as roda_dua,
                SUM(jk.kendaraan_roda_4 * k.jumlah_meninggal) as roda_4,
                SUM(jk.kendaraan_lebih_roda_4 * k.jumlah_meninggal) as lebih_roda_4,
                SUM(jk.kendaraan_lainnya * k.jumlah_meninggal) as lainnya
        FROM korban k
        JOIN jenis_kendaraan jk ON k.gampong_id = jk.gampong_id AND k.tahun = jk.tahun
        """)
        korban_kendaraan_row = cursor.fetchone()
        korban_kendaraan_labels = ["Roda 2", "Roda 4", "> Roda 4", "Lainnya"]
        korban_kendaraan_values = [
            int(korban_kendaraan_row['roda_dua'] or 0),
            int(korban_kendaraan_row['roda_4'] or 0),
            int(korban_kendaraan_row['lebih_roda_4'] or 0),
            int(korban_kendaraan_row['lainnya'] or 0)
        ]
        pie_chart_korban_kendaraan = create_pie_chart_summary(korban_kendaraan_labels, korban_kendaraan_values, "Distribusi Korban per Jenis Kendaraan")

        # Statistik korban per kondisi jalan
        cursor.execute("""
            SELECT
                SUM(kj.jalan_berlubang * k.jumlah_meninggal) as jalan_berlubang,
                SUM(kj.jalan_jalur_dua * k.jumlah_meninggal) as jalan_jalur_dua
            FROM korban k
            JOIN kondisi_jalan kj ON k.gampong_id = kj.gampong_id AND k.tahun = kj.tahun
        """)
        korban_jalan_row = cursor.fetchone()
        korban_jalan_labels = ["Jalan Berlubang", "Jalan Jalur Dua"]
        korban_jalan_values = [
            int(korban_jalan_row['jalan_berlubang'] or 0),
            int(korban_jalan_row['jalan_jalur_dua'] or 0)
        ]
        pie_chart_korban_jalan = create_pie_chart_summary(korban_jalan_labels, korban_jalan_values, "Distribusi Korban per Kondisi Jalan")

=======
    except mysql.connector.Error as err:
        app.logger.error(f"Database error in public dashboard: {err}")
        total_kecelakaan, total_meninggal = 0, 0
        kecelakaan_summary_labels, kecelakaan_summary_data = [], []
        korban_summary_labels, korban_summary_data = [], []
        available_years = []
        selected_year_map = 'all'
        k_clusters = 3
        max_iterations = 100
        map_html = None
>>>>>>> main
    finally:
        cursor.close()
        conn.close()

    return render_template('public_dashboard.html',
<<<<<<< HEAD
        map_html=map_html,
        available_years=available_years,
        selected_year_map=selected_year_map,
        line_chart_kecelakaan_tahun=line_chart_kecelakaan_tahun,
        bar_chart_kecelakaan_gampong=bar_chart_kecelakaan_gampong,
        line_chart_korban_tahun=line_chart_korban_tahun,
        bar_chart_korban_gampong=bar_chart_korban_gampong,
        pie_chart_korban_kendaraan=pie_chart_korban_kendaraan,
        pie_chart_korban_jalan=pie_chart_korban_jalan
    )

# --- Simulasi K-Medoids (API dan Halaman) ---
# K-Medoids Simulation Page
=======
        total_kecelakaan=total_kecelakaan,
        total_meninggal=total_meninggal,
        korban_summary_labels=json.dumps(korban_summary_labels),
        korban_summary_data=json.dumps(korban_summary_data),
        kecelakaan_summary_labels=json.dumps(kecelakaan_summary_labels),
        kecelakaan_summary_data=json.dumps(kecelakaan_summary_data),
        map_html=map_html,
        available_years=available_years,
        selected_year_map=selected_year_map,
        k_clusters=k_clusters,
        max_iterations=max_iterations
    )

# --- K-Medoids Simulation Page ---
>>>>>>> main
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
        
        # Check if new columns exist first
        cursor.execute("SHOW COLUMNS FROM korban LIKE 'luka_berat'")
        has_luka_berat = cursor.fetchone() is not None
        
        cursor.execute("SHOW COLUMNS FROM korban LIKE 'luka_ringan'")
        has_luka_ringan = cursor.fetchone() is not None
        
        if has_luka_berat and has_luka_ringan:
            # Use new columns if they exist
            query = """
                SELECT DISTINCT
                    g.id as gampong_id,
                    g.nama_gampong,
                    kec.tahun,
                    COALESCE(kec.jumlah_kecelakaan, 0) as jumlah_kecelakaan,
                    COALESCE(ko.jumlah_meninggal, 0) as jumlah_meninggal,
                    COALESCE(ko.luka_berat, 0) as luka_berat,
                    COALESCE(ko.luka_ringan, 0) as luka_ringan,
                    COALESCE(jk.kendaraan_roda_dua, 0) as kendaraan_roda_dua,
                    COALESCE(jk.kendaraan_roda_4, 0) as kendaraan_roda_4,
                    COALESCE(jk.kendaraan_lebih_roda_4, 0) as kendaraan_lebih_roda_4,
                    COALESCE(jk.kendaraan_lainnya, 0) as kendaraan_lainnya,
                    COALESCE(kjp.jalan_berlubang, 0) as jalan_berlubang,
                    COALESCE(kjp.jalan_jalur_dua, 0) as jalan_jalur_dua,
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
        else:
            # Fallback to old structure
            query = """
                SELECT DISTINCT
                    g.id as gampong_id,
                    g.nama_gampong,
                    kec.tahun,
                    COALESCE(kec.jumlah_kecelakaan, 0) as jumlah_kecelakaan,
                    COALESCE(ko.jumlah_meninggal, 0) as jumlah_meninggal,
                    COALESCE(jk.kendaraan_roda_dua, 0) as kendaraan_roda_dua,
                    COALESCE(jk.kendaraan_roda_4, 0) as kendaraan_roda_4,
                    COALESCE(jk.kendaraan_lebih_roda_4, 0) as kendaraan_lebih_roda_4,
                    COALESCE(jk.kendaraan_lainnya, 0) as kendaraan_lainnya,
                    COALESCE(kjp.jalan_berlubang, 0) as jalan_berlubang,
                    COALESCE(kjp.jalan_jalur_dua, 0) as jalan_jalur_dua,
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
        
        # Add missing victim columns if they don't exist
        if 'luka_berat' not in df.columns:
            if 'jumlah_meninggal' in df.columns:
                df['luka_berat'] = df['jumlah_meninggal'] * 1.5  # Sample: 1.5x deaths
            else:
                df['luka_berat'] = 0
        
        if 'luka_ringan' not in df.columns:
            if 'jumlah_meninggal' in df.columns:
                df['luka_ringan'] = df['jumlah_meninggal'] * 2.3  # Sample: 2.3x deaths
            else:
                df['luka_ringan'] = 0
        
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

# API endpoint untuk reprocess data dashboard
@app.route('/api/reprocess_dashboard', methods=['POST'])
def reprocess_dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Recalculate dashboard statistics
        dashboard_data = {}
        
        # Total kecelakaan
        cursor.execute("SELECT COUNT(*) as total FROM kecelakaan")
        dashboard_data['total_kecelakaan'] = cursor.fetchone()['total']
        
        # Total korban
        cursor.execute("SELECT COUNT(*) as total FROM korban")
        dashboard_data['total_korban'] = cursor.fetchone()['total']
        
        # Total gampong
        cursor.execute("SELECT COUNT(*) as total FROM gampong")
        dashboard_data['total_gampong'] = cursor.fetchone()['total']
        
        # Kecelakaan per tahun (karena tidak ada kolom tanggal, hanya tahun)
        cursor.execute("""
        SELECT
            tahun as tahun,
            SUM(jumlah_kecelakaan) as jumlah
        FROM kecelakaan
        GROUP BY tahun
        ORDER BY tahun
        """)
        dashboard_data['kecelakaan_per_tahun'] = cursor.fetchall()
        
        # Top 5 gampong dengan kecelakaan terbanyak
        cursor.execute("""
        SELECT g.nama_gampong, COUNT(k.id) as jumlah_kecelakaan
        FROM gampong g
        LEFT JOIN kecelakaan k ON g.id = k.gampong_id
        GROUP BY g.id
        ORDER BY jumlah_kecelakaan DESC
        LIMIT 5
        """)
        dashboard_data['top_gampong'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Dashboard data berhasil diperbarui',
            'data': dashboard_data
        })
        
    except Exception as e:
        app.logger.error(f"Error in reprocess_dashboard: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# API endpoint untuk reprocess data statistik kecelakaan
@app.route('/api/reprocess_statistik_kecelakaan', methods=['POST'])
def reprocess_statistik_kecelakaan():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Recalculate accident statistics
        statistik_data = {}
        
        # Kecelakaan per gampong
        cursor.execute("""
        SELECT g.nama_gampong, COUNT(k.id) as jumlah_kecelakaan
        FROM gampong g
        LEFT JOIN kecelakaan k ON g.id = k.gampong_id
        GROUP BY g.id, g.nama_gampong
        ORDER BY jumlah_kecelakaan DESC
        """)
        statistik_data['per_gampong'] = cursor.fetchall()
        
        # Kecelakaan per tahun (karena tidak ada kolom tanggal, hanya tahun)
        cursor.execute("""
        SELECT
            tahun as tahun,
            SUM(jumlah_kecelakaan) as jumlah
        FROM kecelakaan
        GROUP BY tahun
        ORDER BY tahun
        """)
        statistik_data['per_tahun'] = cursor.fetchall()
        
        # Kecelakaan per tahun (karena tidak ada kolom jenis_kecelakaan)
        cursor.execute("""
        SELECT tahun, SUM(jumlah_kecelakaan) as jumlah
        FROM kecelakaan
        GROUP BY tahun
        ORDER BY jumlah DESC
        """)
        statistik_data['per_tahun'] = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Data statistik kecelakaan berhasil diperbarui',
            'data': statistik_data
        })
        
    except Exception as e:
        app.logger.error(f"Error in reprocess_statistik_kecelakaan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# API endpoint untuk reprocess data statistik korban
@app.route('/api/reprocess_statistik_korban', methods=['POST'])
def reprocess_statistik_korban():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Recalculate victim statistics
        statistik_data = {}
        
        # Korban meninggal per tahun
        cursor.execute("""
        SELECT tahun, SUM(jumlah_meninggal) as jumlah
        FROM korban
        GROUP BY tahun
        ORDER BY tahun
        """)
        statistik_data['per_tahun'] = cursor.fetchall()

        # Total korban meninggal
        cursor.execute("""
        SELECT SUM(jumlah_meninggal) as jumlah
        FROM korban
        """)
        statistik_data['total'] = cursor.fetchone()

        # Korban meninggal per gampong
        cursor.execute("""
        SELECT g.nama_gampong, SUM(k.jumlah_meninggal) as jumlah
        FROM korban k
        JOIN gampong g ON k.gampong_id = g.id
        GROUP BY g.nama_gampong
        ORDER BY jumlah DESC
        """)
        statistik_data['per_gampong'] = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Statistik korban berhasil diperbarui'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API endpoint untuk reprocess data korban usia
@app.route('/api/reprocess_korban_usia', methods=['POST'])
def reprocess_korban_usia():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Recalculate age-based victim statistics
        usia_data = {}
        
        # Data korban berdasarkan tahun (karena tidak ada kolom usia atau jenis_kelamin)
        cursor.execute("""
        SELECT
            tahun,
            SUM(jumlah_meninggal) as jumlah_korban
        FROM korban
        GROUP BY tahun
        ORDER BY tahun
        """)
        usia_data['data_tahun'] = cursor.fetchall()

        # Total korban meninggal
        cursor.execute("SELECT SUM(jumlah_meninggal) as total_korban FROM korban")
        usia_data['total_korban'] = cursor.fetchone()['total_korban'] or 0

        # Rata-rata korban per tahun
        cursor.execute("SELECT AVG(jumlah_meninggal) as rata_rata_korban FROM korban WHERE jumlah_meninggal IS NOT NULL")
        rata_rata = cursor.fetchone()['rata_rata_korban']
        usia_data['rata_rata_korban'] = round(rata_rata, 2) if rata_rata else 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Data korban berdasarkan usia berhasil diperbarui',
            'data': usia_data
        })
        
    except Exception as e:
        app.logger.error(f"Error in reprocess_korban_usia: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# API endpoint untuk reprocess data jenis kecelakaan
@app.route('/api/reprocess_jenis_kecelakaan', methods=['POST'])
def reprocess_jenis_kecelakaan():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Recalculate accident type statistics
        jenis_data = {}
        
        # Data kecelakaan per tahun (karena tidak ada kolom jenis_kecelakaan)
        cursor.execute("""
        SELECT
            tahun,
            SUM(jumlah_kecelakaan) as jumlah_kecelakaan,
            COUNT(DISTINCT k.id) as total_kejadian
        FROM kecelakaan k
        GROUP BY tahun
        ORDER BY jumlah_kecelakaan DESC
        """)
        jenis_data['data_tahun'] = cursor.fetchall()

        # Total kecelakaan
        cursor.execute("SELECT SUM(jumlah_kecelakaan) as total_kecelakaan FROM kecelakaan")
        jenis_data['total_kecelakaan'] = cursor.fetchone()['total_kecelakaan'] or 0

        # Tahun dengan kecelakaan terbanyak
        cursor.execute("""
        SELECT tahun, SUM(jumlah_kecelakaan) as jumlah
        FROM kecelakaan
        GROUP BY tahun
        ORDER BY jumlah DESC
        LIMIT 1
        """)
        jenis_data['tahun_terbanyak'] = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Data jenis kecelakaan berhasil diperbarui',
            'data': jenis_data
        })
        
    except Exception as e:
        app.logger.error(f"Error in reprocess_jenis_kecelakaan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)



