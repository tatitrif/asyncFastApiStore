from fastapi import APIRouter, status, UploadFile, File, Form
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

import exceptions
from dao import item as dao
from dependencies.database import get_db
from dependencies.user import check_admin_role
from helpers.paginator import pagination
from helpers.upload import handle_file_upload
from schemas import item as schemas
from schemas.base import PageInfo, Page

router = APIRouter(prefix="/items", tags=["items"])


@router.get(
    "/{item_id}",
    response_model=schemas.ItemResponse,
)
async def _get_one_by_id(item_id: int, session: AsyncSession = Depends(get_db)):
    entity = await dao.ItemsDAO(session).find_one_or_none(id=item_id)
    if entity:
        return entity
    raise exceptions.ITEM_EXCEPTION_NOT_FOUND_ITEM


@router.get(
    "/",
    response_model=Page,
)
async def _get_many(
    page_params: dict = Depends(pagination),
    session: AsyncSession = Depends(get_db),
):
    pagination_info, page_entities = await dao.ItemsDAO(session).find_all_by_page(
        **page_params
    )
    if not page_entities:
        raise exceptions.ITEM_EXCEPTION_NOT_FOUND_PAGE

    return Page(
        page_info=PageInfo(**pagination_info),
        page_data=[schemas.ItemResponse(**entity.__dict__) for entity in page_entities],
    )


@router.post(
    "/",
    response_model=schemas.ItemResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_admin_role)],
)
async def _create_one(
    item: schemas.ItemRequest = Depends(),
    image_file: UploadFile | str | None = File(None, media_type="image/*"),
    session: AsyncSession = Depends(get_db),
):
    data = item.model_dump()
    if image_file:
        try:
            file_name = await handle_file_upload(image_file)
            data["image"] = file_name
        except ValueError:
            raise exceptions.ITEM_EXCEPTION_IMAGE
    return await dao.ItemsDAO(session).add_one_and_return(**data)


@router.patch(
    "/{item_id}",
    response_model=schemas.ItemResponse,
    dependencies=[Depends(check_admin_role)],
)
async def _update_one_by_id(
    item_id: int,
    name: str = Form(None),
    description: str | None = Form(None),
    price: float = Form(0),
    image_file: UploadFile | str | None = File(None, media_type="image/*"),
    session: AsyncSession = Depends(get_db),
):
    data = dict(
        name=name,
        description=description,
        price=price,
    )

    if image_file:
        try:
            file_name = await handle_file_upload(image_file)
            data["image"] = file_name

        except ValueError:
            raise exceptions.ITEM_EXCEPTION_IMAGE

    if await dao.ItemsDAO(session).find_one_or_none(id=item_id):
        return await dao.ItemsDAO(session).update_one_by_id(item_id, **data)
    raise exceptions.ITEM_EXCEPTION_NOT_FOUND_ITEM


@router.delete(
    "/{item_id}",
    dependencies=[Depends(check_admin_role)],
)
async def _delete_by_id(item_id: int, session: AsyncSession = Depends(get_db)):
    if await dao.ItemsDAO(session).find_one_or_none(id=item_id):
        if await dao.ItemsDAO(session).delete(id=item_id):
            return {"detail": f"Deleted id={item_id}"}
    raise exceptions.ITEM_EXCEPTION_NOT_FOUND_ITEM
