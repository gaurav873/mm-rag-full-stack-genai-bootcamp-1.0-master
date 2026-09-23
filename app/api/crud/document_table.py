from dataclasses import dataclass
from uuid import UUID
from requests import Session
from api.models.model import DocumentTable, EmbeddingStatus


@dataclass
class TableInput:
    page_number: int          # which page this table belongs to
    table_number: int
    raw_content: str
    table_schema: dict
    normalized_data: list | dict
    content_hash: str
    title: str | None = None
    surrounding_context: str | None = None
    summary: str | None = None

def create_document_table(
    db: Session,
    document_id: UUID,
    version_id: UUID,
    page_id: UUID,
    table_number: int,
    raw_content: str,
    table_schema: dict,
    normalized_data: list | dict,
    content_hash: str,
    title: str | None = None,
    surrounding_context: str | None = None,
    summary: str | None = None,
) -> DocumentTable:
    """Create a DocumentTable record for a page."""
    table = DocumentTable(
        document_id=document_id,
        version_id=version_id,
        page_id=page_id,
        table_number=table_number,
        raw_content=raw_content,
        table_schema=table_schema,
        normalized_data=normalized_data,
        content_hash=content_hash,
        title=title,
        surrounding_context=surrounding_context,
        summary=summary,
        embedding_status=EmbeddingStatus.pending,
    )
    db.add(table)
    db.commit()
    db.refresh(table)
    return table