from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from api.models.model import Document, DocumentVersion, PageHash

def create_document_version(
    db: Session,
    document_id: UUID,
    document_hash: str,
    total_pages: int,
) -> DocumentVersion:
    """
    Create a new DocumentVersion for an existing Document.
    Auto-increments version_number based on existing versions,
    and updates Document.current_version to match.
    """
    document = db.get(Document, document_id)
    if document is None:
        raise ValueError(f"Document {document_id} not found")

    next_version_number = document.current_version + 1

    version = DocumentVersion(
        document_id=document_id,
        version_number=next_version_number,
        document_hash=document_hash,
        total_pages=total_pages,
    )
    db.add(version)

    document.current_version = next_version_number

    db.commit()
    db.refresh(version)
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
