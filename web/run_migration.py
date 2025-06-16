#!/usr/bin/env python3
"""
Script to run database migration for adding victim categories
"""

import mysql.connector
import subprocess
import sys

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kecelakaan_data'
}

def run_sql_file(file_path):
    """Run SQL file using mysql command"""
    try:
        # Run the SQL file using mysql command
        cmd = [
            'mysql',
            '-h', db_config['host'],
            '-u', db_config['user'],
            db_config['database']
        ]
        
        if db_config['password']:
            cmd.extend(['-p' + db_config['password']])
        
        with open(file_path, 'r') as sql_file:
            result = subprocess.run(cmd, stdin=sql_file, capture_output=True, text=True)
            
        if result.returncode == 0:
            print(f"✅ Successfully executed {file_path}")
            print("Output:", result.stdout)
        else:
            print(f"❌ Error executing {file_path}")
            print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Exception running {file_path}: {e}")
        return False
    
    return True

def run_python_migration():
    """Run migration using Python mysql connector"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("🔄 Running database migration...")
        
        # Check if columns already exist
        cursor.execute("DESCRIBE korban")
        columns = [row[0] for row in cursor.fetchall()]
        
        if 'luka_berat' not in columns:
            print("➕ Adding luka_berat column...")
            cursor.execute("ALTER TABLE korban ADD COLUMN luka_berat INT DEFAULT 0 AFTER jumlah_meninggal")
            
        if 'luka_ringan' not in columns:
            print("➕ Adding luka_ringan column...")
            cursor.execute("ALTER TABLE korban ADD COLUMN luka_ringan INT DEFAULT 0 AFTER luka_berat")
        
        # Update existing records with sample data
        print("📝 Updating existing records with sample data...")
        cursor.execute("""
            UPDATE korban SET 
                luka_berat = FLOOR(RAND() * (jumlah_meninggal * 2 + 10)) + 1,
                luka_ringan = FLOOR(RAND() * (jumlah_meninggal * 3 + 15)) + 2
            WHERE (luka_berat IS NULL OR luka_berat = 0) AND (luka_ringan IS NULL OR luka_ringan = 0)
        """)
        
        conn.commit()
        
        # Show updated table structure
        print("\n📋 Updated table structure:")
        cursor.execute("DESCRIBE korban")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # Show sample data
        print("\n📊 Sample data:")
        cursor.execute("SELECT gampong_id, tahun, jumlah_meninggal, luka_berat, luka_ringan FROM korban LIMIT 5")
        for row in cursor.fetchall():
            print(f"  Gampong {row[0]}, Tahun {row[1]}: Meninggal={row[2]}, Luka Berat={row[3]}, Luka Ringan={row[4]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Migration completed successfully!")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🚀 Starting database migration for victim categories...")
    
    # Try Python migration first
    if run_python_migration():
        print("\n🎉 Migration completed! You can now run the application with:")
        print("   python main.py")
        print("\nThe dashboard will now show:")
        print("   - Meninggal (Deaths)")
        print("   - Luka Berat (Serious Injuries)")  
        print("   - Luka Ringan (Minor Injuries)")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        print("You may need to run the SQL file manually:")
        print("   mysql -u root -p kecelakaan_data < add_victim_categories.sql")

if __name__ == "__main__":
    main()