
-- Table for Gampong
CREATE TABLE gampong (
    id INT PRIMARY KEY,
    nama_gampong VARCHAR(255) NOT NULL
);

-- Table for Kecelakaan
CREATE TABLE kecelakaan (
    id INT PRIMARY KEY AUTO_INCREMENT,
    gampong_id INT NOT NULL,
    jumlah_kecelakaan INT,
    tahun INT,
    FOREIGN KEY (gampong_id) REFERENCES gampong(id) ON DELETE CASCADE
);

-- Table for Korban
CREATE TABLE korban (
    id INT PRIMARY KEY AUTO_INCREMENT,
    gampong_id INT NOT NULL,
    jumlah_meninggal INT,
    jumlah_luka_berat INT,
    jumlah_luka_ringan INT,
    tahun INT,
    FOREIGN KEY (gampong_id) REFERENCES gampong(id) ON DELETE CASCADE
);

-- Table for Jenis Kendaraan
CREATE TABLE jenis_kendaraan (
    id INT PRIMARY KEY AUTO_INCREMENT,
    gampong_id INT NOT NULL,
    kendaraan_roda_dua INT,
    kendaraan_roda_4 INT,
    kendaraan_lebih_roda_4 INT,
    kendaraan_lainnya INT,
    tahun INT,
    FOREIGN KEY (gampong_id) REFERENCES gampong(id) ON DELETE CASCADE
);

-- Table for Kondisi Jalan
CREATE TABLE kondisi_jalan (
    id INT PRIMARY KEY AUTO_INCREMENT,
    gampong_id INT NOT NULL,
    jalan_berlubang INT,
    jalan_jalur_dua INT,
    jalan_tikungan INT,
    jalanan_sempit INT,
    tahun INT,
    FOREIGN KEY (gampong_id) REFERENCES gampong(id) ON DELETE CASCADE
);

-- Table for Koordinat
CREATE TABLE koordinat (
    id INT PRIMARY KEY AUTO_INCREMENT,
    gampong_id INT NOT NULL,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    FOREIGN KEY (gampong_id) REFERENCES gampong(id) ON DELETE CASCADE
);
