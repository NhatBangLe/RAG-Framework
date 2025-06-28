import datetime

__all__ = ['DEFAULT_TIMEZONE', 'DEFAULT_CHARSET', 'DEFAULT_TOKEN_SEPARATOR',
           "SUPPORTED_DOCUMENT_TYPE_DICT", "SUPPORTED_LANGUAGE_DICT"]

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
