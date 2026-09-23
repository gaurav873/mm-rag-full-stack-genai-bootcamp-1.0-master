from uuid import UUID
from attr import dataclass
from requests import Session
from app.api.models.model import DocumentImage, EmbeddingStatus

@dataclass
class ImageInput:
    page_number: int          # which page this image belongs to (matched by number, not ID)
    image_number: int
    object_key: str
    image_ext: str
    image_hash: str
    title: str | None = None
    ocr_text: str | None = None
    vision_summary: str | None = None
    surrounding_context: str | None = None


def create_document_image(
    db: Session,
    document_id: UUID,
    version_id: UUID,
    page_id: UUID,
    image_number: int,
    object_key: str,
    image_ext: str,
    image_hash: str,
    title: str | None = None,
    ocr_text: str | None = None,
    vision_summary: str | None = None,
    surrounding_context: str | None = None,
) -> DocumentImage:
    """Create a DocumentImage record for a page."""
    image = DocumentImage(
        document_id=document_id,
        version_id=version_id,
        page_id=page_id,
        image_number=image_number,
        object_key=object_key,
        image_ext=image_ext,
        image_hash=image_hash,
        title=title,
        ocr_text=ocr_text,
        vision_summary=vision_summary,
        surrounding_context=surrounding_context,
        embedding_status=EmbeddingStatus.pending,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image