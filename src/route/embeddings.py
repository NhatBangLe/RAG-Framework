from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/embeddings",
    tags=["Embeddings"],
    responses={
        400: {"description": "Invalid parameter(s)."},
        404: {"description": "Entity not found."}
    },
)
