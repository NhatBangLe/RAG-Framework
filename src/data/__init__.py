from typing import Annotated

from pydantic import BeforeValidator

__all__ = ["PyObjectId"]

PyObjectId = Annotated[str, BeforeValidator(str)]
