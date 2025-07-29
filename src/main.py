import asyncio
import logging
import os
import platform
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

from src.data.database import insert_default_data
from src.dependency import DownloadGeneratorDep
from src.route.agent import router as agent_router
from src.route.chat_model import router as chat_model_router
from src.route.embeddings import router as embeddings_router
from src.route.file import router as file_router
from src.route.mcp import router as mcp_router
from src.route.prompt import router as prompt_router
from src.route.recognizer import router as recognizer_router
from src.route.retriever import router as retriever_router
from src.route.tool import router as tool_router
from src.util.constant import EnvVar
from src.util.error import NotFoundError, InvalidArgumentError, NotAcceptableError


## Set up logging.
def setup_logging():
    level = os.getenv("LOG_LEVEL", "INFO")
    matches = {
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "WARNING": logging.WARNING,
    }

    pattern = (
        "%(asctime)s - %(levelname)s - %(name)s - "
        "%(filename)s:%(lineno)d - %(message)s"
    )
    logging.basicConfig(level=matches[level], format=pattern)


def setup_event_loop():
    if 'Windows' in platform.system():
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )


# Initialize
load_dotenv()
setup_event_loop()
setup_logging()
logger = logging.getLogger(__name__)

# Create a new client and connect to the server
mongodb_client = AsyncMongoClient(os.getenv(EnvVar.DB_URI.value), server_api=ServerApi('1'))


# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(app_inst: FastAPI):
    logger.info("Connecting to database...")
    await mongodb_client.aconnect()
    logger.info("Database connection established. Starting up the application...")

    is_create_default_data = os.getenv(EnvVar.CREATE_DEFAULT_ENTITIES.value, "False")
    if is_create_default_data in ["True", "true"]:
        logger.info("Creating default entities...")
        await insert_default_data()
        logger.info("Default entities have been created successfully.")

    yield

    logger.info("Closing database connection...")
    await mongodb_client.close()
    logger.info("Good bye!")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_model_router)
app.include_router(prompt_router)
app.include_router(retriever_router)
app.include_router(embeddings_router)
app.include_router(recognizer_router)
app.include_router(mcp_router)
app.include_router(agent_router)
app.include_router(file_router)
app.include_router(tool_router)


# Global routes
@app.get("/download", tags=["Download File"], status_code=status.HTTP_200_OK)
async def download(token: str, generator: DownloadGeneratorDep):
    file = generator.verify_token(token)
    return FileResponse(
        path=file["path"],
        media_type=file["mime_type"],
        filename=file["name"]
    )


@app.get("/health", tags=["Health Check"], status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK"
    }


# Exception handlers
# noinspection PyUnusedLocal
@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": exc.reason},
    )


# noinspection PyUnusedLocal
@app.exception_handler(InvalidArgumentError)
async def invalid_argument_exception_handler(request: Request, exc: InvalidArgumentError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": exc.reason},
    )


# noinspection PyUnusedLocal
@app.exception_handler(NotAcceptableError)
async def not_acceptable_exception_handler(request: Request, exc: NotAcceptableError):
    return JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content={"message": exc.reason},
    )
