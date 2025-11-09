"""
PostgreSQL Database Setup Script for SLAQ

This script automates the creation of the PostgreSQL database for SLAQ.
It will:
1. Connect to PostgreSQL
2. Create the slaq_db database
3. Verify the connection
4. Optionally update your .env file

Usage:
    python setup_database.py

Requirements:
    - PostgreSQL installed and running
    - psycopg2-binary (already in requirements.txt)
    - Your PostgreSQL password
"""

import sys
import os
from pathlib import Path
from getpass import getpass

def check_postgres_connection(password):
    """Test connection to PostgreSQL server"""
    try:
        import psycopg2
        
        # Connect to default 'postgres' database
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password=password,
            host='localhost',
            port='5432'
        )
        conn.close()
        return True
    except ImportError:
        print("❌ Error: psycopg2 not installed!")
        print("   Run: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Common issues:")
        print("  1. Wrong password")
        print("  2. PostgreSQL service not running")
        print("  3. PostgreSQL not installed")
        print()
        print("To check if PostgreSQL is running:")
        print("  Get-Service -Name postgresql*")
        print()
        return False


def database_exists(password, dbname='slaq_db'):
    """Check if database already exists"""
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password=password,
            host='localhost',
            port='5432'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (dbname,)
        )
        exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        
        return exists
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False


def create_database(password, dbname='slaq_db'):
    """Create the SLAQ database"""
    try:
        import psycopg2
        
        # Connect to default postgres database
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password=password,
            host='localhost',
            port='5432'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create database
        print(f"Creating database '{dbname}'...")
        cursor.execute(f"CREATE DATABASE {dbname}")
        print(f"✅ Database '{dbname}' created successfully!")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False


def verify_database_connection(password, dbname='slaq_db'):
    """Verify connection to the created database"""
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            dbname=dbname,
            user='postgres',
            password=password,
            host='localhost',
            port='5432'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Successfully connected to '{dbname}'!")
        print(f"   PostgreSQL version: {version.split(',')[0]}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to verify connection: {e}")
        return False


def update_env_file(password):
    """Update .env file with database credentials"""
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("⚠️  Warning: .env file not found!")
        print("   Please create .env file manually with database credentials.")
        return False
    
    try:
        # Read existing .env
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update DB_PASSWORD line
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('DB_PASSWORD='):
                lines[i] = f'DB_PASSWORD={password}\n'
                updated = True
                break
        
        if not updated:
            print("⚠️  DB_PASSWORD not found in .env file.")
            return False
        
        # Write back
        with open(env_path, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Updated .env file with database password")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not update .env file: {e}")
        print("   Please update DB_PASSWORD manually in .env")
        return False


def main():
    """Main setup function"""
    print()
    print("=" * 60)
    print("SLAQ PostgreSQL Database Setup")
    print("=" * 60)
    print()
    
    # Get PostgreSQL password
    print("Please enter your PostgreSQL password")
    print("(This is the password you set when installing PostgreSQL)")
    print()
    password = getpass("PostgreSQL password: ")
    
    if not password:
        print("❌ Password cannot be empty!")
        sys.exit(1)
    
    print()
    print("Testing PostgreSQL connection...")
    
    # Test connection
    if not check_postgres_connection(password):
        print()
        print("Setup failed. Please fix the connection issue and try again.")
        sys.exit(1)
    
    print("✅ PostgreSQL connection successful!")
    print()
    
    # Check if database already exists
    if database_exists(password):
        print("ℹ️  Database 'slaq_db' already exists!")
        print()
        
        # Still verify connection
        if verify_database_connection(password):
            print()
            print("=" * 60)
            print("✅ Database is ready to use!")
            print("=" * 60)
            print()
            
            # Ask to update .env
            response = input("Update .env file with this password? (y/n): ")
            if response.lower() == 'y':
                update_env_file(password)
            
            print()
            print("Next steps:")
            print("  1. Ensure .env file has correct DB_PASSWORD")
            print("  2. Run: python manage.py migrate")
            print("  3. Run: python manage.py createsuperuser")
            print("  4. Run: python manage.py runserver")
            print()
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Create database
    print()
    if not create_database(password):
        sys.exit(1)
    
    print()
    
    # Verify connection to new database
    if not verify_database_connection(password):
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ SUCCESS! Database setup complete")
    print("=" * 60)
    print()
    
    # Ask to update .env
    response = input("Update .env file with this password? (y/n): ")
    if response.lower() == 'y':
        update_env_file(password)
    else:
        print()
        print("⚠️  Remember to update your .env file manually:")
        print(f"   DB_PASSWORD={password}")
    
    print()
    print("🎉 Database 'slaq_db' is ready!")
    print()
    print("Next steps:")
    print("  1. Verify .env file has correct DB_PASSWORD")
    print("  2. Run: python manage.py migrate")
    print("  3. Run: python manage.py createsuperuser")
    print("  4. Run: python manage.py runserver")
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
