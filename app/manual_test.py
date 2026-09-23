# manual_test.py
from sqlalchemy.orm import sessionmaker
from api.configs.settings import engine  # or wherever your `engine` variable lives now (from pydantic_settings file)

from api.crud.crud_controller import document_creation_controller  # adjust path to your actual file
from api.page_service import PageInput                          # adjust path to your actual file

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

result = document_creation_controller(
    db=db,
    filename="test.pdf",
    source_type="upload",
    document_hash="abc123",
    pages=[
        PageInput(page_number=1, page_hash="p1hash"),
        PageInput(page_number=2, page_hash="p2hash", has_ocr=True),
    ],
)

print("Document ID:", result["document"].document_id)
print("Version ID:", result["version"].version_id)
print("Pages created:", len(result["pages"]))

db.close()