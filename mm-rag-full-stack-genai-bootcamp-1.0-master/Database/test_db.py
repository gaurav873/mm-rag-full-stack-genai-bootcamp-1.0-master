from connection import engine
from sqlalchemy import text


with engine.connect() as connection:
    result = connection.execute(text("SELECT 1"))