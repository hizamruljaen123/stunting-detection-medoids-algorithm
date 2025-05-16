
-- Dummy data for Gampong
INSERT INTO gampong (id, nama_gampong) VALUES (1, 'Batuphat');
INSERT INTO gampong (id, nama_gampong) VALUES (2, 'Krueng Geukuh');
INSERT INTO gampong (id, nama_gampong) VALUES (3, 'Blang Pulo');
INSERT INTO gampong (id, nama_gampong) VALUES (4, 'Meuria Paloh');
INSERT INTO gampong (id, nama_gampong) VALUES (5, 'Blang Panyang');
INSERT INTO gampong (id, nama_gampong) VALUES (6, 'Panggoi');
INSERT INTO gampong (id, nama_gampong) VALUES (7, 'Cunda');
INSERT INTO gampong (id, nama_gampong) VALUES (8, 'Kandang');
INSERT INTO gampong (id, nama_gampong) VALUES (9, 'Alue Awe');
INSERT INTO gampong (id, nama_gampong) VALUES (10, 'Puentet');
INSERT INTO gampong (id, nama_gampong) VALUES (11, 'Mongedong');
INSERT INTO gampong (id, nama_gampong) VALUES (12, 'Kutablang');
INSERT INTO gampong (id, nama_gampong) VALUES (13, 'Darussalam');
INSERT INTO gampong (id, nama_gampong) VALUES (14, 'Meunasah Kota');
INSERT INTO gampong (id, nama_gampong) VALUES (15, 'Lancang Garam');
INSERT INTO gampong (id, nama_gampong) VALUES (16, 'Simpang Empat');
INSERT INTO gampong (id, nama_gampong) VALUES (17, 'Keude Aceh');
INSERT INTO gampong (id, nama_gampong) VALUES (18, 'Uteun Bayi');
INSERT INTO gampong (id, nama_gampong) VALUES (19, 'Banda Masen');
INSERT INTO gampong (id, nama_gampong) VALUES (20, 'Ujong Blang');


-- Dummy data for Kecelakaan
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (1, 13, 2023);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (2, 6, 2024);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (3, 13, 2023);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (4, 3, 2022);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (5, 7, 2023);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (6, 1, 2022);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (7, 15, 2021);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (8, 11, 2020);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (9, 2, 2020);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (10, 13, 2020);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (11, 4, 2024);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (12, 6, 2021);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (13, 12, 2022);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (14, 12, 2020);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (15, 9, 2022);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (16, 6, 2020);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (17, 15, 2023);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (18, 10, 2021);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (19, 15, 2023);
INSERT INTO kecelakaan (gampong_id, jumlah_kecelakaan, tahun) VALUES (20, 3, 2020);


-- Dummy data for Korban
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (1, 4, 3, 9, 2021);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (2, 5, 10, 18, 2021);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (3, 4, 7, 5, 2023);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (4, 1, 7, 10, 2020);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (5, 2, 3, 6, 2022);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (6, 5, 8, 6, 2020);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (7, 4, 4, 12, 2021);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (8, 1, 8, 5, 2024);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (9, 0, 7, 12, 2023);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (10, 1, 9, 5, 2023);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (11, 3, 1, 17, 2024);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (12, 1, 8, 8, 2021);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (13, 1, 9, 19, 2022);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (14, 2, 4, 7, 2022);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (15, 3, 9, 9, 2020);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (16, 5, 5, 14, 2020);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (17, 5, 3, 11, 2021);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (18, 0, 1, 17, 2020);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (19, 1, 1, 10, 2020);
INSERT INTO korban (gampong_id, jumlah_meninggal, jumlah_luka_berat, jumlah_luka_ringan, tahun) VALUES (20, 3, 7, 11, 2024);


-- Dummy data for Jenis Kendaraan
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (1, 39, 17, 6, 1, 2021);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (2, 17, 9, 3, 2, 2021);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (3, 16, 6, 5, 0, 2022);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (4, 17, 12, 7, 4, 2022);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (5, 10, 5, 5, 0, 2024);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (6, 18, 10, 9, 0, 2024);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (7, 18, 19, 3, 3, 2022);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (8, 39, 15, 6, 3, 2021);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (9, 12, 6, 3, 3, 2023);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (10, 23, 5, 9, 3, 2024);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (11, 11, 10, 5, 4, 2024);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (12, 21, 16, 7, 4, 2021);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (13, 40, 6, 8, 2, 2022);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (14, 39, 9, 8, 2, 2022);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (15, 20, 11, 10, 2, 2022);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (16, 24, 15, 1, 3, 2021);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (17, 39, 8, 9, 3, 2022);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (18, 10, 15, 2, 5, 2024);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (19, 30, 11, 6, 5, 2022);
INSERT INTO jenis_kendaraan (gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun) VALUES (20, 38, 5, 3, 3, 2024);


-- Dummy data for Kondisi Jalan
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (1, 1, 0, 2, 4, 2023);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (2, 2, 1, 3, 5, 2023);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (3, 5, 0, 4, 4, 2024);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (4, 2, 2, 4, 4, 2020);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (5, 1, 0, 1, 1, 2023);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (6, 1, 2, 4, 4, 2023);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (7, 1, 1, 3, 5, 2021);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (8, 5, 3, 3, 5, 2022);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (9, 3, 1, 2, 2, 2021);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (10, 4, 0, 2, 3, 2020);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (11, 2, 0, 4, 2, 2021);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (12, 5, 0, 3, 5, 2024);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (13, 3, 0, 3, 3, 2020);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (14, 2, 1, 4, 2, 2020);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (15, 1, 2, 3, 2, 2023);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (16, 2, 1, 2, 2, 2024);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (17, 4, 3, 4, 2, 2020);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (18, 4, 1, 3, 3, 2024);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (19, 1, 3, 1, 1, 2023);
INSERT INTO kondisi_jalan (gampong_id, jalan_berlubang, jalan_jalur_dua, jalan_tikungan, jalanan_sempit, tahun) VALUES (20, 2, 2, 1, 4, 2021);


-- Dummy data for Koordinat
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (1, 4.52395423, 96.90143505);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (2, 4.80191436, 95.77418061);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (3, 4.72570175, 95.8290459);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (4, 5.30996836, 96.8174127);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (5, 5.27855872, 95.14487895);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (6, 4.90151345, 95.04134523);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (7, 5.43179124, 95.35371672);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (8, 4.85745915, 96.27296605);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (9, 4.9577579, 96.31303034);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (10, 5.45046717, 96.15226314);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (11, 5.1743098, 95.83667471);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (12, 4.71694168, 96.26722317);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (13, 4.97682913, 96.37661381);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (14, 5.08125577, 95.6530266);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (15, 5.1693461, 96.14782474);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (16, 5.10973874, 96.29057419);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (17, 4.82525673, 96.3438315);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (18, 4.58985375, 95.16488025);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (19, 5.28227546, 96.0590562);
INSERT INTO koordinat (gampong_id, latitude, longitude) VALUES (20, 4.52753082, 95.39643256);
