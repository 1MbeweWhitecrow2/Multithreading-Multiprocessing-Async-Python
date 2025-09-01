import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()  # załaduj DATABASE_URL lub PGHOST/PGUSER itd. z .env

def test_postgres_connection():
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            host = os.getenv("PGHOST", "localhost")
            port = os.getenv("PGPORT", "5432")
            user = os.getenv("PGUSER", "postgres")
            password = os.getenv("PGPASSWORD", "")
            dbname = os.getenv("PGDATABASE", "postgres")
            db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            row = result.fetchone()
            print("✅ Połączenie OK")
            print("Wersja PostgreSQL:", row[0])
    except Exception as e:
        print("❌ Błąd połączenia:", e)

test_postgres_connection()
