# crud_controller.py
from uuid import UUID
from sqlalchemy.orm import Session

from api.crud.document_images import ImageInput, create_document_image
from api.crud.document_table import TableInput
from document_crud import create_document
from document_version_crud import create_document_version
from document_page_crud import create_document_pages, PageInput
from document_images import create_document_image
from document_table import create_document_table

def document_creation_controller(
    db: Session,
    filename: str,
    source_type: str,
    document_hash: str,
    pages: list[PageInput],
    images: list[ImageInput] | None = None,
    tables: list[TableInput] | None = None,
) -> dict:
    """
    Orchestrates full document ingestion:
    Document -> DocumentVersion -> DocumentPages -> DocumentImages/DocumentTables,
    as a single atomic transaction.
    """
    images = images or []
    tables = tables or []

    try:
        document = create_document(
            db,
            filename=filename,
            source_type=source_type,
        )

        version = create_document_version(
            db,
            document_id=document.document_id,
            document_hash=document_hash,
            total_pages=len(pages),
        )

        created_pages = create_document_pages(
            db,
            version_id=version.version_id,
            pages=pages,
        )

        # map page_number -> page_id, so images/tables can be linked to the right page
        page_id_by_number = {p.page_number: p.page_id for p in created_pages}

        created_images = []
        if images:
            images_by_page: dict[int, list[ImageInput]] = {}
            for img in images:
                images_by_page.setdefault(img.page_number, []).append(img)

            for page_number, page_images in images_by_page.items():
                if page_number not in page_id_by_number:
                    raise ValueError(
                        f"image references page_number={page_number}, "
                        f"which does not exist in the provided pages"
                    )
                created_images.extend(
                    create_document_image(
                        db,
                        document_id=document.document_id,
                        version_id=version.version_id,
                        page_id=page_id_by_number[page_number],
                        images=page_images,
                    )
                )

        created_tables = []
        if tables:
            tables_by_page: dict[int, list[TableInput]] = {}
            for tbl in tables:
                tables_by_page.setdefault(tbl.page_number, []).append(tbl)

            for page_number, page_tables in tables_by_page.items():
                if page_number not in page_id_by_number:
                    raise ValueError(
                        f"table references page_number={page_number}, "
                        f"which does not exist in the provided pages"
                    )
                created_tables.extend(
                    create_document_table(
                        db,
                        document_id=document.document_id,
                        version_id=version.version_id,
                        page_id=page_id_by_number[page_number],
                        tables=page_tables,
                    )
                )

        db.commit()  # single commit — everything lands together, or nothing does

    except Exception:
        db.rollback()
        raise

    db.refresh(document)
    db.refresh(version)

    return {
        "document": document,
        "version": version,
        "pages": created_pages,
        "images": created_images,
        "tables": created_tables,
    }