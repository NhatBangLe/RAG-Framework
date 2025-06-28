import os
from enum import Enum

DB_URI = "MONGODB_URI"
DB_NAME = "MONGODB_DATABASE"


class MongoCollection(Enum):
    CHAT_MODEL = "chat_model"
    PROMPT = "prompt"
    RECOGNIZER = "recognizer"
    RETRIEVER = "retriever"
    EMBEDDINGS = "embeddings"


def get_database():
    from ..main import mongodb_client
    db_name = os.getenv(DB_NAME)
    return mongodb_client.get_database(db_name)


def get_collection(name: MongoCollection):
    db = get_database()
    return db.get_collection(name.value)


def get_session():
    from ..main import mongodb_client
    session = mongodb_client.start_session()
    yield session
    session.end_session()
