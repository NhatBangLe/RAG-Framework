import datetime

__all__ = ['DEFAULT_TIMEZONE', 'DEFAULT_CHARSET', 'DEFAULT_TOKEN_SEPARATOR',
           "SUPPORTED_DOCUMENT_TYPE_DICT", "SUPPORTED_LANGUAGE_DICT", "EnvVar"]

from enum import Enum

DEFAULT_TIMEZONE = datetime.timezone.utc
DEFAULT_CHARSET = "utf-8"
DEFAULT_TOKEN_SEPARATOR = "::"
SUPPORTED_DOCUMENT_TYPE_DICT = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt"
}
SUPPORTED_LANGUAGE_DICT = {
    "vi": "Vietnamese",
    "en": "English"
}


class EnvVar(str, Enum):
    LOCAL_FILE_DIR = "LOCAL_FILE_DIR"
    DOWNLOAD_SECURE_KEY = "DOWNLOAD_SECURE_KEY"
    DB_URI = "MONGODB_URI"
    DB_NAME = "MONGODB_DATABASE"
