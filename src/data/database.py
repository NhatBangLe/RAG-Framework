import os
from enum import Enum

from bson import ObjectId
from pydantic import BaseModel

from ..util.constant import EnvVar
from ..util.error import NotFoundError


class MongoCollection(str, Enum):
    CHAT_MODEL = "chat_model"
    PROMPT = "prompt"
    RECOGNIZER = "recognizer"
    RETRIEVER = "retriever"
    EMBEDDINGS = "embeddings"
    MCP = "mcp"
    AGENT = "agent"
    FILE = "file"


def get_database():
    from ..main import mongodb_client
    db_name = os.getenv(EnvVar.DB_NAME.value)
    return mongodb_client.get_database(db_name)


def get_collection(name: MongoCollection):
    db = get_database()
    return db.get_collection(name.value)


def get_session():
    from ..main import mongodb_client
    session = mongodb_client.start_session()
    yield session
    session.end_session()


async def get_by_id(entity_id: str, collection: MongoCollection, not_found_msg: str | None = None):
    """
    Retrieves a document by its ID from a specified MongoDB collection.

    Args:
        entity_id: The ID of the entity to retrieve.
        collection: The MongoDB collection to search within.
        not_found_msg: An optional custom error message to raise if the entity is not found.

    Returns:
        The retrieved document as a dictionary.

    Raises:
        NotFoundError: If no entity with the given ID is found in the collection.
    """
    c = get_collection(collection)
    document = await c.find_one({"_id": ObjectId(entity_id)})
    if document is None:
        msg = not_found_msg if not_found_msg is not None else f'No entity with id {entity_id} found.'
        raise NotFoundError(msg)
    return document


async def create_document(data: BaseModel, collection: MongoCollection):
    """
    Creates a new document in a specified MongoDB collection.

    Args:
        data: The Pydantic model containing the data for the new document.
        collection: The MongoDB collection where the document will be created.

    Returns:
        The ID of the newly created document.
    """
    c = get_collection(collection)
    created_entity = await c.insert_one(data.model_dump())
    return str(created_entity.inserted_id)


async def update_by_id(entity_id: str, update_data: BaseModel, collection: MongoCollection,
                       not_found_msg: str | None = None):
    """
    Updates an existing document by its ID in a specified MongoDB collection.

    Args:
        entity_id: The ID of the entity to update.
        update_data: The Pydantic model containing the data to update the document with.
        collection: The MongoDB collection where the document will be updated.
        not_found_msg: An optional custom error message to raise if the entity is not found or not modified.

    Raises:
        NotFoundError: If no entity with the given ID is found or if the update operation
            does not modify any document.
    """
    collection = get_collection(collection)
    query_filter = {'_id': ObjectId(entity_id)}
    update_operation = {'$set': update_data.model_dump()}
    result = await collection.update_one(query_filter, update_operation)
    if result.modified_count == 0:
        msg = not_found_msg if not_found_msg is not None else (f'Cannot update prompt entity with id {entity_id}. '
                                                               'Because no prompt entity found.')
        raise NotFoundError(msg)


async def delete_by_id(entity_id: str, collection: MongoCollection, not_found_msg: str | None = None):
    """
    Deletes a document by its ID from a specified MongoDB collection.

    Args:
        entity_id: The ID of the entity to delete.
        collection: The MongoDB collection from which the document will be deleted.
        not_found_msg: An optional custom error message to raise if the entity is not found.

    Raises:
        NotFoundError: If no entity with the given ID is found in the collection.
    """
    c = get_collection(collection)
    result = await c.delete_one({"_id": ObjectId(entity_id)})
    if result.deleted_count == 0:
        msg = not_found_msg if not_found_msg is not None else f'No entity with id {entity_id} found.'
        raise NotFoundError(msg)
