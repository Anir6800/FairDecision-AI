from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import get_database
from app.routes.bias import router as bias_router
from app.routes.evaluate import router as evaluate_router
from app.routes.upload import UPLOAD_DIR, router as upload_router

app = FastAPI(title="FairDecision AI")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api")
app.include_router(evaluate_router, prefix="/api")
app.include_router(bias_router, prefix="/api")


@app.on_event("startup")
async def create_upload_dir() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0"}


@app.get("/db-test")
async def db_test():
    db = get_database()
    await db["ping"].insert_one({"created_at": datetime.now(timezone.utc)})
    return {"db": "connected"}
