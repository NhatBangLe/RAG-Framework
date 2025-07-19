import os
from typing import Annotated

from fastapi import Depends, Query
from pymongo.asynchronous.client_session import AsyncClientSession

from .data.database import get_session
from .util import SecureDownloadGenerator, PagingParams
from .util.constant import EnvVar


def provide_download_generator():
    secret_key = os.getenv(EnvVar.DOWNLOAD_SECURE_KEY.value, "SUPER_SECRET_DEFAULT_KEY")
    return SecureDownloadGenerator(secret_key)


SessionDep = Annotated[AsyncClientSession, Depends(get_session)]
DownloadGeneratorDep = Annotated[SecureDownloadGenerator, Depends(provide_download_generator)]
PagingQuery = Annotated[PagingParams, Query()]
