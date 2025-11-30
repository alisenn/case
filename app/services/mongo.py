from pymongo import MongoClient
from app.core.config import settings

_client = None
_db = None


def _get_client():
    global _client, _db
    if _client is None:
        _client = MongoClient(settings.MONGODB_URL, maxPoolSize=50)
        _db = _client[settings.MONGODB_DB_NAME]
    return _client


def get_logs_collection():
    """
    Returns the MongoDB collection used for task log persistence.
    Lazily initializes the client to avoid fork-safety issues on import.
    """
    if _db is None:
        _get_client()
    return _db["task_logs"]
