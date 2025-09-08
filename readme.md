# Stunting Detection using Medoids Algorithm

## Introduction
Stunting detection aims to identify children at risk of stunting (low height-for-age).  
The **k-Medoids (PAM – Partitioning Around Medoids)** algorithm is a clustering technique similar to k-Means but uses actual data points as cluster centers (medoids).  
It is more robust to outliers, making it suitable for health-related data.

### Example Features
- Age (months)  
- Weight (kg)  
- Height (cm)  
- Family Income  
- Parents’ Education  
- Nutritional Intake  

## How k-Medoids Works
1. Initialize `k` medoids randomly.  
2. Assign each data point to the nearest medoid.  
3. Compute total cost (sum of distances of points to their medoid).  
4. Swap medoid with non-medoid points if it reduces cost.  
5. Repeat until no improvement occurs.

## Python Implementation (Simplified Example)
```python
import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances
from pyclustering.cluster.kmedoids import kmedoids
from pyclustering.utils import calculate_distance_matrix

# Example dataset (toy data)
data = [
    [24, 10, 80],  # age, weight, height
    [36, 14, 95],
    [18, 8, 75],
    [30, 12, 90],
    [20, 9, 78],
    [40, 15, 100],
    [28, 11, 85]
]

data = np.array(data)

# Initial medoid indices (randomly chosen)
initial_medoids = [0, 1]  # choose k=2 clusters

# Create k-Medoids instance
kmedoids_instance = kmedoids(data, initial_medoids, metric='euclidean')

# Run clustering
kmedoids_instance.process()

# Get clusters and medoids
clusters = kmedoids_instance.get_clusters()
medoids = kmedoids_instance.get_medoids()

print("Clusters:", clusters)
print("Medoids:", medoids)
