from dataclasses import dataclass
from uuid import UUID
from requests import Session
from api.models.model import DocumentPage
from sqlalchemy import select
from sqlalchemy.orm import Session

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

def create_page_hashes(db: Session, version_id: int, page_hashes: list[str]) -> list[DocumentPage]:
    """Bulk-insert page hashes for a version, in page order (index 0 = page 1)."""
    pages = [
        DocumentPage(version_id=version_id, page_number=i + 1, page_hash=h)
        for i, h in enumerate(page_hashes)
    ]
    db.add_all(pages)
    db.flush()
    return pages

def get_page_hashes_by_version(db: Session, version_id: int) -> list[DocumentPage]:
    stmt = (
        select(DocumentPage)
        .where(DocumentPage.version_id == version_id)
        .order_by(DocumentPage.page_number.asc())
    )
    return list(db.execute(stmt).scalars().all())


def find_documents_by_page_hash(db: Session, page_hash: str) -> list[DocumentPage]:
    """Global reuse check — which versions/pages elsewhere share this exact page content?"""
    stmt = select(DocumentPage).where(DocumentPage.page_hash == page_hash)
    return list(db.execute(stmt).scalars().all())