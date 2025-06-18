-- ======================================================
-- FILE: verify_data_consistency.sql
-- Tujuan: Script untuk memverifikasi konsistensi data setelah perbaikan
-- ======================================================

USE kecelakaan_data;

-- ======================================================
-- 1. VALIDASI TOTAL KECELAKAAN PER GAMPONG PER TAHUN
-- ======================================================

SELECT 
    'VALIDASI KECELAKAAN vs KENDARAAN' as validasi_type,
    g.nama_gampong,
    k.tahun,
    k.jumlah_kecelakaan,
    (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya) as total_kendaraan,
    (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan) as total_korban,
    CASE 
        WHEN k.jumlah_kecelakaan <= (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya)
        AND k.jumlah_kecelakaan <= (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
        THEN 'VALID ✓'
        ELSE 'INVALID ✗'
    END as status_validasi
FROM gampong g
JOIN kecelakaan k ON g.id = k.gampong_id
JOIN jenis_kendaraan jk ON g.id = jk.gampong_id AND k.tahun = jk.tahun
JOIN korban kr ON g.id = kr.gampong_id AND k.tahun = kr.tahun
ORDER BY g.nama_gampong, k.tahun;

-- ======================================================
-- 2. RINGKASAN TOTAL PER TAHUN
-- ======================================================

SELECT 
    'RINGKASAN PER TAHUN' as summary_type,
    k.tahun,
    COUNT(DISTINCT k.gampong_id) as jumlah_gampong,
    SUM(k.jumlah_kecelakaan) as total_kecelakaan,
    SUM(jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya) as total_kendaraan,
    SUM(kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan) as total_korban,
    ROUND(AVG(k.jumlah_kecelakaan), 2) as rata_rata_kecelakaan_per_gampong
FROM kecelakaan k
JOIN jenis_kendaraan jk ON k.gampong_id = jk.gampong_id AND k.tahun = jk.tahun
JOIN korban kr ON k.gampong_id = kr.gampong_id AND k.tahun = kr.tahun
GROUP BY k.tahun
ORDER BY k.tahun;

-- ======================================================
-- 3. GAMPONG DENGAN KECELAKAAN TERTINGGI DAN TERENDAH PER TAHUN
-- ======================================================

-- Tertinggi per tahun
SELECT 
    'GAMPONG KECELAKAAN TERTINGGI' as category,
    tahun,
    nama_gampong,
    jumlah_kecelakaan,
    total_korban
FROM (
    SELECT 
        k.tahun,
        g.nama_gampong,
        k.jumlah_kecelakaan,
        (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan) as total_korban,
        ROW_NUMBER() OVER (PARTITION BY k.tahun ORDER BY k.jumlah_kecelakaan DESC) as rn
    FROM kecelakaan k
    JOIN gampong g ON k.gampong_id = g.id
    JOIN korban kr ON k.gampong_id = kr.gampong_id AND k.tahun = kr.tahun
) ranked
WHERE rn = 1
ORDER BY tahun;

-- Terendah per tahun
SELECT 
    'GAMPONG KECELAKAAN TERENDAH' as category,
    tahun,
    nama_gampong,
    jumlah_kecelakaan,
    total_korban
FROM (
    SELECT 
        k.tahun,
        g.nama_gampong,
        k.jumlah_kecelakaan,
        (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan) as total_korban,
        ROW_NUMBER() OVER (PARTITION BY k.tahun ORDER BY k.jumlah_kecelakaan ASC) as rn
    FROM kecelakaan k
    JOIN gampong g ON k.gampong_id = g.id
    JOIN korban kr ON k.gampong_id = kr.gampong_id AND k.tahun = kr.tahun
) ranked
WHERE rn = 1
ORDER BY tahun;

-- ======================================================
-- 4. DISTRIBUSI JENIS KENDARAAN TERLIBAT
-- ======================================================

SELECT 
    'DISTRIBUSI KENDARAAN' as analysis_type,
    tahun,
    SUM(kendaraan_roda_dua) as total_roda_2,
    SUM(kendaraan_roda_4) as total_roda_4,
    SUM(kendaraan_lebih_roda_4) as total_lebih_roda_4,
    SUM(kendaraan_lainnya) as total_lainnya,
    SUM(kendaraan_roda_dua + kendaraan_roda_4 + kendaraan_lebih_roda_4 + kendaraan_lainnya) as grand_total,
    -- Persentase
    ROUND((SUM(kendaraan_roda_dua) * 100.0 / SUM(kendaraan_roda_dua + kendaraan_roda_4 + kendaraan_lebih_roda_4 + kendaraan_lainnya)), 2) as persen_roda_2,
    ROUND((SUM(kendaraan_roda_4) * 100.0 / SUM(kendaraan_roda_dua + kendaraan_roda_4 + kendaraan_lebih_roda_4 + kendaraan_lainnya)), 2) as persen_roda_4
FROM jenis_kendaraan
GROUP BY tahun
ORDER BY tahun;

-- ======================================================
-- 5. DISTRIBUSI TINGKAT KORBAN
-- ======================================================

SELECT 
    'DISTRIBUSI KORBAN' as analysis_type,
    tahun,
    SUM(jumlah_meninggal) as total_meninggal,
    SUM(luka_berat) as total_luka_berat,
    SUM(luka_ringan) as total_luka_ringan,
    SUM(jumlah_meninggal + luka_berat + luka_ringan) as total_korban,
    -- Tingkat fatalitas
    ROUND((SUM(jumlah_meninggal) * 100.0 / SUM(jumlah_meninggal + luka_berat + luka_ringan)), 2) as tingkat_fatalitas_persen,
    ROUND((SUM(luka_berat) * 100.0 / SUM(jumlah_meninggal + luka_berat + luka_ringan)), 2) as tingkat_luka_berat_persen
FROM korban
GROUP BY tahun
ORDER BY tahun;

-- ======================================================
-- 6. KORELASI KONDISI JALAN DAN KECELAKAAN
-- ======================================================

SELECT 
    'KORELASI JALAN-KECELAKAAN' as analysis_type,
    tahun,
    SUM(kj.jalan_berlubang) as total_jalan_berlubang,
    SUM(kj.jalan_jalur_dua) as total_jalan_jalur_dua,
    SUM(k.jumlah_kecelakaan) as total_kecelakaan,
    -- Rasio
    ROUND((SUM(k.jumlah_kecelakaan) * 1.0 / SUM(kj.jalan_berlubang + kj.jalan_jalur_dua)), 2) as rasio_kecelakaan_per_kondisi_jalan
FROM kondisi_jalan kj
JOIN kecelakaan k ON kj.gampong_id = k.gampong_id AND kj.tahun = k.tahun
GROUP BY tahun
ORDER BY tahun;

-- ======================================================
-- 7. RINGKASAN VALIDASI AKHIR
-- ======================================================

SELECT 
    'VALIDASI AKHIR' as final_check,
    COUNT(*) as total_records,
    SUM(CASE 
        WHEN k.jumlah_kecelakaan <= (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya)
        AND k.jumlah_kecelakaan <= (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
        THEN 1 ELSE 0 
    END) as records_valid,
    SUM(CASE 
        WHEN k.jumlah_kecelakaan > (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya)
        OR k.jumlah_kecelakaan > (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
        THEN 1 ELSE 0 
    END) as records_invalid,
    ROUND(
        (SUM(CASE 
            WHEN k.jumlah_kecelakaan <= (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya)
            AND k.jumlah_kecelakaan <= (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
            THEN 1 ELSE 0 
        END) * 100.0 / COUNT(*)), 
        2
    ) as persentase_valid
FROM kecelakaan k
JOIN jenis_kendaraan jk ON k.gampong_id = jk.gampong_id AND k.tahun = jk.tahun
JOIN korban kr ON k.gampong_id = kr.gampong_id AND k.tahun = kr.tahun;

-- ======================================================
-- 8. TOTAL KECELAKAAN KESELURUHAN (HARUS DALAM RATUSAN)
-- ======================================================

SELECT 
    'TOTAL KESELURUHAN' as summary,
    SUM(jumlah_kecelakaan) as grand_total_kecelakaan,
    COUNT(DISTINCT gampong_id) as jumlah_gampong,
    COUNT(DISTINCT tahun) as jumlah_tahun,
    ROUND(AVG(jumlah_kecelakaan), 2) as rata_rata_per_record,
    MIN(jumlah_kecelakaan) as kecelakaan_minimum,
    MAX(jumlah_kecelakaan) as kecelakaan_maksimum
FROM kecelakaan;
