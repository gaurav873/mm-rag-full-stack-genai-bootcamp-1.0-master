from dataclasses import dataclass
from uuid import UUID
from requests import Session
from api.models.model import DocumentPage

@dataclass
class PageInput:
    page_number: int
    page_hash: str
    image_count: int = 0
    table_count: int = 0
    has_ocr: bool = False


def create_document_pages(
    db: Session,
    version_id: UUID,
    pages: list[PageInput],
) -> list[DocumentPage]:
    """Bulk-create multiple DocumentPages under a given version, in one transaction."""
    page_objs = [
        DocumentPage(
            version_id=version_id,
            page_number=p.page_number,
            page_hash=p.page_hash,
            image_count=p.image_count,
            table_count=p.table_count,
            has_ocr=p.has_ocr,
        )
        for p in pages
    ]
    db.add_all(page_objs)
    db.commit()
    for page in page_objs:
        db.refresh(page)
    return page_objs
