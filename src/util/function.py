import datetime
import os
import uuid
import zipfile
from pathlib import Path

from .constant import DEFAULT_TIMEZONE, EnvVar
from .error import InvalidArgumentError


def get_datetime_now():
    return datetime.datetime.now(DEFAULT_TIMEZONE)


def strict_uuid_parser(uuid_string: str) -> uuid.UUID:
    """
    Strict UUID parser that raises an exception on invalid input.

    Args:
        uuid_string: String representation of UUID

    Returns:
        uuid.UUID object

    Raises:
        InvalidArgumentError: If UUID string is invalid
    """
    try:
        return uuid.UUID(uuid_string)
    except (ValueError, TypeError) as e:
        raise InvalidArgumentError(f"Invalid UUID format: {uuid_string}") from e


def zip_folder(folder_path: str | os.PathLike[str], output_path: str | os.PathLike[str]):
    """
    Zip a folder
    :param folder_path: Path to a folder which needs to archive
    :param output_path: Path to the zip output file
    """
    folder = Path(folder_path)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in folder.rglob('*'):
            if file_path.is_file():
                zipf.write(file_path, file_path.relative_to(folder))


def get_cache_dir_path():
    return os.getenv(EnvVar.CACHES_DIR.value, "/app/cache")
