from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import get_database

app = FastAPI(title="FairDecision AI")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0"}


@app.get("/db-test")
async def db_test():
    db = get_database()
    await db["ping"].insert_one({"created_at": datetime.now(timezone.utc)})
    return {"db": "connected"}
