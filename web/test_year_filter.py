#!/usr/bin/env python3

import mysql.connector
import pandas as pd
from main import get_db_connection

# Test if year filtering is working in backend
conn = get_db_connection()
cursor = conn.cursor(dictionary=True)

# Test with specific year filter
year_filter = '2023'
query = '''
    SELECT DISTINCT
        g.id as gampong_id,
        g.nama_gampong,
        kec.tahun,
        COALESCE(kec.jumlah_kecelakaan, 0) as jumlah_kecelakaan,
        koord.latitude,
        koord.longitude
    FROM gampong g
    LEFT JOIN kecelakaan kec ON g.id = kec.gampong_id
    LEFT JOIN koordinat koord ON g.id = koord.gampong_id
    WHERE kec.jumlah_kecelakaan IS NOT NULL
    AND kec.tahun = %s
'''

cursor.execute(query, (year_filter,))
filtered_data = cursor.fetchall()

print(f'Year filter: {year_filter}')
print(f'Filtered data count: {len(filtered_data)}')
print('Sample filtered data:')
for i, row in enumerate(filtered_data[:5]):
    print(f'  {i+1}. {row["nama_gampong"]} - Tahun: {row["tahun"]}')

# Test without year filter
query_all = '''
    SELECT DISTINCT
        g.id as gampong_id,
        g.nama_gampong,
        kec.tahun,
        COALESCE(kec.jumlah_kecelakaan, 0) as jumlah_kecelakaan,
        koord.latitude,
        koord.longitude
    FROM gampong g
    LEFT JOIN kecelakaan kec ON g.id = kec.gampong_id
    LEFT JOIN koordinat koord ON g.id = koord.gampong_id
    WHERE kec.jumlah_kecelakaan IS NOT NULL
'''

cursor.execute(query_all)
all_data = cursor.fetchall()

print(f'\nAll data count: {len(all_data)}')
print('Sample all data years:')
years = list(set([row['tahun'] for row in all_data]))
print(f'  Available years: {sorted(years)}')

cursor.close()
conn.close()
