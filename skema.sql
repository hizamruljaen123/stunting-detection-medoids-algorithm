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
  `nama_gampong` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table kecelakaan_data.jenis_kendaraan: ~60 rows (approximately)
INSERT INTO `jenis_kendaraan` (`id`, `gampong_id`, `kendaraan_roda_dua`, `kendaraan_roda_4`, `kendaraan_lebih_roda_4`, `kendaraan_lainnya`, `tahun`) VALUES
	(2, 1, 12, 7, 1, 1, 2022),
	(3, 1, 15, 3, 1, 1, 2023),
	(4, 1, 10, 3, 2, 0, 2024),
	(6, 2, 8, 3, 1, 0, 2022),
	(7, 2, 14, 4, 1, 1, 2023),
	(8, 2, 11, 5, 2, 1, 2024),
	(10, 3, 16, 5, 2, 1, 2022),
	(11, 3, 13, 4, 1, 2, 2023),
	(12, 3, 9, 2, 1, 1, 2024),
	(14, 4, 6, 2, 1, 1, 2022),
	(15, 4, 11, 3, 1, 1, 2023),
	(16, 4, 8, 2, 1, 0, 2024),
	(18, 5, 10, 3, 1, 1, 2022),
	(19, 5, 12, 2, 1, 0, 2023),
	(20, 5, 14, 3, 2, 1, 2024),
	(22, 6, 18, 4, 2, 1, 2022),
	(23, 6, 9, 2, 1, 0, 2023),
	(24, 6, 13, 3, 1, 1, 2024),
	(26, 7, 20, 5, 3, 2, 2022),
	(27, 7, 8, 1, 1, 0, 2023),
	(28, 7, 22, 4, 2, 2, 2024),
	(30, 8, 11, 3, 1, 1, 2022),
	(31, 8, 13, 2, 2, 1, 2023),
	(32, 8, 10, 3, 1, 1, 2024),
	(34, 9, 7, 2, 1, 0, 2022),
	(35, 9, 9, 2, 1, 0, 2023),
	(36, 9, 8, 2, 1, 1, 2024),
	(38, 10, 19, 4, 2, 1, 2022),
	(39, 10, 12, 3, 1, 1, 2023),
	(40, 10, 8, 2, 1, 0, 2024),
	(42, 11, 14, 3, 2, 1, 2022),
	(43, 11, 12, 2, 1, 1, 2023),
	(44, 11, 13, 3, 1, 1, 2024),
	(46, 12, 17, 4, 2, 1, 2022),
	(47, 12, 10, 2, 1, 0, 2023),
	(48, 12, 6, 1, 1, 0, 2024),
	(50, 13, 15, 3, 1, 1, 2022),
	(51, 13, 14, 2, 1, 1, 2023),
	(52, 13, 16, 3, 2, 1, 2024),
	(54, 14, 13, 3, 1, 1, 2022),
	(55, 14, 8, 1, 1, 0, 2023),
	(56, 14, 12, 2, 1, 1, 2024),
	(58, 15, 11, 2, 1, 1, 2022),
	(59, 15, 14, 3, 1, 1, 2023),
	(60, 15, 12, 3, 1, 1, 2024),
	(62, 16, 9, 2, 1, 0, 2022),
	(63, 16, 11, 2, 1, 1, 2023),
	(64, 16, 13, 3, 1, 1, 2024),
	(66, 17, 12, 2, 2, 0, 2022),
	(67, 17, 7, 1, 1, 0, 2023),
	(68, 17, 14, 3, 1, 1, 2024),
	(70, 18, 10, 2, 1, 1, 2022),
	(71, 18, 13, 3, 1, 1, 2023),
	(72, 18, 11, 2, 1, 1, 2024),
	(74, 19, 6, 1, 1, 0, 2022),
	(75, 19, 9, 2, 1, 0, 2023),
	(76, 19, 8, 1, 1, 1, 2024),
	(78, 20, 11, 3, 1, 1, 2022),
	(79, 20, 7, 1, 1, 0, 2023),
	(80, 20, 10, 2, 1, 1, 2024);

-- Dumping structure for view kecelakaan_data.kecelakaan
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `kecelakaan` (
	`id` BIGINT(20) UNSIGNED NOT NULL,
	`gampong_id` INT(10) NOT NULL,
	`tahun` BIGINT(19) NULL,
	`jumlah_kecelakaan` BIGINT(19) NOT NULL
) ENGINE=MyISAM;

-- Dumping structure for table kecelakaan_data.kondisi_jalan
CREATE TABLE IF NOT EXISTS `kondisi_jalan` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gampong_id` int NOT NULL,
  `jalan_berlubang` int DEFAULT NULL,
  `jalan_jalur_dua` int DEFAULT NULL,
  `tahun` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gampong_id` (`gampong_id`),
  CONSTRAINT `kondisi_jalan_ibfk_1` FOREIGN KEY (`gampong_id`) REFERENCES `gampong` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table kecelakaan_data.kondisi_jalan: ~60 rows (approximately)
INSERT INTO `kondisi_jalan` (`id`, `gampong_id`, `jalan_berlubang`, `jalan_jalur_dua`, `tahun`) VALUES
	(2, 1, 3, 5, 2022),
	(3, 1, 4, 6, 2023),
	(4, 1, 2, 4, 2024),
	(6, 2, 2, 3, 2022),
	(7, 2, 3, 4, 2023),
	(8, 2, 3, 5, 2024),
	(10, 3, 5, 7, 2022),
	(11, 3, 4, 6, 2023),
	(12, 3, 2, 3, 2024),
	(14, 4, 1, 2, 2022),
	(15, 4, 3, 4, 2023),
	(16, 4, 2, 3, 2024),
	(18, 5, 3, 4, 2022),
	(19, 5, 2, 3, 2023),
	(20, 5, 4, 5, 2024),
	(22, 6, 6, 8, 2022),
	(23, 6, 2, 3, 2023),
	(24, 6, 4, 5, 2024),
	(26, 7, 7, 9, 2022),
	(27, 7, 1, 2, 2023),
	(28, 7, 8, 10, 2024),
	(30, 8, 3, 4, 2022),
	(31, 8, 4, 5, 2023),
	(32, 8, 3, 4, 2024),
	(34, 9, 2, 3, 2022),
	(35, 9, 2, 3, 2023),
	(36, 9, 3, 4, 2024),
	(38, 10, 6, 8, 2022),
	(39, 10, 4, 5, 2023),
	(40, 10, 2, 3, 2024),
	(42, 11, 5, 6, 2022),
	(43, 11, 3, 4, 2023),
	(44, 11, 4, 5, 2024),
	(46, 12, 6, 7, 2022),
	(47, 12, 3, 4, 2023),
	(48, 12, 1, 2, 2024),
	(50, 13, 5, 6, 2022),
	(51, 13, 4, 5, 2023),
	(52, 13, 5, 7, 2024),
	(54, 14, 4, 5, 2022),
	(55, 14, 2, 3, 2023),
	(56, 14, 3, 4, 2024),
	(58, 15, 3, 4, 2022),
	(59, 15, 4, 6, 2023),
	(60, 15, 4, 5, 2024),
	(62, 16, 2, 3, 2022),
	(63, 16, 3, 4, 2023),
	(64, 16, 4, 5, 2024),
	(66, 17, 3, 4, 2022),
	(67, 17, 1, 2, 2023),
	(68, 17, 4, 6, 2024),
	(70, 18, 3, 4, 2022),
	(71, 18, 4, 5, 2023),
	(72, 18, 3, 4, 2024),
	(74, 19, 1, 2, 2022),
	(75, 19, 2, 3, 2023),
	(76, 19, 2, 3, 2024),
	(78, 20, 3, 4, 2022),
	(79, 20, 1, 2, 2023),
	(80, 20, 3, 4, 2024);

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
	(1, 1, 5.22359300, 97.04638400),
	(2, 2, 5.24600000, 97.02500000),
	(3, 3, 5.20823900, 97.06926600),
	(4, 4, 5.20446500, 97.08631100),
	(5, 5, 5.20310100, 97.11026300),
	(6, 6, 5.18975500, 97.11826500),
	(7, 7, 5.17356700, 97.13144800),
	(8, 8, 5.15163700, 97.13518700),
	(9, 9, 5.12968000, 97.15372200),
	(10, 10, 5.17497800, 97.11558300),
	(11, 11, 5.17913300, 97.13754000),
	(12, 12, 5.18555400, 97.13364600),
	(13, 13, 5.18711900, 97.14385000),
	(14, 14, 5.16944600, 97.12875000),
	(15, 15, 5.18330000, 97.14170000),
	(16, 16, 5.18014200, 97.14203100),
	(17, 17, 5.17668500, 97.14354000),
	(18, 18, 5.18843800, 97.13191600),
	(19, 19, 5.19455700, 97.12819400),
	(20, 20, 5.20723200, 97.12262600);

-- Dumping structure for table kecelakaan_data.korban
CREATE TABLE IF NOT EXISTS `korban` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gampong_id` int NOT NULL,
  `jumlah_meninggal` int DEFAULT NULL,
  `tahun` int DEFAULT NULL,
  `luka_berat` int DEFAULT NULL,
  `luka_ringan` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gampong_id` (`gampong_id`),
  CONSTRAINT `korban_ibfk_1` FOREIGN KEY (`gampong_id`) REFERENCES `gampong` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Dumping data for table kecelakaan_data.korban: ~60 rows (approximately)
INSERT INTO `korban` (`id`, `gampong_id`, `jumlah_meninggal`, `tahun`, `luka_berat`, `luka_ringan`) VALUES
	(2, 1, 2, 2022, 1, 1),
	(3, 1, 1, 2023, 5, 14),
	(4, 1, 2, 2024, 3, 10),
	(6, 2, 1, 2022, 3, 8),
	(7, 2, 2, 2023, 4, 14),
	(8, 2, 1, 2024, 5, 13),
	(10, 3, 3, 2022, 6, 15),
	(11, 3, 2, 2023, 5, 13),
	(12, 3, 1, 2024, 3, 9),
	(14, 4, 1, 2022, 2, 7),
	(15, 4, 2, 2023, 3, 11),
	(16, 4, 1, 2024, 2, 8),
	(18, 5, 2, 2022, 3, 10),
	(19, 5, 1, 2023, 4, 10),
	(20, 5, 3, 2024, 4, 13),
	(22, 6, 3, 2022, 6, 16),
	(23, 6, 1, 2023, 3, 8),
	(24, 6, 2, 2024, 4, 12),
	(26, 7, 4, 2022, 7, 19),
	(27, 7, 1, 2023, 2, 7),
	(28, 7, 5, 2024, 6, 19),
	(30, 8, 2, 2022, 4, 10),
	(31, 8, 2, 2023, 3, 13),
	(32, 8, 1, 2024, 3, 11),
	(34, 9, 1, 2022, 2, 7),
	(35, 9, 1, 2023, 3, 8),
	(36, 9, 1, 2024, 2, 9),
	(38, 10, 4, 2022, 6, 16),
	(39, 10, 2, 2023, 4, 11),
	(40, 10, 1, 2024, 2, 8),
	(42, 11, 3, 2022, 5, 12),
	(43, 11, 2, 2023, 3, 11),
	(44, 11, 2, 2024, 4, 12),
	(46, 12, 3, 2022, 6, 15),
	(47, 12, 1, 2023, 3, 9),
	(48, 12, 1, 2024, 2, 5),
	(50, 13, 3, 2022, 4, 13),
	(51, 13, 2, 2023, 4, 12),
	(52, 13, 3, 2024, 5, 14),
	(54, 14, 2, 2022, 4, 12),
	(55, 14, 1, 2023, 2, 7),
	(56, 14, 2, 2024, 3, 11),
	(58, 15, 2, 2022, 3, 10),
	(59, 15, 2, 2023, 4, 13),
	(60, 15, 2, 2024, 3, 12),
	(62, 16, 1, 2022, 3, 8),
	(63, 16, 2, 2023, 3, 10),
	(64, 16, 2, 2024, 4, 12),
	(66, 17, 2, 2022, 4, 10),
	(67, 17, 1, 2023, 2, 6),
	(68, 17, 3, 2024, 4, 12),
	(70, 18, 2, 2022, 3, 9),
	(71, 18, 2, 2023, 4, 12),
	(72, 18, 2, 2024, 3, 10),
	(74, 19, 1, 2022, 2, 5),
	(75, 19, 1, 2023, 3, 8),
	(76, 19, 1, 2024, 2, 8),
	(78, 20, 2, 2022, 4, 10),
	(79, 20, 1, 2023, 2, 6),
	(80, 20, 2, 2024, 3, 9);

-- Dumping structure for view kecelakaan_data.total_kecelakaan
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `total_kecelakaan` (
	`id` BIGINT(20) UNSIGNED NOT NULL,
	`gampong_id` INT(10) NOT NULL,
	`nama_gampong` VARCHAR(255) NOT NULL COLLATE 'utf8mb4_general_ci',
	`tahun` BIGINT(19) NULL,
	`jumlah_kecelakaan` BIGINT(19) NOT NULL
) ENGINE=MyISAM;

-- Dumping structure for view kecelakaan_data.total_korban
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `total_korban` (
	`id` BIGINT(20) UNSIGNED NOT NULL,
	`gampong_id` INT(10) NOT NULL,
	`nama_gampong` VARCHAR(255) NOT NULL COLLATE 'utf8mb4_general_ci',
	`tahun` INT(10) NULL,
	`jumlah_meninggal` BIGINT(19) NOT NULL,
	`luka_berat` BIGINT(19) NOT NULL,
	`luka_ringan` BIGINT(19) NOT NULL,
	`total_korban` BIGINT(19) NOT NULL
) ENGINE=MyISAM;

-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `kecelakaan`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `kecelakaan` AS select row_number() OVER (ORDER BY `g`.`id`,coalesce(`kr`.`tahun`,`jk`.`tahun`) )  AS `id`,`g`.`id` AS `gampong_id`,coalesce(`kr`.`tahun`,`jk`.`tahun`) AS `tahun`,least(coalesce((((`jk`.`kendaraan_roda_dua` + `jk`.`kendaraan_roda_4`) + `jk`.`kendaraan_lebih_roda_4`) + `jk`.`kendaraan_lainnya`),0),coalesce(((`kr`.`jumlah_meninggal` + `kr`.`luka_berat`) + `kr`.`luka_ringan`),0)) AS `jumlah_kecelakaan` from ((`gampong` `g` left join `korban` `kr` on((`g`.`id` = `kr`.`gampong_id`))) left join `jenis_kendaraan` `jk` on(((`g`.`id` = `jk`.`gampong_id`) and (`kr`.`tahun` = `jk`.`tahun`)))) where ((`kr`.`tahun` is not null) and (`jk`.`tahun` is not null) and (((((`jk`.`kendaraan_roda_dua` + `jk`.`kendaraan_roda_4`) + `jk`.`kendaraan_lebih_roda_4`) + `jk`.`kendaraan_lainnya`) > 0) or (((`kr`.`jumlah_meninggal` + `kr`.`luka_berat`) + `kr`.`luka_ringan`) > 0))) order by `g`.`id`,coalesce(`kr`.`tahun`,`jk`.`tahun`);

-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `total_kecelakaan`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `total_kecelakaan` AS select row_number() OVER (ORDER BY `g`.`id`,coalesce(`kj`.`tahun`,`kjd`.`tahun`) )  AS `id`,`g`.`id` AS `gampong_id`,`g`.`nama_gampong` AS `nama_gampong`,coalesce(`kj`.`tahun`,`kjd`.`tahun`) AS `tahun`,(((((coalesce(`kj`.`jalan_berlubang`,0) + coalesce(`kj`.`jalan_jalur_dua`,0)) + coalesce(`kjd`.`kendaraan_roda_dua`,0)) + coalesce(`kjd`.`kendaraan_roda_4`,0)) + coalesce(`kjd`.`kendaraan_lebih_roda_4`,0)) + coalesce(`kjd`.`kendaraan_lainnya`,0)) AS `jumlah_kecelakaan` from ((`gampong` `g` left join `kondisi_jalan` `kj` on((`g`.`id` = `kj`.`gampong_id`))) left join `jenis_kendaraan` `kjd` on(((`g`.`id` = `kjd`.`gampong_id`) and (`kj`.`tahun` = `kjd`.`tahun`)))) where (((`kj`.`tahun` is not null) or (`kjd`.`tahun` is not null)) and ((((((coalesce(`kj`.`jalan_berlubang`,0) + coalesce(`kj`.`jalan_jalur_dua`,0)) + coalesce(`kjd`.`kendaraan_roda_dua`,0)) + coalesce(`kjd`.`kendaraan_roda_4`,0)) + coalesce(`kjd`.`kendaraan_lebih_roda_4`,0)) + coalesce(`kjd`.`kendaraan_lainnya`,0)) > 0)) order by `g`.`id`,coalesce(`kj`.`tahun`,`kjd`.`tahun`);

-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `total_korban`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `total_korban` AS select row_number() OVER (ORDER BY `g`.`id`,`kr`.`tahun` )  AS `id`,`g`.`id` AS `gampong_id`,`g`.`nama_gampong` AS `nama_gampong`,`kr`.`tahun` AS `tahun`,coalesce(`kr`.`jumlah_meninggal`,0) AS `jumlah_meninggal`,coalesce(`kr`.`luka_berat`,0) AS `luka_berat`,coalesce(`kr`.`luka_ringan`,0) AS `luka_ringan`,coalesce(((`kr`.`jumlah_meninggal` + `kr`.`luka_berat`) + `kr`.`luka_ringan`),0) AS `total_korban` from (`gampong` `g` left join `korban` `kr` on((`g`.`id` = `kr`.`gampong_id`))) where ((`kr`.`tahun` is not null) and (((`kr`.`jumlah_meninggal` + `kr`.`luka_berat`) + `kr`.`luka_ringan`) > 0)) order by `g`.`id`,`kr`.`tahun`;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
