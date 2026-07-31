import os

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    echo=True,          # Print SQL queries (disable in production)
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()