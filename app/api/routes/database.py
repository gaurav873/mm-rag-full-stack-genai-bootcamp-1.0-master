# api/database.py
from sqlalchemy.orm import sessionmaker, Session
from api.configs.settings import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()