# api/services/documents.py
import hashlib
from fastapi import UploadFile
from sqlalchemy.orm import Session

from api.crud.documents import get_document_by_filename, get_latest_version
from api.models.model import Document, DocumentVersion


async def read_file_contents(file: UploadFile) -> bytes:
    """Read the full contents of an uploaded file."""
    return await file.read()


def compute_file_hash(contents: bytes) -> str:
    """Compute a SHA-256 hash of file contents."""
    return hashlib.sha256(contents).hexdigest()


def check_existing_document(
    db: Session, filename: str, file_hash: str
) -> tuple[str, Document | None, DocumentVersion | None]:
    """
    Check the database for an existing document with this filename,
    and determine whether this upload is new, a new version, or a duplicate.

    Returns: (status, existing_document, latest_version)
    status is one of: "new", "new_version", "duplicate"
    """
    existing_document = get_document_by_filename(db, filename)

    if existing_document is None:
        return "new", None, None

    latest_version = get_latest_version(db, existing_document.document_id)

    if latest_version and latest_version.document_hash == file_hash:
        return "duplicate", existing_document, latest_version

    return "new_version", existing_document, latest_version