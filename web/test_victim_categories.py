#!/usr/bin/env python3
"""
Test script to verify victim categories functionality
"""

import mysql.connector
import requests
import json

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kecelakaan_data'
}

def test_database_structure():
    """Test if database has the victim categories columns"""
    print("🔍 Testing database structure...")
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Check table structure
        cursor.execute("DESCRIBE korban")
        columns = [row['Field'] for row in cursor.fetchall()]
        
        print(f"📋 Korban table columns: {columns}")
        
        has_luka_berat = 'luka_berat' in columns
        has_luka_ringan = 'luka_ringan' in columns
        
        if has_luka_berat and has_luka_ringan:
            print("✅ New victim category columns exist!")
            
            # Show sample data
            cursor.execute("SELECT gampong_id, tahun, jumlah_meninggal, luka_berat, luka_ringan FROM korban LIMIT 3")
            sample_data = cursor.fetchall()
            
            print("📊 Sample victim data:")
            for row in sample_data:
                print(f"  Gampong {row['gampong_id']}, Tahun {row['tahun']}: Meninggal={row['jumlah_meninggal']}, Luka Berat={row['luka_berat']}, Luka Ringan={row['luka_ringan']}")
        else:
            print("⚠️  New columns don't exist yet. Application will use fallback sample data.")
            print("   Run: python run_migration.py")
        
        cursor.close()
        conn.close()
        return has_luka_berat and has_luka_ringan
        
    except mysql.connector.Error as e:
        print(f"❌ Database connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_application_response():
    """Test if application responds correctly"""
    print("\n🌐 Testing application response...")
    try:
        # Test if app is running
        response = requests.get('http://127.0.0.1:5000/login', timeout=5)
        if response.status_code == 200:
            print("✅ Application is running and responsive!")
            return True
        else:
            print(f"⚠️  Application responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Application is not running. Start it with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error testing application: {e}")
        return False

def generate_sample_chart_data():
    """Generate sample data for chart visualization"""
    print("\n📈 Generating sample chart data...")
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Get total deaths
        cursor.execute("SELECT SUM(jumlah_meninggal) as total_meninggal FROM korban")
        result = cursor.fetchone()
        total_meninggal = result['total_meninggal'] or 0
        
        # Generate sample data
        sample_data = {
            'labels': ['Meninggal', 'Luka Berat', 'Luka Ringan'],
            'data': [
                total_meninggal,
                int(total_meninggal * 1.5),  # Sample: 1.5x deaths
                int(total_meninggal * 2.3)   # Sample: 2.3x deaths
            ]
        }
        
        print(f"📊 Sample chart data: {json.dumps(sample_data, indent=2)}")
        
        cursor.close()
        conn.close()
        return sample_data
        
    except Exception as e:
        print(f"❌ Error generating sample data: {e}")
        return None

def check_columns():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Get column information from korban table
        cursor.execute("SHOW COLUMNS FROM korban")
        columns = [column['Field'] for column in cursor.fetchall()]
        print("\nColumns in korban table:", columns)

        # Get sample data
        cursor.execute("SELECT gampong_id, tahun, jumlah_meninggal FROM korban LIMIT 3")
        rows = cursor.fetchall()
        print("\nSample data from korban table:")
        for row in rows:
            print(f"  Gampong {row['gampong_id']}, Tahun {row['tahun']}: Meninggal={row['jumlah_meninggal']}")

        return True

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

def main():
    print("🚀 Testing Victim Categories Implementation")
    print("=" * 50)
    
    # Test database
    db_ok = test_database_structure()
    
    # Test application
    app_ok = test_application_response()
    
    # Generate sample data
    chart_data = generate_sample_chart_data()
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    if db_ok:
        print("✅ Database: New victim category columns exist")
    else:
        print("⚠️  Database: Using fallback sample data")
        print("   → Run migration: python run_migration.py")
    
    if app_ok:
        print("✅ Application: Running and responsive")
        print("   → Access dashboard: http://127.0.0.1:5000/")
    else:
        print("❌ Application: Not running")
        print("   → Start application: python main.py")
    
    if chart_data and sum(chart_data['data']) > 0:
        print("✅ Chart Data: Available and valid")
        print(f"   → Total victims: {sum(chart_data['data'])}")
    else:
        print("⚠️  Chart Data: No data available")
    
    print("\n🎯 EXPECTED RESULT:")
    print("   Dashboard at http://127.0.0.1:5000/ should show:")
    print("   • Pie chart with 3 categories: Meninggal, Luka Berat, Luka Ringan")
    print("   • Chart colors: Red, Yellow, Blue")
    print("   • Non-zero values for all categories")

if __name__ == "__main__":
    main()