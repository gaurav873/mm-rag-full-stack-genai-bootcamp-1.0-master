from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from .models import Document, DocumentVersion, PageHash
def create_version(
    db: Session,
    document_id: int,
    document_hash: str,
    storage_path: str,
) -> DocumentVersion:
    """Create a new version under an existing document, auto-incrementing version_number."""
    last = get_latest_version(db, document_id)
    next_version_number = (last.version_number + 1) if last else 1

    version = DocumentVersion(
        document_id=document_id,
        version_number=next_version_number,
        document_hash=document_hash,
        storage_path=storage_path,
        created_at=datetime.now(timezone.utc),
    )
    db.add(version)
    db.flush()
    return version


def get_latest_version(db: Session, document_id: int) -> DocumentVersion | None:
    stmt = (
        select(DocumentVersion)
        .where(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.version_number.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def get_all_versions(db: Session, document_id: int) -> list[DocumentVersion]:
    stmt = (
        select(DocumentVersion)
        .where(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.version_number.asc())
    )
    return list(db.execute(stmt).scalars().all())


def get_version_by_hash(db: Session, document_hash: str) -> DocumentVersion | None:
    """Global lookup — is this exact file content stored anywhere, under any document?"""
    stmt = select(DocumentVersion).where(DocumentVersion.document_hash == document_hash)
    return db.execute(stmt).scalar_one_or_none()


def delete_version(db: Session, version_id: int) -> bool:
    version = db.get(DocumentVersion, version_id)
    if version is None:
        return False
    db.delete(version)
    db.flush()
    return True
