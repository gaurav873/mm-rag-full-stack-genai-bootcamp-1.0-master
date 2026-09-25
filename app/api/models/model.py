import enum
from datetime import datetime
from sqlalchemy import Enum
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import func

class Base(DeclarativeBase):
    pass

class EmbeddingStatus(str, enum.Enum):
    pending = "pending"
    embedded = "embedded"
    failed = "failed"
    stale="stale"

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
        DateTime(timezone=True),
        server_default=func.now(),
    )

    versions: Mapped[list["DocumentVersion"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan"
    )
    source_type: Mapped[str] = mapped_column(
    String(20),
    nullable=False,
    index=True
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = (
    UniqueConstraint("document_id", "version_number"),
)
    version_id: Mapped[UUID] = mapped_column(
    PG_UUID(as_uuid=True),
    primary_key=True,
    default=uuid4
    )

    document_id: Mapped[UUID] = mapped_column(
    PG_UUID(as_uuid=True),
    ForeignKey("documents.document_id", ondelete="CASCADE"),
    index=True,
    nullable=False
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    version_number: Mapped[int] = mapped_column(
        Integer
    )

    document_hash: Mapped[str] = mapped_column(
        String(64)
    )
    total_pages: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),

    )
    document_object_key: Mapped[str ] = mapped_column(String(500), nullable=False)
    document: Mapped["Document"] = relationship(
        back_populates="versions",
    )

    pages: Mapped[list["DocumentPage"]] = relationship(
        back_populates="version",
        cascade="all, delete-orphan"
    )
    embedding_status: Mapped[EmbeddingStatus] = mapped_column(
   Enum(EmbeddingStatus, name="embedding_status_enum"), default=EmbeddingStatus.pending, nullable=False)

class DocumentPage(Base):
    __tablename__ = "document_pages"

    __table_args__ = (
    UniqueConstraint("version_id", "page_number"),
    )

    page_id: Mapped[UUID] = mapped_column(
    PG_UUID(as_uuid=True),
    primary_key=True,
    default=uuid4
    )

    version_id: Mapped[UUID] = mapped_column(
    PG_UUID(as_uuid=True),
    ForeignKey("document_versions.version_id", ondelete="CASCADE"),
    index=True,
    nullable=False
    )
    page_object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    page_number: Mapped[int] = mapped_column(
        Integer
    )
    page_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    back_populates="page",cascade="all, delete-orphan"
    )

    version: Mapped["DocumentVersion"] = relationship(
        back_populates="pages"
    )

    images: Mapped[list["DocumentImage"]] = relationship(
        back_populates="page",cascade="all, delete-orphan"
    )
    embedding_status: Mapped[EmbeddingStatus] = mapped_column(
    Enum(EmbeddingStatus, name="embedding_status_enum"), default=EmbeddingStatus.pending, nullable=False)
class DocumentImage(Base):
    __tablename__ = "document_images"

    image_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    document_id: Mapped[UUID] = mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("documents.document_id", ondelete="CASCADE"),
            index=True,
            nullable=False
        )
    
    version_id: Mapped[UUID] = mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("document_versions.version_id", ondelete="CASCADE"),
            index=True,
            nullable=False
        )
    
    page_id: Mapped[UUID] = mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("document_pages.page_id", ondelete="CASCADE"),
            index=True,
            nullable=False
        )
    image_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    image_object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)

    image_ext: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
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
    embedding_status: Mapped[EmbeddingStatus] = mapped_column(
    Enum(EmbeddingStatus, name="embedding_status_enum"),
    default=EmbeddingStatus.pending,
    nullable=False,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    page: Mapped["DocumentPage"] = relationship(
        back_populates="images",
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
        ForeignKey("documents.document_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    table_object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)

    version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("document_versions.version_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    page_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("document_pages.page_id", ondelete="CASCADE"),
        index=True,
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
    table_schema: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Cleaned structured rows
    normalized_data: Mapped[list | dict | None] = mapped_column(JSONB, nullable=True)

    # Search-friendly description
    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # pending / embedded /  failed
    embedding_status: Mapped[EmbeddingStatus] = mapped_column(
    Enum(EmbeddingStatus, name="embedding_status_enum"),
    default=EmbeddingStatus.pending,
    nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    content_hash: Mapped[str] = mapped_column(
    String(64),
    nullable=False,
    index=True
    )


    page: Mapped["DocumentPage"] = relationship(
    back_populates="tables",
    )
