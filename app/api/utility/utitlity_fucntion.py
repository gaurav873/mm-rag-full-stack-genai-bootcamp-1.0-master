# api/services/documents.py
import hashlib
from io import BytesIO
from fastapi import UploadFile
from sqlalchemy.orm import Session
from pypdf import PdfReader, PdfWriter

from api.crud.documents import get_document_by_filename, get_latest_version
from api.models.model import Document, DocumentVersion


async def read_file_contents(file: UploadFile) -> bytes:
    """Read the full contents of an uploaded file."""
    return await file.read()


def compute_file_hash(contents: bytes) -> str:
    """Compute a SHA-256 hash of file contents."""
    return hashlib.sha256(contents).hexdigest()
def extract_and_hash_pages(contents: bytes) -> list[str]:
    """
    Split a PDF's bytes into individual pages and return a SHA-256 hash
    for each page's raw content, in page order (index 0 = page 1).
    """
    reader = PdfReader(BytesIO(contents))
    page_hashes = []

    for page in reader.pages:
        writer = PdfWriter()
        writer.add_page(page)

        buffer = BytesIO()
        writer.write(buffer)
        page_bytes = buffer.getvalue()

        page_hash = hashlib.sha256(page_bytes).hexdigest()
        page_hashes.append(page_hash)

    return page_hashes

from collections import Counter

def check_existing_document(
    db: Session,
    file_hash: str,
    page_hashes: list[str],
    overlap_threshold: float = 0.5,  # tune this: 50%+ shared pages = "same document family"
) -> dict:
    """
    Determine whether an uploaded file is:
      - "duplicate"    -> exact document_hash match already exists
      - "new_version"  -> no exact match, but pages overlap strongly with an existing document
      - "new"          -> no meaningful page overlap with anything

    Returns a dict with status, matched document/version, and match details.
    """

    # Step 1: exact whole-document match (fast path, no need to look at pages)
    existing_version = get_version_by_hash(db, file_hash)
    if existing_version:
        return {
            "status": "duplicate",
            "document_id": existing_version.document_id,
            "matched_version": existing_version,
        }

    # Step 2: no exact match -> check page-level overlap against ALL existing pages
    if not page_hashes:
        return {"status": "new", "document_id": None, "matched_version": None}

    matches = find_documents_by_page_hashes(db, page_hashes)  # see below
    if not matches:
        return {"status": "new", "document_id": None, "matched_version": None}

    # Step 3: group matches by document_id, count how many pages overlap with each
    doc_overlap_counts = Counter(m.document_id for m in matches)
    best_document_id, matched_page_count = doc_overlap_counts.most_common(1)[0]

    overlap_ratio = matched_page_count / len(page_hashes)

    if overlap_ratio >= overlap_threshold:
        latest_version = get_latest_version(db, best_document_id)
        return {
            "status": "new_version",
            "document_id": best_document_id,
            "matched_version": latest_version,
            "overlap_ratio": overlap_ratio,
            "matched_pages": matched_page_count,
        }

    # overlap exists but too weak to call it "the same document"
    return {
        "status": "new",
        "document_id": None,
        "matched_version": None,
        "overlap_ratio": overlap_ratio,
    }