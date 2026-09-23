import logging
from pathlib import Path
import uuid
from typing import Annotated
from fastapi import APIRouter, UploadFile, File,Depends, HTTPException
from api.configs.document_format import Validate_Document_Format
from api.validation.document_validation import DocumentValidator 
from api.utility.utitlity_fucntion import read_file_contents, compute_file_hash, check_existing_document

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
    validator = DocumentValidator()
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    for file in files:
        is_valid, error = validator.validate_extension(file.filename)
        if not is_valid:
            failed_files.append({"filename": file.filename, "reason": error})
            continue

        is_valid, error = validator.validate_size(contents)
        if not is_valid:
            failed_files.append({"filename": file.filename, "reason": error})
            continue
        contents = read_file_contents(file) # reading file contents
        file_hash = compute_file_hash(contents)
        status, existing_doc, latest_version = check_existing_document(
            db, file.filename, file_hash
        )
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

























