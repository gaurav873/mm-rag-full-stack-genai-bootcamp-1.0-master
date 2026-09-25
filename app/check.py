from api.configs.settings import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM document_pages"))
    for row in result:
        print(row)