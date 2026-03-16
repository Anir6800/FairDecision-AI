import os

from dotenv import find_dotenv, load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


load_dotenv(find_dotenv(usecwd=True), override=False)


MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
_client = AsyncIOMotorClient(MONGODB_URI)


def get_database():
    return _client["fairdecision"]


def get_candidates():
    return get_database()["candidates"]


def get_evaluations():
    return get_database()["evaluations"]


def get_jd_collection():
    return get_database()["job_descriptions"]
