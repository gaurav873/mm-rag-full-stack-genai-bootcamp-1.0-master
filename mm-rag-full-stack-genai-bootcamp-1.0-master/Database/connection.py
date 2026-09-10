from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict

def get_connection():
    engine = create_engine("postgresql+psycopg2://postgres:9871@localhost:5432/Rag-Project", echo=True)
    return engine

if __name__ == "__main__":

    try:
        engine = get_connection()
        print(f"Connection to the Postgres for user  created successfully.")

    except Exception as ex:
        print("Connection could not be made due to the following error:\n", ex)
# SessionLocal = sessionmaker(
#     bind=engine,
#     autocommit=False,
#     autoflush=False,uv uv
# 