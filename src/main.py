from contextlib import asynccontextmanager

from fastapi import FastAPI


# noinspection PyUnusedLocal
@asynccontextmanager
async def lifespan(app_inst: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
