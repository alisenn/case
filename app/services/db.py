from pymongo import MongoClient
from app.core.config import settings


_client = MongoClient(settings.MONGODB_URL)
_db = _client[settings.MONGODB_DB_NAME]


def get_logs_collection():
    """
    Returns the MongoDB collection used for task log persistence.
    """
    return _db["task_logs"]
