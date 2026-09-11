from fastapi import FastAPI
from fastapi import APIRouter, UploadFile, File

app = FastAPI(
    title="Multimodal RAG API",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}



router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "content_type": file.content_type
    }
app.include_router(router)