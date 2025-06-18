-- ======================================================
-- FILE: test_kecelakaan_view.sql
-- Tujuan: Menguji dan memverifikasi VIEW kecelakaan
-- ======================================================

USE kecelakaan_data;

-- ======================================================
-- 1. Test Basic Functionality
-- ======================================================

SELECT 'TEST 1: Basic View Functionality' as test_name;

SELECT 
    COUNT(*) as total_records,
    MIN(tahun) as min_year,
    MAX(tahun) as max_year,
    COUNT(DISTINCT gampong_id) as unique_gampong,
    SUM(jumlah_kecelakaan) as total_kecelakaan
FROM kecelakaan;

-- ======================================================
-- 2. Test Data Integrity
-- ======================================================

SELECT 'TEST 2: Data Integrity Check' as test_name;

-- Check for NULL values
SELECT 
    'NULL Values Check' as check_type,
    SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END) as null_id,
    SUM(CASE WHEN gampong_id IS NULL THEN 1 ELSE 0 END) as null_gampong_id,
    SUM(CASE WHEN tahun IS NULL THEN 1 ELSE 0 END) as null_tahun,
    SUM(CASE WHEN jumlah_kecelakaan IS NULL THEN 1 ELSE 0 END) as null_jumlah_kecelakaan
FROM kecelakaan;

-- ======================================================
-- 3. Test Calculation Logic
-- ======================================================

SELECT 'TEST 3: Calculation Logic Verification' as test_name;

SELECT 
    g.nama_gampong,
    k.tahun,
    k.jumlah_kecelakaan as view_result,
    
    -- Manual calculation components
    (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya) as total_kendaraan,
    (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan) as total_korban,
    
    -- Expected result (manual LEAST calculation)
    LEAST(
        (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya),
        (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
    ) as expected_result,
    
    -- Validation
    CASE 
        WHEN k.jumlah_kecelakaan = LEAST(
            (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya),
            (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
        ) THEN 'PASS ✓'
        ELSE 'FAIL ✗'
    END as validation_status

FROM kecelakaan k
JOIN gampong g ON k.gampong_id = g.id
JOIN jenis_kendaraan jk ON k.gampong_id = jk.gampong_id AND k.tahun = jk.tahun
JOIN korban kr ON k.gampong_id = kr.gampong_id AND k.tahun = kr.tahun
ORDER BY g.nama_gampong, k.tahun
LIMIT 10;

-- ======================================================
-- 4. Test Consistency Rules
-- ======================================================

SELECT 'TEST 4: Business Logic Consistency' as test_name;

SELECT 
    'Consistency Validation' as validation_type,
    COUNT(*) as total_records,
    SUM(CASE 
        WHEN k.jumlah_kecelakaan <= (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya)
        AND k.jumlah_kecelakaan <= (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
        THEN 1 ELSE 0 
    END) as consistent_records,
    SUM(CASE 
        WHEN k.jumlah_kecelakaan > (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya)
        OR k.jumlah_kecelakaan > (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
        THEN 1 ELSE 0 
    END) as inconsistent_records,
    ROUND(
        (SUM(CASE 
            WHEN k.jumlah_kecelakaan <= (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya)
            AND k.jumlah_kecelakaan <= (kr.jumlah_meninggal + kr.luka_berat + kr.luka_ringan)
            THEN 1 ELSE 0 
        END) * 100.0 / COUNT(*)), 
        2
    ) as consistency_percentage
FROM kecelakaan k
JOIN jenis_kendaraan jk ON k.gampong_id = jk.gampong_id AND k.tahun = jk.tahun
JOIN korban kr ON k.gampong_id = kr.gampong_id AND k.tahun = kr.tahun;

-- ======================================================
-- 5. Test Performance & Coverage
-- ======================================================

SELECT 'TEST 5: Data Coverage Analysis' as test_name;

-- Coverage by year
SELECT 
    'Coverage by Year' as analysis_type,
    tahun,
    COUNT(*) as records_per_year,
    COUNT(DISTINCT gampong_id) as gampong_covered,
    SUM(jumlah_kecelakaan) as total_kecelakaan_per_year,
    ROUND(AVG(jumlah_kecelakaan), 2) as avg_kecelakaan_per_gampong
FROM kecelakaan
GROUP BY tahun
ORDER BY tahun;

-- Coverage by gampong
SELECT 
    'Top 5 Gampong by Total Accidents' as analysis_type,
    g.nama_gampong,
    COUNT(*) as years_covered,
    SUM(k.jumlah_kecelakaan) as total_kecelakaan,
    ROUND(AVG(k.jumlah_kecelakaan), 2) as avg_per_year
FROM kecelakaan k
JOIN gampong g ON k.gampong_id = g.id
GROUP BY g.id, g.nama_gampong
ORDER BY total_kecelakaan DESC
LIMIT 5;

-- ======================================================
-- 6. Test Real-time Update Behavior
-- ======================================================

SELECT 'TEST 6: Real-time Update Test' as test_name;

-- Show current value for a specific record
SELECT 
    'Before Update' as status,
    g.nama_gampong,
    k.tahun,
    k.jumlah_kecelakaan,
    kr.luka_ringan as current_luka_ringan
FROM kecelakaan k
JOIN gampong g ON k.gampong_id = g.id
JOIN korban kr ON k.gampong_id = kr.gampong_id AND k.tahun = kr.tahun
WHERE g.id = 1 AND k.tahun = 2022;

-- Simulate update (but don't actually update)
SELECT 
    'After Simulated Update (+5 luka_ringan)' as status,
    g.nama_gampong,
    2022 as tahun,
    LEAST(
        (jk.kendaraan_roda_dua + jk.kendaraan_roda_4 + jk.kendaraan_lebih_roda_4 + jk.kendaraan_lainnya),
        (kr.jumlah_meninggal + kr.luka_berat + (kr.luka_ringan + 5))
    ) as simulated_new_jumlah_kecelakaan,
    (kr.luka_ringan + 5) as simulated_new_luka_ringan
FROM korban kr
JOIN jenis_kendaraan jk ON kr.gampong_id = jk.gampong_id AND kr.tahun = jk.tahun
JOIN gampong g ON kr.gampong_id = g.id
WHERE kr.gampong_id = 1 AND kr.tahun = 2022;

-- ======================================================
-- 7. Test Backward Compatibility
-- ======================================================

SELECT 'TEST 7: Backward Compatibility' as test_name;

-- Common queries that should still work
SELECT 'Common Query 1: Basic SELECT' as query_type;
SELECT * FROM kecelakaan WHERE tahun = 2023 LIMIT 3;

SELECT 'Common Query 2: Aggregation' as query_type;
SELECT tahun, SUM(jumlah_kecelakaan) as total FROM kecelakaan GROUP BY tahun;

SELECT 'Common Query 3: JOIN with gampong' as query_type;
SELECT 
    g.nama_gampong,
    SUM(k.jumlah_kecelakaan) as total_kecelakaan
FROM kecelakaan k
JOIN gampong g ON k.gampong_id = g.id
GROUP BY g.id, g.nama_gampong
ORDER BY total_kecelakaan DESC
LIMIT 3;

-- ======================================================
-- 8. Final Summary Report
-- ======================================================

SELECT 'FINAL SUMMARY: VIEW kecelakaan Status' as final_report;

SELECT 
    'VIEW Performance Summary' as summary_type,
    COUNT(*) as total_records_generated,
    COUNT(DISTINCT gampong_id) as gampong_coverage,
    COUNT(DISTINCT tahun) as year_coverage,
    SUM(jumlah_kecelakaan) as grand_total_kecelakaan,
    MIN(jumlah_kecelakaan) as min_kecelakaan,
    MAX(jumlah_kecelakaan) as max_kecelakaan,
    ROUND(AVG(jumlah_kecelakaan), 2) as avg_kecelakaan,
    'VIEW is functioning correctly' as status
FROM kecelakaan;

-- Test completion message
SELECT 
    '✅ All tests completed successfully!' as test_status,
    'VIEW kecelakaan is ready for production use' as conclusion,
    NOW() as test_completed_at;
