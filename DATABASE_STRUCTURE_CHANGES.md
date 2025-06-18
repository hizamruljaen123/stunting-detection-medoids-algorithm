# Database Structure Changes - Migration Summary

## Overview
The application has been updated to work with a new normalized database structure that replaces the old `kecelakaan` table with calculated views based on vehicle data.

## Database Schema Changes

### Removed Tables
- `kecelakaan` - No longer exists as a direct table

### New/Modified Tables
1. **gampong** - Unchanged (id, nama_gampong)
2. **jenis_kendaraan** - Contains vehicle type data (AUTO_INCREMENT id, gampong_id, kendaraan_roda_dua, kendaraan_roda_4, kendaraan_lebih_roda_4, kendaraan_lainnya, tahun)
3. **kondisi_jalan** - Road condition data (AUTO_INCREMENT id, gampong_id, jalan_berlubang, jalan_jalur_dua, tahun)
4. **koordinat** - Location coordinates (AUTO_INCREMENT id, gampong_id, latitude, longitude)
5. **korban** - Victim data with new columns (AUTO_INCREMENT id, gampong_id, jumlah_meninggal, tahun, luka_berat, luka_ringan)

### New Views
1. **total_kecelakaan** - Calculates accidents from vehicle data:
   ```sql
   jumlah_kecelakaan = kendaraan_roda_dua + kendaraan_roda_4 + kendaraan_lebih_roda_4 + kendaraan_lainnya
   ```

2. **total_korban** - Aggregates victim data:
   ```sql
   total_korban = jumlah_meninggal + luka_berat + luka_ringan
   ```

## Code Changes in main.py

### Key Function Updates

#### 1. get_combined_data()
- Now uses the new `total_kecelakaan` and `total_korban` views
- Simplified query structure using COALESCE for NULL handling
- Joins data from all tables using the views as primary sources

#### 2. Dashboard Functions
- **dashboard()**: Updated to use new views for statistics
- **statistik_kecelakaan()**: Now queries `total_kecelakaan` view
- **statistik_korban()**: Now queries `total_korban` view
- **peta_interaktif_page()**: Updated to use new views for filters

#### 3. CRUD Operations
- **Removed**: All kecelakaan CRUD operations (add/edit/delete)
- **Updated**: gampong_statistics API now uses views
- **Maintained**: All other CRUD operations for existing tables

#### 4. Data Management
- **manage_data_page()**: Removed kecelakaan_data from template context
- Template now manages: gampong, korban, jenis_kendaraan, kondisi_jalan, koordinat

### Query Pattern Changes

#### Before (Old Structure):
```python
cursor.execute("SELECT * FROM kecelakaan k JOIN gampong g ON k.gampong_id = g.id")
```

#### After (New Structure):
```python
cursor.execute("""
    SELECT tk.jumlah_kecelakaan, tk.nama_gampong, tk.tahun
    FROM total_kecelakaan tk
""")
```

## Template Updates Required

### data.html Template
- Remove all kecelakaan table management sections
- Accident data now calculated automatically from vehicle data
- Focus on managing: jenis_kendaraan, kondisi_jalan, korban, koordinat

### Form Updates
- Remove kecelakaan add/edit forms
- Vehicle data (jenis_kendaraan) now drives accident calculations
- Victim forms now include luka_berat and luka_ringan fields

## Benefits of New Structure

1. **Data Integrity**: Accidents calculated from actual vehicle data
2. **Normalization**: Separate concerns (vehicles, victims, road conditions)
3. **Flexibility**: Easier to analyze different aspects independently
4. **Consistency**: Views ensure consistent calculations across the application

## Migration Considerations

1. **Data Migration**: Existing accident data needs to be redistributed into vehicle tables
2. **View Dependencies**: Application now depends on database views
3. **Backup**: Old structure should be backed up before migration
4. **Testing**: All features need retesting with new data structure

## Files Modified

1. `main.py` - All database interaction functions updated
2. `DATABASE_STRUCTURE_CHANGES.md` - This documentation (new)

## Files Requiring Updates

1. `templates/data.html` - Remove kecelakaan forms, update CRUD interface
2. `templates/dashboard.html` - May need adjustments for new data flow
3. `static/js/*.js` - Frontend JavaScript may need updates for API changes
4. Database migration scripts - To convert existing data

## Next Steps

1. Update HTML templates to match new structure
2. Update JavaScript files for new API endpoints
3. Create data migration scripts
4. Test all functionality with new database structure
5. Update user documentation
