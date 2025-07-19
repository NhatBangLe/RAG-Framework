from ..database import get_by_id, MongoCollection, get_collection, create_document, update_by_id, delete_by_id
from ..dto.prompt import PromptCreate, PromptUpdate, PromptPublic
from ..model import Prompt
from ...config.model.prompt import PromptConfiguration
from ...util import PagingWrapper, PagingParams


async def get_all_prompts_as_documents(params: PagingParams) -> PagingWrapper[PromptPublic]:
    collection = get_collection(MongoCollection.PROMPT)
    return await PagingWrapper.get_paging(params, collection)


async def get_prompt_as_document(prompt_id: str):
    not_found_msg = f'No prompt configuration with id {prompt_id} found.'
    return await get_by_id(prompt_id, MongoCollection.PROMPT, not_found_msg)


async def get_prompt_as_configuration(prompt_id: str) -> PromptConfiguration:
    doc_prompt = await get_prompt_as_document(prompt_id)
    prompt = Prompt.model_validate(doc_prompt)
    return PromptConfiguration.model_validate(prompt.model_dump())


async def create_prompt_as_document(data: PromptCreate):
    model = Prompt.model_validate(data.model_dump())
    return await create_document(model, MongoCollection.PROMPT)


async def update_prompt_as_document(prompt_id: str, data: PromptUpdate):
    model = Prompt.model_validate(data.model_dump())
    await update_by_id(prompt_id, model, MongoCollection.PROMPT)


async def delete_prompt_by_id(prompt_id: str):
    await delete_by_id(prompt_id, MongoCollection.PROMPT)
