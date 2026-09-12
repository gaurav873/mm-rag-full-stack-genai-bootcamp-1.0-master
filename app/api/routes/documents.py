import logging
from pathlib import Path
import uuid
from typing import Annotated
from fastapi import APIRouter, UploadFile, File,Depends, HTTPException
from api.configs.document_format import Validate_Document_Format
from api.validation.document_validation import DocumentValidator 

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = Path("/workspaces/mm-rag-full-stack-genai-bootcamp-1.0-master/upload")
UPLOAD_DIR.mkdir(exist_ok=True)

# ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".docx"}
# MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload")
async def upload_files(files: Annotated[list[UploadFile], File(...)]):
    '''
    It handles the upload of multiple files, 
    validates their extensions and sizes, 
    saves them to a specified directory, and 
    returns a summary of the upload process, 
    including any failed uploads with reasons.
    '''
    uploaded_files = []
    failed_files = []
    validator = DocumentValidator(document_config)
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    for file in files:
        is_valid, error = validator.validate_extension(file.filename)
        if not is_valid:
            failed_files.append({"filename": file.filename, "reason": error})
            continue

        contents = await file.read()
        is_valid, error = validator.validate_size(contents)
        if not is_valid:
            failed_files.append({"filename": file.filename, "reason": error})
            continue

        uploaded_files.append({"filename": file.filename, "contents": contents})

    # Case 1: every single file failed validation
    if not uploaded_files and failed_files:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "All files failed validation",
                "failed": failed_files,
            },
        )

    # Case 2: some passed, some failed — partial success
    if failed_files:
        return {
            "message": f"{len(uploaded_files)} file(s) uploaded, {len(failed_files)} failed validation",
            "uploaded": [f["filename"] for f in uploaded_files],
            "failed": failed_files,
        }
    # Case 3: everything passed
    
    return {
        "message": f"All {len(uploaded_files)} file(s) uploaded successfully",
        "uploaded": [f["filename"] for f in uploaded_files],
    }


























    document_json_format=Validate_Document_Format()
    max_size_mb = document_json_format["document"].max_size_mb
    max_size_bytes = max_size_mb * 1024 * 1024

    for file in files:
        # Validate extension
        ext = Path(file.filename).suffix.lower()
        allowed_extensions = document_json_format['document'].extensions
        if ext not in allowed_extensions:
            failed_files.append({
                "filename": file.filename,
                "reason": f"File type '{ext}' not allowed"
            })
            continue

        # Read file
        contents = await file.read()

        # Validate size
        if len(contents) > max_size_bytes:
            failed_files.append({
                "filename": file.filename,
                "reason": f"File too large. Max {max_size_mb}MB"
            })
            continue

        # Create UUID
        document_id = uuid.uuid4()

        # Save file
        unique_name = f"{document_id}_{file.filename}"
        save_path = UPLOAD_DIR / unique_name
        print(f"Saving file to {save_path},unique_name={unique_name},document_id={document_id}")
        with open(save_path, "wb") as f:
            f.write(contents)

        uploaded_files.append({
            "document_id": str(document_id),
            "filename": file.filename,
            "size": len(contents),
            "content_type": file.content_type
        })

    return {
        "message": "Upload completed",
        "uploaded": uploaded_files,
        "failed": failed_files
    }
