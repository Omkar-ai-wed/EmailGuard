"""
Quick Supabase connection test.
Run: python test_supabase.py
"""
import sys

try:
    from config import settings
    print(f"✅ Config loaded")
    print(f"   DATABASE_URL: {settings.DATABASE_URL[:55]}...")
except Exception as e:
    print(f"❌ Config load failed: {e}")
    sys.exit(1)

try:
    from sqlalchemy import create_engine, text
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=2,
        max_overflow=2,
    )
    print("✅ Engine created")
except Exception as e:
    print(f"❌ Engine creation failed: {e}")
    sys.exit(1)

try:
    with engine.connect() as conn:
        # Basic connectivity
        row = conn.execute(text("SELECT version()")).fetchone()
        print(f"✅ Connected to Supabase (PostgreSQL)!")
        print(f"   PG Version: {row[0][:60]}")

        # List public tables
        tables = [
            r[0] for r in conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
            )
        ]
        if tables:
            print(f"✅ Public tables found: {tables}")
        else:
            print("⚠️  No tables in public schema yet (run migrations / create_all)")

        # Check current DB user
        db_user = conn.execute(text("SELECT current_user, current_database()")).fetchone()
        print(f"   User: {db_user[0]}  |  Database: {db_user[1]}")

except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

print("\n🎉 Supabase connection is working correctly!")
