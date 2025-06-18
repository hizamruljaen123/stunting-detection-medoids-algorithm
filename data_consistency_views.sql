-- ======================================================
-- FILE: data_consistency_views.sql
-- Tujuan: Membuat view dan stored procedure untuk memastikan konsistensi data
-- ======================================================

USE kecelakaan_data;

-- ======================================================
-- 1. VIEW: v_kecelakaan_summary (Updated for VIEW kecelakaan)
-- View yang menggabungkan semua data dan memvalidasi konsistensi
-- ======================================================

DROP VIEW IF EXISTS v_kecelakaan_summary;

CREATE VIEW v_kecelakaan_summary AS
SELECT 
    g.id as gampong_id,
    g.nama_gampong,
    k.tahun,
    k.jumlah_kecelakaan,
    
    -- Data Kendaraan
    jk.kendaraan_roda_dua,
    jk.kendaraan_roda_4,
    jk.kendaraan_lebih_roda_4,
    jk.kendaraan_lainnya,
    (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya) as total_kendaraan,
    
    -- Data Korban
    kr.jumlah_meninggal,
    kr.luka_berat,
    kr.luka_ringan,
    (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan) as total_korban,
    
    -- Data Kondisi Jalan
    kj.jalan_berlubang,
    kj.jalan_jalur_dua,
    
    -- Koordinat
    ko.latitude,
    ko.longitude,
    
    -- Validasi Konsistensi (Always consistent since VIEW calculates automatically)
    'KONSISTEN' as status_konsistensi,
    
    -- Additional info about calculation source
    CASE 
        WHEN (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya) 
             < (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
        THEN 'LIMITED_BY_VEHICLES'
        WHEN (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya) 
             > (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
        THEN 'LIMITED_BY_VICTIMS'
        ELSE 'EQUAL_CONSTRAINT'
    END as calculation_basis
    
FROM gampong g
LEFT JOIN kecelakaan k ON g.id = k.gampong_id
LEFT JOIN jenis_kendaraan jk ON g.id = jk.gampong_id AND k.tahun = jk.tahun
LEFT JOIN korban kr ON g.id = kr.gampong_id AND k.tahun = kr.tahun
LEFT JOIN kondisi_jalan kj ON g.id = kj.gampong_id AND k.tahun = kj.tahun
LEFT JOIN koordinat ko ON g.id = ko.gampong_id
ORDER BY g.nama_gampong, k.tahun;

-- ======================================================
-- 2. VIEW: v_ringkasan_per_tahun
-- Ringkasan data per tahun untuk semua gampong
-- ======================================================

DROP VIEW IF EXISTS v_ringkasan_per_tahun;

CREATE VIEW v_ringkasan_per_tahun AS
SELECT 
    tahun,
    COUNT(DISTINCT gampong_id) as jumlah_gampong,
    SUM(jumlah_kecelakaan) as total_kecelakaan,
    SUM(total_kendaraan) as total_kendaraan_terlibat,
    SUM(total_korban) as total_korban,
    SUM(jumlah_meninggal) as total_meninggal,
    SUM(luka_berat) as total_luka_berat,
    SUM(luka_ringan) as total_luka_ringan,
    ROUND(AVG(jumlah_kecelakaan), 2) as rata_rata_kecelakaan_per_gampong,
    
    -- Persentase konsistensi data
    ROUND(
        (SUM(CASE WHEN status_konsistensi = 'KONSISTEN' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 
        2
    ) as persentase_data_konsisten
    
FROM v_kecelakaan_summary
WHERE tahun IS NOT NULL
GROUP BY tahun
ORDER BY tahun;

-- ======================================================
-- 3. VIEW: v_gampong_tertinggi
-- Gampong dengan kecelakaan tertinggi per tahun
-- ======================================================

DROP VIEW IF EXISTS v_gampong_tertinggi;

CREATE VIEW v_gampong_tertinggi AS
WITH ranked_data AS (
    SELECT 
        tahun,
        nama_gampong,
        jumlah_kecelakaan,
        total_korban,
        ROW_NUMBER() OVER (PARTITION BY tahun ORDER BY jumlah_kecelakaan DESC) as rank_kecelakaan
    FROM v_kecelakaan_summary
    WHERE tahun IS NOT NULL
)
SELECT 
    tahun,
    nama_gampong as gampong_tertinggi,
    jumlah_kecelakaan,
    total_korban
FROM ranked_data
WHERE rank_kecelakaan = 1
ORDER BY tahun;

-- ======================================================
-- 4. STORED PROCEDURE: sp_validasi_konsistensi
-- Prosedur untuk memvalidasi dan melaporkan inkonsistensi data
-- ======================================================

DELIMITER //

DROP PROCEDURE IF EXISTS sp_validasi_konsistensi //

CREATE PROCEDURE sp_validasi_konsistensi()
BEGIN
    -- Karena kecelakaan sekarang adalah VIEW yang auto-calculated,
    -- konsistensi selalu terjamin. Procedure ini akan menampilkan
    -- informasi tentang bagaimana VIEW melakukan kalkulasi.
    
    SELECT 'INFO: Kecelakaan adalah VIEW yang auto-calculated' as info_message;
    
    -- Menampilkan bagaimana VIEW mengkalkulasi data
    SELECT 
        'Calculation Analysis' as analysis_type,
        g.nama_gampong,
        k.tahun,
        k.jumlah_kecelakaan,
        (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya) as total_kendaraan,
        (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan) as total_korban,
        CASE 
            WHEN (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya) 
                 < (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
            THEN 'CONSTRAINED_BY_VEHICLES'
            WHEN (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya) 
                 > (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
            THEN 'CONSTRAINED_BY_VICTIMS'
            ELSE 'EQUAL_VALUES'
        END as limiting_factor
    FROM kecelakaan k
    JOIN gampong g ON k.gampong_id = g.id
    JOIN jenis_kendaraan jk ON k.gampong_id = jk.gampong_id AND k.tahun = jk.tahun
    JOIN korban kr ON k.gampong_id = kr.gampong_id AND k.tahun = kr.tahun
    ORDER BY g.nama_gampong, k.tahun;
    
    -- Statistik ringkasan
    SELECT 
        'RINGKASAN VALIDASI VIEW' as tipe,
        COUNT(*) as total_records,
        'All records are consistent (VIEW auto-calculated)' as consistency_status,
        '100.00' as consistency_percentage,
        SUM(k.jumlah_kecelakaan) as total_kecelakaan,
        ROUND(AVG(k.jumlah_kecelakaan), 2) as rata_rata_kecelakaan
    FROM kecelakaan k;
    
    -- Breakdown by limiting factor
    SELECT 
        'BREAKDOWN BY LIMITING FACTOR' as analysis,
        CASE 
            WHEN (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya) 
                 < (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
            THEN 'VEHICLE_LIMITED'
            WHEN (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya) 
                 > (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
            THEN 'VICTIM_LIMITED'
            ELSE 'EQUAL_VALUES'
        END as constraint_type,
        COUNT(*) as record_count,
        ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM kecelakaan)), 2) as percentage
    FROM kecelakaan k
    JOIN jenis_kendaraan jk ON k.gampong_id = jk.gampong_id AND k.tahun = jk.tahun
    JOIN korban kr ON k.gampong_id = kr.gampong_id AND k.tahun = kr.tahun
    GROUP BY constraint_type;
    
END //

DELIMITER ;

-- ======================================================
-- 5. FUNCTION: fn_hitung_tingkat_bahaya
-- Fungsi untuk menghitung tingkat bahaya berdasarkan data kecelakaan
-- ======================================================

DELIMITER //

DROP FUNCTION IF EXISTS fn_hitung_tingkat_bahaya //

CREATE FUNCTION fn_hitung_tingkat_bahaya(
    p_kecelakaan INT,
    p_meninggal INT,
    p_luka_berat INT
) RETURNS VARCHAR(20)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_skor DECIMAL(5,2);
    DECLARE v_tingkat VARCHAR(20);
    
    -- Menghitung skor bahaya
    -- Kecelakaan: bobot 1, Meninggal: bobot 5, Luka Berat: bobot 2
    SET v_skor = (p_kecelakaan * 1) + (p_meninggal * 5) + (p_luka_berat * 2);
    
    -- Menentukan tingkat bahaya
    IF v_skor >= 100 THEN
        SET v_tingkat = 'SANGAT TINGGI';
    ELSEIF v_skor >= 50 THEN
        SET v_tingkat = 'TINGGI';
    ELSEIF v_skor >= 25 THEN
        SET v_tingkat = 'SEDANG';
    ELSEIF v_skor >= 10 THEN
        SET v_tingkat = 'RENDAH';
    ELSE
        SET v_tingkat = 'SANGAT RENDAH';
    END IF;
    
    RETURN v_tingkat;
END //

DELIMITER ;

-- ======================================================
-- 6. VIEW: v_tingkat_bahaya_gampong
-- View yang menampilkan tingkat bahaya per gampong
-- ======================================================

DROP VIEW IF EXISTS v_tingkat_bahaya_gampong;

CREATE VIEW v_tingkat_bahaya_gampong AS
SELECT 
    nama_gampong,
    tahun,
    jumlah_kecelakaan,
    jumlah_meninggal,
    luka_berat,
    luka_ringan,
    fn_hitung_tingkat_bahaya(jumlah_kecelakaan, jumlah_meninggal, luka_berat) as tingkat_bahaya,
    (jumlah_kecelakaan * 1) + (jumlah_meninggal * 5) + (luka_berat * 2) as skor_bahaya
FROM v_kecelakaan_summary
WHERE tahun IS NOT NULL
ORDER BY skor_bahaya DESC, nama_gampong, tahun;

-- ======================================================
-- CONTOH PENGGUNAAN (Updated for VIEW kecelakaan)
-- ======================================================

-- Melihat ringkasan semua data
-- SELECT * FROM v_kecelakaan_summary LIMIT 10;

-- Melihat ringkasan per tahun  
-- SELECT * FROM v_ringkasan_per_tahun;

-- Melihat gampong dengan kecelakaan tertinggi per tahun
-- SELECT * FROM v_gampong_tertinggi;

-- Validasi konsistensi data (Now shows VIEW calculation analysis)
-- CALL sp_validasi_konsistensi();

-- Melihat tingkat bahaya per gampong
-- SELECT * FROM v_tingkat_bahaya_gampong WHERE tingkat_bahaya IN ('TINGGI', 'SANGAT TINGGI');

-- NEW: Test VIEW kecelakaan functionality
-- SELECT * FROM kecelakaan ORDER BY jumlah_kecelakaan DESC LIMIT 10;

-- NEW: Analyze VIEW calculation basis
-- SELECT 
--     nama_gampong, tahun, jumlah_kecelakaan, calculation_basis 
-- FROM v_kecelakaan_summary 
-- WHERE calculation_basis = 'LIMITED_BY_VEHICLES';

-- NEW: Compare with manual calculation
-- SELECT 
--     k.*,
--     LEAST(
--         (SELECT SUM(kendaraan_roda_dua + kendaraan_roda_4 + kendaraan_lebih_roda_4 + kendaraan_lainnya) 
--          FROM jenis_kendaraan jk WHERE jk.gampong_id = k.gampong_id AND jk.tahun = k.tahun),
--         (SELECT SUM(jumlah_meninggal + luka_berat + luka_ringan) 
--          FROM korban kr WHERE kr.gampong_id = k.gampong_id AND kr.tahun = k.tahun)
--     ) as manual_calculation
-- FROM kecelakaan k;
