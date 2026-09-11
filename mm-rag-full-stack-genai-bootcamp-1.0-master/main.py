from fastapi import FastAPI
from api.routes.documents import router

app = FastAPI(
    title="Multimodal RAG API",
    version="1.0.0",
    openapi_version="3.0.2",

)

app.include_router(router, prefix="/api", tags=["uploads"])
@app.get("/")
def root():
    return {"message": "API is running"}