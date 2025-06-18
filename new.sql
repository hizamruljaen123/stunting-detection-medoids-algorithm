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

-- Data exporting was unselected.

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

-- Data exporting was unselected.

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

-- Data exporting was unselected.

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

-- Data exporting was unselected.

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

-- Data exporting was unselected.

-- Dumping structure for view kecelakaan_data.total_kecelakaan
-- Creating temporary table to overcome VIEW dependency errors
CREATE TABLE `total_kecelakaan` (
	`id` BIGINT(20) UNSIGNED NOT NULL,
	`gampong_id` INT(10) NOT NULL,
	`nama_gampong` VARCHAR(255) NOT NULL COLLATE 'utf8mb4_general_ci',
	`tahun` INT(10) NULL,
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
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `total_kecelakaan` AS select row_number() OVER (ORDER BY `g`.`id`,`jk`.`tahun` )  AS `id`,`g`.`id` AS `gampong_id`,`g`.`nama_gampong` AS `nama_gampong`,`jk`.`tahun` AS `tahun`,coalesce((((`jk`.`kendaraan_roda_dua` + `jk`.`kendaraan_roda_4`) + `jk`.`kendaraan_lebih_roda_4`) + `jk`.`kendaraan_lainnya`),0) AS `jumlah_kecelakaan` from (`gampong` `g` left join `jenis_kendaraan` `jk` on((`g`.`id` = `jk`.`gampong_id`))) where ((`jk`.`tahun` is not null) and ((((`jk`.`kendaraan_roda_dua` + `jk`.`kendaraan_roda_4`) + `jk`.`kendaraan_lebih_roda_4`) + `jk`.`kendaraan_lainnya`) > 0)) order by `g`.`id`,`jk`.`tahun`;

-- Removing temporary table and create final VIEW structure
DROP TABLE IF EXISTS `total_korban`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `total_korban` AS select row_number() OVER (ORDER BY `g`.`id`,`kr`.`tahun` )  AS `id`,`g`.`id` AS `gampong_id`,`g`.`nama_gampong` AS `nama_gampong`,`kr`.`tahun` AS `tahun`,coalesce(`kr`.`jumlah_meninggal`,0) AS `jumlah_meninggal`,coalesce(`kr`.`luka_berat`,0) AS `luka_berat`,coalesce(`kr`.`luka_ringan`,0) AS `luka_ringan`,coalesce(((`kr`.`jumlah_meninggal` + `kr`.`luka_berat`) + `kr`.`luka_ringan`),0) AS `total_korban` from (`gampong` `g` left join `korban` `kr` on((`g`.`id` = `kr`.`gampong_id`))) where ((`kr`.`tahun` is not null) and (((`kr`.`jumlah_meninggal` + `kr`.`luka_berat`) + `kr`.`luka_ringan`) > 0)) order by `g`.`id`,`kr`.`tahun`;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
