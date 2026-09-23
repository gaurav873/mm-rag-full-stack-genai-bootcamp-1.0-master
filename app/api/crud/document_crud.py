from sqlalchemy import select
from sqlalchemy.orm import Session


from api.models.model import Document, DocumentVersion, PageHash


# # ---------- Document ----------
# def save_uploaded_document(
#     db: Session,
#     filename: str,
#     contents: bytes,
#     file_hash: str,
#     page_hashes: list[str],
#     storage_path: str,
#     check_result: dict,
#     owner_id: int | None = None,  # if you've added auth/ownership
# ) -> dict:
#     """
#     Persist an uploaded file based on the outcome of check_existing_document.
#     Assumes the file bytes have ALREADY been written to `storage_path` on disk
#     (or object storage) before this is called — this function only touches the DB.
#     """
#     status = check_result["status"]

#     if status == "duplicate":
#         # nothing to save — it's identical to something that already exists
#         return {
#             "status": "duplicate",
#             "document_id": check_result["document_id"],
#             "version": check_result["matched_version"],
#         }

#     if status == "new_version":
#         document_id = check_result["document_id"]
#         version = create_version(
#             db,
#             document_id=document_id,
#             document_hash=file_hash,
#             storage_path=storage_path,
#         )
#         create_page_hashes(db, version_id=version.version_id, page_hashes=page_hashes)

#         return {
#             "status": "new_version",
#             "document_id": document_id,
#             "version": version,
#         }

#     # status == "new"
#     document = create_document(db, filename=filename, owner_id=owner_id)
#     version = create_version(
#         db,
#         document_id=document.document_id,
#         document_hash=file_hash,
#         storage_path=storage_path,
#     )
#     create_page_hashes(db, version_id=version.version_id, page_hashes=page_hashes)

#     return {
#         "status": "new",
#         "document_id": document.document_id,
#         "version": version,
#     }

def create_document(
    db: Session,
    filename: str,
    source_type: str,
) -> Document:
    """Create a bare Document (no version/pages yet)."""
    document = Document(
        filename=filename,
        source_type=source_type,
        current_version=0,  # bumped to 1 once the first version is created
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

def get_document_by_id(db: Session, document_id: int) -> Document | None:
    return db.get(Document, document_id)


def get_document_by_filename(db: Session, filename: str) -> Document | None:
    stmt = select(Document).where(Document.filename == filename)
    return db.execute(stmt).scalar_one_or_none()


def list_documents(db: Session, skip: int = 0, limit: int = 50) -> list[Document]:
    stmt = select(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def delete_document(db: Session, document_id: int) -> bool:
    """Deletes the document and relies on cascade to remove versions/pages."""
    document = db.get(Document, document_id)
    if document is None:
        return False
    db.delete(document)
    db.flush()
    return True


# ---------- DocumentVersion ----------


# ---------- PageHash ----------

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