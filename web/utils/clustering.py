import pandas as pd
from sklearn_extra.cluster import KMedoids
from sklearn.preprocessing import StandardScaler
from .models import JenisKecelakaan, KorbanUsia

def perform_clustering(data_type='jenis_kecelakaan', n_clusters=3):
    """Perform K-Medoids clustering on accident data"""
    # Load data from database
    if data_type == 'jenis_kecelakaan':
        query = JenisKecelakaan.query
        features = ['Tabrakan', 'Terjatuh', 'Tertabrak', 'Terbalik', 
                   'Kecelakaan_Tunggal', 'Kecelakaan_Beruntun']
    else:
        query = KorbanUsia.query  
        features = ['anak_anak', 'remaja', 'dewasa', 'paruh_baya', 'lansia']

    df = pd.read_sql(query.statement, query.session.bind)
    
    # Preprocess data
    scaler = StandardScaler()
    X = scaler.fit_transform(df[features])
    
    # Cluster using K-Medoids
    kmedoids = KMedoids(n_clusters=n_clusters, random_state=42)
    clusters = kmedoids.fit_predict(X)
    
    # Prepare results
    results = {
        'labels': clusters.tolist(),
        'centers': scaler.inverse_transform(kmedoids.cluster_centers_).tolist(),
        'kecamatan': df['Kecamatan'].tolist(),
        'features': features,
        'data_type': data_type
    }
    
    return results