import base64
import hashlib
import hmac
import math
import secrets
import time
from os import PathLike
from typing import TypedDict, Self, Callable, Any

from pydantic import BaseModel, Field
from pymongo.asynchronous.collection import AsyncCollection

from src.util.constant import DEFAULT_CHARSET, DEFAULT_TOKEN_SEPARATOR
from src.util.error import InvalidArgumentError


class FileInformation(TypedDict):
    """File information dictionary"""
    name: str
    mime_type: str
    path: str | PathLike[str]


class SecureDownloadGenerator:
    """Generate secure, time-limited download links"""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode(DEFAULT_CHARSET)

    def generate_token(self, data: FileInformation, expires_in: int = 3600, user_id: str | None = None) -> str:
        """Generate a secure token for file download."""
        expiry = int(time.time()) + expires_in
        nonce = secrets.token_urlsafe(16)

        # Include user_id in the payload if provided
        payload_parts = [data["name"], str(data["path"]), data["mime_type"], str(expiry), nonce]
        if user_id:
            payload_parts.append(user_id)
        payload = DEFAULT_TOKEN_SEPARATOR.join(payload_parts)

        # Create signature
        signature = hmac.new(
            self.secret_key,
            payload.encode(DEFAULT_CHARSET),
            hashlib.sha256
        ).hexdigest()

        # Combine payload and signature
        token_data = f"{payload}{DEFAULT_TOKEN_SEPARATOR}{signature}"

        # Base64 encode for URL safety
        token = base64.urlsafe_b64encode(token_data.encode(DEFAULT_CHARSET)).decode(DEFAULT_CHARSET)
        return token

    def verify_token(self, token: str) -> FileInformation | None:
        """Verify a download token and return a file id."""
        # Decode base64
        try:
            token_data: str = base64.urlsafe_b64decode(token.encode(DEFAULT_CHARSET)).decode(DEFAULT_CHARSET)
        except Exception:
            raise InvalidArgumentError("Invalid token")

        # Split token parts
        parts: list[str] = token_data.split(DEFAULT_TOKEN_SEPARATOR)
        if len(parts) < 5:
            return None

        # Extract parts
        name, path, mime_type, expiry_str, nonce = parts[:5]

        # Check expiration
        expiry = int(expiry_str)
        if time.time() > expiry:
            return None

        # Check if user_id is included
        if len(parts) == 7:
            user_id = parts[5]
            signature = parts[6]
            payload = DEFAULT_TOKEN_SEPARATOR.join([name, path, mime_type, expiry_str, nonce, user_id])
        else:
            signature = parts[5]
            payload = DEFAULT_TOKEN_SEPARATOR.join([name, path, mime_type, expiry_str, nonce])

        # Verify signature
        expected_signature = hmac.new(
            self.secret_key,
            payload.encode(DEFAULT_CHARSET),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return None

        return FileInformation(
            name=name,
            mime_type=mime_type,
            path=path,
        )


class Progress(TypedDict):
    """
    A dictionary representing the progress of an operation.
    """
    status: str
    percentage: float


class PagingParams(BaseModel):
    offset: int = Field(description="The page number.", default=0, ge=0)
    limit: int = Field(description="The page size.", default=10, gt=0, le=100)


class PagingWrapper[T](BaseModel):
    """
    The `PagingWrapper` class provides a standardized structure for encapsulating
    paginated results from an API or database query. It inherits from `BaseModel`
    for data validation and serialization and uses `Generic[T]` to allow for
    flexible content types.
    """

    content: list[T] = Field(description="Return content")
    first: bool | None = Field(default=None, description="Whether this is a first page.")
    last: bool | None = Field(default=None, description="Whether this is a last page.")
    page_number: int = Field(description="The page number.")
    page_size: int = Field(description="The page size.")
    total_elements: int | None = Field(default=None, description="The total number of elements in database.")
    total_pages: int | None = Field(default=None,
                                    description="The total number of pages in database if use `page_size`.")

    @classmethod
    async def get_paging(
            cls,
            params: PagingParams,
            collection: AsyncCollection,
            map_func: Callable[[dict[str, Any]], T],
            *args
    ):
        total_elements = await collection.count_documents({})
        total_pages = math.ceil(total_elements / params.limit)
        results = collection.find(*args).limit(params.limit).skip(params.limit * params.offset)
        content = []
        async for r in results:
            record = dict(r)
            if "_id" in record:
                record["id"] = str(record["_id"])
                del record["_id"]
            content.append(map_func(record))

        return cls(
            content=content,
            first=params.offset == 0,
            last=params.offset == max(total_pages - 1, 0),
            total_elements=total_elements,
            total_pages=total_pages,
            page_number=params.offset,
            page_size=params.limit,
        )

    @classmethod
    def convert_content_type[T, D](cls, data: Self, map_func: Callable[[T], D]):
        new_content = [map_func(d) for d in data.content]
        return cls(
            content=new_content,
            first=data.first,
            last=data.last,
            total_elements=data.total_elements,
            total_pages=data.total_pages,
            page_number=data.page_number,
            page_size=data.page_size,
        )
