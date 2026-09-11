from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func

class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    document_id: Mapped[UUID] = mapped_column(
    PG_UUID(as_uuid=True),
    primary_key=True,
    default=uuid4
    )
    filename: Mapped[str] = mapped_column(
        String(255)
    )

    current_version: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    versions: Mapped[list["DocumentVersion"]] = relationship(
        back_populates="document"
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    version_id: Mapped[UUID] = mapped_column(
    PG_UUID(as_uuid=True),
    primary_key=True,
    default=uuid4
    )

    document_id: Mapped[UUID] = mapped_column(
    PG_UUID(as_uuid=True),
    ForeignKey("documents.document_id"),
    nullable=False
    )

    version_number: Mapped[int] = mapped_column(
        Integer
    )

    document_hash: Mapped[str] = mapped_column(
        String(64)
    )
    total_pages: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    document: Mapped["Document"] = relationship(
        back_populates="versions"
    )

    pages: Mapped[list["DocumentPage"]] = relationship(
        back_populates="version"
    )

class DocumentPage(Base):
    __tablename__ = "document_pages"

    page_id: Mapped[UUID] = mapped_column(
    PG_UUID(as_uuid=True),
    primary_key=True,
    default=uuid4
    )

    version_id: Mapped[UUID] = mapped_column(
    PG_UUID(as_uuid=True),
    ForeignKey("document_versions.version_id"),
    nullable=False
    )

    page_number: Mapped[int] = mapped_column(
        Integer
    )

    page_hash: Mapped[str] = mapped_column(
        String(64)
    )

    image_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    table_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    has_ocr: Mapped[bool] = mapped_column(
        default=False
    )
    tables: Mapped[list["DocumentTable"]] = relationship(
    back_populates="page"
    )

    version: Mapped["DocumentVersion"] = relationship(
        back_populates="pages"
    )

    images: Mapped[list["DocumentImage"]] = relationship(
        back_populates="page"
    )
class DocumentImage(Base):
    __tablename__ = "document_images"

    image_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    page_id: Mapped[int] = mapped_column(
        ForeignKey("document_pages.page_id"),
        nullable=False
    )

    image_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    object_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    image_ext: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    image_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    ocr_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    vision_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    surrounding_context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    embedding_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )

    page: Mapped["DocumentPage"] = relationship(
        back_populates="images"
    )
class DocumentTable(Base):
    __tablename__ = "document_tables"

    table_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    document_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.document_id"),
        nullable=False
    )

    version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("document_versions.version_id"),
        nullable=False
    )

    page_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("document_pages.page_id"),
        nullable=False
    )

    table_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    surrounding_context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Complete table extracted from the PDF
    raw_content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Table structure: columns, types, etc.
    schema: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )

    # Cleaned structured rows
    normalized_data: Mapped[list | dict] = mapped_column(
        JSONB,
        nullable=False
    )

    # Search-friendly description
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # pending / embedded / stale / failed
    embedding_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    page: Mapped["DocumentPage"] = relationship(
    back_populates="tables"
    )