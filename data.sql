-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.0.30 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             12.6.0.6765
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping structure for table kecelakaan_data.gampong
CREATE TABLE IF NOT EXISTS `gampong` (
  `id` int NOT NULL,
  `nama_gampong` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table kecelakaan_data.gampong: ~20 rows (approximately)
INSERT INTO `gampong` (`id`, `nama_gampong`) VALUES
	(1, 'Batuphat'),
	(2, 'Krueng Geukuh'),
	(3, 'Blang Pulo'),
	(4, 'Meuria Paloh'),
	(5, 'Blang Panyang'),
	(6, 'Panggoi'),
	(7, 'Cunda'),
	(8, 'Kandang'),
	(9, 'Alue Awe'),
	(10, 'Puentet'),
	(11, 'Mongedong'),
	(12, 'Kutablang'),
	(13, 'Darussalam'),
	(14, 'Meunasah Kota'),
	(15, 'Lancang Garam'),
	(16, 'Simpang Empat'),
	(17, 'Keude Aceh'),
	(18, 'Uteun Bayi'),
	(19, 'Banda Masen'),
	(20, 'Ujong Blang');

-- Dumping structure for table kecelakaan_data.jenis_kendaraan
CREATE TABLE IF NOT EXISTS `jenis_kendaraan` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gampong_id` int NOT NULL,
  `kendaraan_roda_dua` int DEFAULT NULL,
  `kendaraan_roda_4` int DEFAULT NULL,
  `kendaraan_lebih_roda_4` int DEFAULT NULL,
  `kendaraan_lainnya` int DEFAULT NULL,
  `tahun` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gampong_id` (`gampong_id`),
  CONSTRAINT `jenis_kendaraan_ibfk_1` FOREIGN KEY (`gampong_id`) REFERENCES `gampong` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table kecelakaan_data.jenis_kendaraan: ~20 rows (approximately)
INSERT INTO `jenis_kendaraan` (`id`, `gampong_id`, `kendaraan_roda_dua`, `kendaraan_roda_4`, `kendaraan_lebih_roda_4`, `kendaraan_lainnya`, `tahun`) VALUES
	(1, 1, 39, 17, 6, 1, 2021),
	(2, 2, 17, 9, 3, 2, 2021),
	(3, 3, 16, 6, 5, 0, 2022),
	(4, 4, 17, 12, 7, 4, 2022),
	(5, 5, 10, 5, 5, 0, 2024),
	(6, 6, 18, 10, 9, 0, 2024),
	(7, 7, 18, 19, 3, 3, 2022),
	(8, 8, 39, 15, 6, 3, 2021),
	(9, 9, 12, 6, 3, 3, 2023),
	(10, 10, 23, 5, 9, 3, 2024),
	(11, 11, 11, 10, 5, 4, 2024),
	(12, 12, 21, 16, 7, 4, 2021),
	(13, 13, 40, 6, 8, 2, 2022),
	(14, 14, 39, 9, 8, 2, 2022),
	(15, 15, 20, 11, 10, 2, 2022),
	(16, 16, 24, 15, 1, 3, 2021),
	(17, 17, 39, 8, 9, 3, 2022),
	(18, 18, 10, 15, 2, 5, 2024),
	(19, 19, 30, 11, 6, 5, 2022),
	(20, 20, 38, 5, 3, 3, 2024);

-- Dumping structure for table kecelakaan_data.kecelakaan
CREATE TABLE IF NOT EXISTS `kecelakaan` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gampong_id` int NOT NULL,
  `jumlah_kecelakaan` int DEFAULT NULL,
  `tahun` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gampong_id` (`gampong_id`),
  CONSTRAINT `kecelakaan_ibfk_1` FOREIGN KEY (`gampong_id`) REFERENCES `gampong` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table kecelakaan_data.kecelakaan: ~20 rows (approximately)
INSERT INTO `kecelakaan` (`id`, `gampong_id`, `jumlah_kecelakaan`, `tahun`) VALUES
	(1, 1, 13, 2023),
	(2, 2, 6, 2024),
	(3, 3, 13, 2023),
	(4, 4, 3, 2022),
	(5, 5, 7, 2023),
	(6, 6, 1, 2022),
	(7, 7, 15, 2021),
	(8, 8, 11, 2020),
	(9, 9, 2, 2020),
	(10, 10, 13, 2020),
	(11, 11, 4, 2024),
	(12, 12, 6, 2021),
	(13, 13, 12, 2022),
	(14, 14, 12, 2020),
	(15, 15, 9, 2022),
	(16, 16, 6, 2020),
	(17, 17, 15, 2023),
	(18, 18, 10, 2021),
	(19, 19, 15, 2023),
	(20, 20, 3, 2020);

-- Dumping structure for table kecelakaan_data.kondisi_jalan
CREATE TABLE IF NOT EXISTS `kondisi_jalan` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gampong_id` int NOT NULL,
  `jalan_berlubang` int DEFAULT NULL,
  `jalan_jalur_dua` int DEFAULT NULL,
  `jalan_tikungan` int DEFAULT NULL,
  `jalanan_sempit` int DEFAULT NULL,
  `tahun` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gampong_id` (`gampong_id`),
  CONSTRAINT `kondisi_jalan_ibfk_1` FOREIGN KEY (`gampong_id`) REFERENCES `gampong` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table kecelakaan_data.kondisi_jalan: ~20 rows (approximately)
INSERT INTO `kondisi_jalan` (`id`, `gampong_id`, `jalan_berlubang`, `jalan_jalur_dua`, `jalan_tikungan`, `jalanan_sempit`, `tahun`) VALUES
	(1, 1, 1, 0, 2, 4, 2023),
	(2, 2, 2, 1, 3, 5, 2023),
	(3, 3, 5, 0, 4, 4, 2024),
	(4, 4, 2, 2, 4, 4, 2020),
	(5, 5, 1, 0, 1, 1, 2023),
	(6, 6, 1, 2, 4, 4, 2023),
	(7, 7, 1, 1, 3, 5, 2021),
	(8, 8, 5, 3, 3, 5, 2022),
	(9, 9, 3, 1, 2, 2, 2021),
	(10, 10, 4, 0, 2, 3, 2020),
	(11, 11, 2, 0, 4, 2, 2021),
	(12, 12, 5, 0, 3, 5, 2024),
	(13, 13, 3, 0, 3, 3, 2020),
	(14, 14, 2, 1, 4, 2, 2020),
	(15, 15, 1, 2, 3, 2, 2023),
	(16, 16, 2, 1, 2, 2, 2024),
	(17, 17, 4, 3, 4, 2, 2020),
	(18, 18, 4, 1, 3, 3, 2024),
	(19, 19, 1, 3, 1, 1, 2023),
	(20, 20, 2, 2, 1, 4, 2021);

-- Dumping structure for table kecelakaan_data.koordinat
CREATE TABLE IF NOT EXISTS `koordinat` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gampong_id` int NOT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gampong_id` (`gampong_id`),
  CONSTRAINT `koordinat_ibfk_1` FOREIGN KEY (`gampong_id`) REFERENCES `gampong` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table kecelakaan_data.koordinat: ~20 rows (approximately)
INSERT INTO `koordinat` (`id`, `gampong_id`, `latitude`, `longitude`) VALUES
	(1, 1, 4.52395423, 96.90143505),
	(2, 2, 4.80191436, 95.77418061),
	(3, 3, 4.72570175, 95.82904590),
	(4, 4, 5.30996836, 96.81741270),
	(5, 5, 5.27855872, 95.14487895),
	(6, 6, 4.90151345, 95.04134523),
	(7, 7, 5.43179124, 95.35371672),
	(8, 8, 4.85745915, 96.27296605),
	(9, 9, 4.95775790, 96.31303034),
	(10, 10, 5.45046717, 96.15226314),
	(11, 11, 5.17430980, 95.83667471),
	(12, 12, 4.71694168, 96.26722317),
	(13, 13, 4.97682913, 96.37661381),
	(14, 14, 5.08125577, 95.65302660),
	(15, 15, 5.16934610, 96.14782474),
	(16, 16, 5.10973874, 96.29057419),
	(17, 17, 4.82525673, 96.34383150),
	(18, 18, 4.58985375, 95.16488025),
	(19, 19, 5.28227546, 96.05905620),
	(20, 20, 4.52753082, 95.39643256);

-- Dumping structure for table kecelakaan_data.korban
CREATE TABLE IF NOT EXISTS `korban` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gampong_id` int NOT NULL,
  `jumlah_meninggal` int DEFAULT NULL,
  `jumlah_luka_berat` int DEFAULT NULL,
  `jumlah_luka_ringan` int DEFAULT NULL,
  `tahun` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gampong_id` (`gampong_id`),
  CONSTRAINT `korban_ibfk_1` FOREIGN KEY (`gampong_id`) REFERENCES `gampong` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table kecelakaan_data.korban: ~20 rows (approximately)
INSERT INTO `korban` (`id`, `gampong_id`, `jumlah_meninggal`, `jumlah_luka_berat`, `jumlah_luka_ringan`, `tahun`) VALUES
	(1, 1, 4, 3, 9, 2021),
	(2, 2, 5, 10, 18, 2021),
	(3, 3, 4, 7, 5, 2023),
	(4, 4, 1, 7, 10, 2020),
	(5, 5, 2, 3, 6, 2022),
	(6, 6, 5, 8, 6, 2020),
	(7, 7, 4, 4, 12, 2021),
	(8, 8, 1, 8, 5, 2024),
	(9, 9, 0, 7, 12, 2023),
	(10, 10, 1, 9, 5, 2023),
	(11, 11, 3, 1, 17, 2024),
	(12, 12, 1, 8, 8, 2021),
	(13, 13, 1, 9, 19, 2022),
	(14, 14, 2, 4, 7, 2022),
	(15, 15, 3, 9, 9, 2020),
	(16, 16, 5, 5, 14, 2020),
	(17, 17, 5, 3, 11, 2021),
	(18, 18, 0, 1, 17, 2020),
	(19, 19, 1, 1, 10, 2020),
	(20, 20, 3, 7, 11, 2024);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
