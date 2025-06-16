-- Add new columns for victim categories to the korban table
-- Run this script to add Luka Berat and Luka Ringan columns

USE kecelakaan_data;

-- Add new columns to korban table
ALTER TABLE korban 
ADD COLUMN IF NOT EXISTS luka_berat INT DEFAULT 0 AFTER jumlah_meninggal,
ADD COLUMN IF NOT EXISTS luka_ringan INT DEFAULT 0 AFTER luka_berat;

-- Update existing records with some sample data (you can modify these values)
-- This is just to populate the new columns with reasonable test data
UPDATE korban SET 
    luka_berat = FLOOR(RAND() * (jumlah_meninggal * 2 + 10)) + 1,
    luka_ringan = FLOOR(RAND() * (jumlah_meninggal * 3 + 15)) + 2
WHERE luka_berat IS NULL OR luka_berat = 0;

-- Show the updated table structure
DESCRIBE korban;

-- Show sample data to verify the update
SELECT gampong_id, tahun, jumlah_meninggal, luka_berat, luka_ringan 
FROM korban 
LIMIT 10;