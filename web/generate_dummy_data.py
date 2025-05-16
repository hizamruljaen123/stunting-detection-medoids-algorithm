import random
import mysql.connector
from datetime import datetime

# Konfigurasi database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kecelakaan_data'
}

# Daftar kecamatan di Aceh Utara
kecamatan_list = [
    'Baktiya', 'Banda Baro', 'Cot Girek', 'Dewantara', 
    'Geuredong Pase', 'Kuta Makmur', 'Langkahan', 'Lapang',
    'Lhoksukon', 'Matangkuli', 'Meurah Mulia', 'Muara Batu',
    'Nibong', 'Paya Bakong', 'Pirak Timur', 'Samudera',
    'Sawang', 'Seunuddon', 'Simpang Kramat', 'Syamtalira Aron',
    'Syamtalira Bayu', 'Tanah Jambo Aye', 'Tanah Luas', 'Tanah Pasir'
]

def generate_dummy_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Generate data untuk tabel jenis_kecelakaan
    jenis_kecelakaan_data = []
    for tahun in range(2020, 2025):  # Data untuk 5 tahun terakhir
        for kecamatan in kecamatan_list:
            tabrakan = random.randint(5, 50)
            terjatuh = random.randint(2, 30)
            tertabrak = random.randint(1, 20)
            terbalik = random.randint(1, 15)
            tunggal = random.randint(3, 25)
            beruntun = random.randint(1, 10)
            total = tabrakan + terjatuh + tertabrak + terbalik + tunggal + beruntun

            jenis_kecelakaan_data.append((
                kecamatan, tabrakan, terjatuh, tertabrak, 
                terbalik, tunggal, beruntun, total, tahun
            ))

    # Insert data jenis_kecelakaan
    cursor.executemany("""
        INSERT INTO jenis_kecelakaan 
        (Kecamatan, Tabrakan, Terjatuh, Tertabrak, Terbalik, 
         Kecelakaan_Tunggal, Kecelakaan_Beruntun, Jumlah, Tahun)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, jenis_kecelakaan_data)

    # Generate data untuk tabel korban_usia
    korban_usia_data = []
    for tahun in range(2020, 2025):
        for kecamatan in kecamatan_list:
            anak = random.randint(1, 15)
            remaja = random.randint(5, 30)
            dewasa = random.randint(10, 50)
            paruh_baya = random.randint(5, 25)
            lansia = random.randint(1, 10)
            total = anak + remaja + dewasa + paruh_baya + lansia

            korban_usia_data.append((
                kecamatan, anak, remaja, dewasa, 
                paruh_baya, lansia, total, tahun
            ))

    # Insert data korban_usia
    cursor.executemany("""
        INSERT INTO korban_usia 
        (Kecamatan, anak_anak, remaja, dewasa, paruh_baya, lansia, jumlah, tahun)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, korban_usia_data)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Successfully generated dummy data for {len(kecamatan_list)} kecamatan (2020-2024)")

if __name__ == '__main__':
    generate_dummy_data()