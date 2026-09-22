from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from .models import Document, DocumentVersion, PageHash

def create_page_hashes(db: Session, version_id: int, page_hashes: list[str]) -> list[PageHash]:
    """Bulk-insert page hashes for a version, in page order (index 0 = page 1)."""
    pages = [
        PageHash(version_id=version_id, page_number=i + 1, page_hash=h)
        for i, h in enumerate(page_hashes)
    ]
    db.add_all(pages)
    db.flush()
    return pages


def get_page_hashes_by_version(db: Session, version_id: int) -> list[PageHash]:
    stmt = (
        select(PageHash)
        .where(PageHash.version_id == version_id)
        .order_by(PageHash.page_number.asc())
    )
    return list(db.execute(stmt).scalars().all())


def find_documents_by_page_hash(db: Session, page_hash: str) -> list[PageHash]:
    """Global reuse check — which versions/pages elsewhere share this exact page content?"""
    stmt = select(PageHash).where(PageHash.page_hash == page_hash)
    return list(db.execute(stmt).scalars().all())