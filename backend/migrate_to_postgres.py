"""
Migration script to safely migrate data from SQLite to PostgreSQL.

Usage:
    python migrate_to_postgres.py \
        --sqlite sqlite:///db/database.db \
        --postgres postgresql://user:pass@localhost/attendance_db

This script:
    1. Connects to both SQLite and PostgreSQL databases
    2. Validates that PostgreSQL has the correct schema
    3. Reads all data from SQLite
    4. Inserts data into PostgreSQL with validation
    5. Verifies row counts match between databases
"""

import argparse
import sys
from pathlib import Path

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import Student, Faculty, Attendance, RecognitionJob
from backend.extensions import db


def create_connections(sqlite_url: str, postgres_url: str):
    """Create connections to both databases."""
    sqlite_engine = create_engine(sqlite_url, echo=False)
    postgres_engine = create_engine(postgres_url, echo=False)
    
    # Test connections
    try:
        with sqlite_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[OK] Connected to SQLite")
    except Exception as e:
        print(f"[ERROR] Failed to connect to SQLite: {e}")
        return None, None
    
    try:
        with postgres_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[OK] Connected to PostgreSQL")
    except Exception as e:
        print(f"[ERROR] Failed to connect to PostgreSQL: {e}")
        return None, None
    
    return sqlite_engine, postgres_engine


def validate_schema(postgres_engine):
    """Validate that PostgreSQL has the required tables."""
    inspector = inspect(postgres_engine)
    required_tables = {"Student", "Faculty", "Attendance", "RecognitionJob"}
    existing_tables = set(inspector.get_table_names())
    
    if not required_tables.issubset(existing_tables):
        missing = required_tables - existing_tables
        print(f"[ERROR] Missing tables in PostgreSQL: {missing}")
        print("[HINT] Run: alembic upgrade head with DATABASE_URL pointing to PostgreSQL")
        return False
    
    print(f"[OK] All required tables exist in PostgreSQL")
    return True


def count_rows(engine, model):
    """Count rows in a table."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        return session.query(model).count()
    finally:
        session.close()


def migrate_data(sqlite_engine, postgres_engine):
    """Migrate data from SQLite to PostgreSQL."""
    
    # Create sessions
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)
    
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    
    try:
        models = [Student, Faculty, Attendance, RecognitionJob]
        total_migrated = 0
        
        for model in models:
            table_name = model.__tablename__
            
            # Count source records
            source_count = sqlite_session.query(model).count()
            if source_count == 0:
                print(f"[SKIP] {table_name}: No records to migrate")
                continue
            
            print(f"[MIGRATE] {table_name}: Reading {source_count} records...")
            
            # Read all records from SQLite
            records = sqlite_session.query(model).all()
            
            # Insert into PostgreSQL
            for record in records:
                # Create a detached copy for PostgreSQL session
                postgres_session.merge(record)
            
            postgres_session.commit()
            
            # Verify count
            migrated_count = postgres_session.query(model).count()
            if migrated_count >= source_count:
                print(f"[OK] {table_name}: {migrated_count} records migrated")
                total_migrated += migrated_count
            else:
                print(f"[ERROR] {table_name}: Expected {source_count}, got {migrated_count}")
                postgres_session.rollback()
                return False
        
        print(f"\n[SUCCESS] Total {total_migrated} records migrated successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        postgres_session.rollback()
        return False
    finally:
        sqlite_session.close()
        postgres_session.close()


def main():
    parser = argparse.ArgumentParser(
        description="Migrate data from SQLite to PostgreSQL"
    )
    parser.add_argument(
        "--sqlite",
        required=True,
        help="SQLite database URL (e.g., sqlite:///db/database.db)"
    )
    parser.add_argument(
        "--postgres",
        required=True,
        help="PostgreSQL database URL (e.g., postgresql://user:pass@localhost/attendance_db)"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip schema validation (not recommended)"
    )
    
    args = parser.parse_args()
    
    print("[START] Database migration utility")
    print(f"[INFO] Source: {args.sqlite}")
    print(f"[INFO] Target: {args.postgres}")
    print()
    
    # Create connections
    sqlite_engine, postgres_engine = create_connections(args.sqlite, args.postgres)
    if not sqlite_engine or not postgres_engine:
        return 1
    
    # Validate schema
    if not args.skip_validation:
        if not validate_schema(postgres_engine):
            return 1
    
    print()
    
    # Migrate data
    if migrate_data(sqlite_engine, postgres_engine):
        print("\n[DONE] Migration completed successfully!")
        return 0
    else:
        print("\n[DONE] Migration failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
