from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.user import get_current_active_user, check_admin_role
from dependencies.database import get_db
from dao import user as dao
from helpers.paginator import pagination

from schemas import user as schemas
from schemas.base import PageInfo, Page

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=schemas.UserResponse,
)
async def read_users_me(
    current_user: Annotated[schemas.UserResponse, Depends(get_current_active_user)],
):
    return current_user


@router.patch(
    "/me",
    response_model=schemas.UserResponse,
)
async def _update_one_by_id(
    user: Annotated[schemas.UserResponse, Depends(get_current_active_user)],
    data: schemas.UserUpdate = Depends(),
    session: AsyncSession = Depends(get_db),
):
    data = data.model_dump()
    return await dao.UserDAO(session).update_one_by_id(user.id, **data)


@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
)
async def _get_one_by_id(user_id: int, session: AsyncSession = Depends(get_db)):
    entity = await dao.UserDAO(session).find_one_or_none(id=user_id, is_active=1)
    if entity:
        return entity
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found id={user_id}"
    )


@router.get(
    "/",
    response_model=Page,
)
async def _get_many(
    page_params: dict = Depends(pagination),
    session: AsyncSession = Depends(get_db),
):
    pagination_info, page_entities = await dao.UserDAO(session).find_all_by_page(
        **page_params, is_active=1
    )
    if not page_entities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Page not found"
        )
    return Page(
        page_info=PageInfo(**pagination_info),
        page_data=[schemas.UserResponse(**entity.__dict__) for entity in page_entities],
    )


@router.patch(
    "/{user_id}",
    response_model=schemas.UserResponse,
    dependencies=[Depends(check_admin_role)],
)
async def _update_one_by_id(
    user_id: int,
    user: schemas.UserUpdate = Depends(),
    session: AsyncSession = Depends(get_db),
):
    data = user.model_dump()
    if await dao.UserDAO(session).find_one_or_none(id=user_id, is_active=1):
        return await dao.UserDAO(session).update_one_by_id(user_id, **data)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found id={user_id}"
    )


@router.delete("/{user_id}", dependencies=[Depends(check_admin_role)])
async def _delete_by_id(user_id: int, session: AsyncSession = Depends(get_db)):
    if await dao.UserDAO(session).find_one_or_none(id=user_id, is_active=1):
        if await dao.UserDAO(session).update_one_by_id(_id=user_id, is_active=1):
            return {"detail": f"Deleted id={user_id}"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Not found id={user_id}"
    )
