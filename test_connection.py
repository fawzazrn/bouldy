from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_sx3eHVujr5ZS@ep-purple-fire-azzsq5pl.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print("✅ Connected!")
        print(result.fetchone()[0])
except Exception as e:
    print("❌ Connection failed")
    print(e)