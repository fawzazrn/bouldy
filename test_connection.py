from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/boulder"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print("✅ Connected!")
        print(result.fetchone()[0])
except Exception as e:
    print("❌ Connection failed")
    print(e)