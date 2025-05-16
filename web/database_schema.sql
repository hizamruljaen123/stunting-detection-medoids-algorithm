-- Database schema for Kecelakaan Lalu Lintas Kabupaten Aceh Utara
-- Created: 22 April 2025

-- Tabel untuk jenis kecelakaan
CREATE TABLE IF NOT EXISTS `jenis_kecelakaan` (
  `id` int AUTO_INCREMENT PRIMARY KEY,
  `Kecamatan` varchar(100) NOT NULL,
  `Tabrakan` int DEFAULT 0,
  `Terjatuh` int DEFAULT 0,
  `Tertabrak` int DEFAULT 0,
  `Terbalik` int DEFAULT 0,
  `Kecelakaan_Tunggal` int DEFAULT 0,
  `Kecelakaan_Beruntun` int DEFAULT 0,
  `Jumlah` int DEFAULT 0,
  `Tahun` int NOT NULL,
  INDEX `idx_kecamatan` (`Kecamatan`),
  INDEX `idx_tahun` (`Tahun`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel untuk korban berdasarkan usia
CREATE TABLE IF NOT EXISTS `korban_usia` (
  `id` int AUTO_INCREMENT PRIMARY KEY,
  `Kecamatan` varchar(100) NOT NULL,
  `anak_anak` int DEFAULT 0,
  `remaja` int DEFAULT 0,
  `dewasa` int DEFAULT 0,
  `paruh_baya` int DEFAULT 0,
  `lansia` int DEFAULT 0,
  `jumlah` int DEFAULT 0,
  `tahun` int NOT NULL,
  INDEX `idx_kecamatan` (`Kecamatan`),
  INDEX `idx_tahun` (`tahun`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel untuk koordinat kecamatan (opsional)
CREATE TABLE IF NOT EXISTS `kecamatan_coordinates` (
  `id` int AUTO_INCREMENT PRIMARY KEY,
  `Kecamatan` varchar(100) NOT NULL UNIQUE,
  `latitude` decimal(10,6) NOT NULL,
  `longitude` decimal(10,6) NOT NULL,
  INDEX `idx_kecamatan` (`Kecamatan`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contoh data awal untuk koordinat kecamatan
INSERT IGNORE INTO `kecamatan_coordinates` 
(`Kecamatan`, `latitude`, `longitude`) VALUES
('Baktiya', 5.139722, 97.451111),
('Banda Baro', 5.183333, 96.950000),
('Cot Girek', 4.866667, 97.366667),
('Dewantara', 5.216667, 97.500000),
('Geuredong Pase', 5.066667, 97.283333),
('Kuta Makmur', 5.016667, 97.383333),
('Langkahan', 5.100000, 97.316667),
('Lapang', 5.150000, 97.433333),
('Lhoksukon', 5.066667, 97.316667),
('Matangkuli', 5.033333, 97.266667),
('Meurah Mulia', 5.083333, 97.216667),
('Muara Batu', 5.233333, 96.950000),
('Nibong', 5.166667, 97.516667),
('Paya Bakong', 5.116667, 97.233333),
('Pirak Timur', 5.133333, 97.350000),
('Samudera', 5.100000, 97.233333),
('Sawang', 5.083333, 97.300000),
('Seunuddon', 5.166667, 97.450000),
('Simpang Kramat', 5.116667, 97.383333),
('Syamtalira Aron', 5.066667, 97.250000),
('Syamtalira Bayu', 5.033333, 97.216667),
('Tanah Jambo Aye', 5.133333, 97.433333),
('Tanah Luas', 5.083333, 97.333333),
('Tanah Pasir', 5.166667, 97.383333);