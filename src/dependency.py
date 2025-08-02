import os
from typing import Annotated

from fastapi import Depends, Query
from pymongo.asynchronous.client_session import AsyncClientSession

from .data.database import get_session
from .data.function.agent import IAgentService, AgentServiceImpl
from .data.function.chat_model import IChatModelService, ChatModelServiceImpl
from .data.function.embeddings import IEmbeddingsService, EmbeddingsServiceImpl
from .data.function.file import IFileService, FileServiceImpl
from .data.function.mcp import IMCPService, MCPServiceImpl
from .data.function.prompt import IPromptService, PromptServiceImpl
from .data.function.recognizer import IRecognizerService, RecognizerServiceImpl
from .data.function.retriever import IRetrieverService, RetrieverServiceImpl
from .data.function.tool import IToolService, ToolServiceImpl
from .util import SecureDownloadGenerator, PagingParams
from .util.constant import EnvVar


def provide_download_generator():
    secret_key = os.getenv(EnvVar.DOWNLOAD_SECURE_KEY.value, "SUPER_SECRET_DEFAULT_KEY")
    return SecureDownloadGenerator(secret_key)


def provide_chat_model_service() -> IChatModelService:
    return ChatModelServiceImpl()


def provide_file_service() -> IFileService:
    return FileServiceImpl()


def provide_prompt_service() -> IPromptService:
    return PromptServiceImpl()


def provide_mcp_service() -> IMCPService:
    return MCPServiceImpl()


def provide_embeddings_service() -> IEmbeddingsService:
    return EmbeddingsServiceImpl()


def provide_tool_service() -> IToolService:
    return ToolServiceImpl()


def provide_recognizer_service(file_service: "FileServiceDepend") -> IRecognizerService:
    return RecognizerServiceImpl(file_service)


def provide_retriever_service(embeddings_service: "EmbeddingsServiceDepend",
                              file_service: "FileServiceDepend") -> IRetrieverService:
    return RetrieverServiceImpl(embeddings_service, file_service)


def provide_agent_service(chat_model_service: "ChatModelServiceDepend",
                          mcp_service: "MCPServiceDepend",
                          recognizer_service: "RecognizerServiceDepend",
                          prompt_service: "PromptServiceDepend",
                          embeddings_service: "EmbeddingsServiceDepend",
                          retriever_service: "RetrieverServiceDepend",
                          tool_service: "ToolServiceDepend") -> IAgentService:
    return AgentServiceImpl(chat_model_service, mcp_service, recognizer_service,
                            prompt_service, embeddings_service, retriever_service, tool_service)


# Services
ChatModelServiceDepend = Annotated[IChatModelService, Depends(provide_chat_model_service)]
FileServiceDepend = Annotated[IFileService, Depends(provide_file_service)]
PromptServiceDepend = Annotated[IPromptService, Depends(provide_prompt_service)]
MCPServiceDepend = Annotated[IMCPService, Depends(provide_mcp_service)]
EmbeddingsServiceDepend = Annotated[IEmbeddingsService, Depends(provide_embeddings_service)]
ToolServiceDepend = Annotated[IToolService, Depends(provide_tool_service)]
RecognizerServiceDepend = Annotated[IRecognizerService, Depends(provide_recognizer_service)]
RetrieverServiceDepend = Annotated[IRetrieverService, Depends(provide_retriever_service)]
AgentServiceDepend = Annotated[IAgentService, Depends(provide_agent_service)]

SessionDep = Annotated[AsyncClientSession, Depends(get_session)]
DownloadGeneratorDep = Annotated[SecureDownloadGenerator, Depends(provide_download_generator)]
PagingQuery = Annotated[PagingParams, Query()]
