from fastapi.responses import ORJSONResponse
from pydantic import BaseModel


class PageInfo(BaseModel):
    total: int | None
    page: int | None
    size: int | None
    first: int | None
    last: int | None
    previous: int | None
    next: int | None


class Page(BaseModel):
    page_info: PageInfo
    page_data: list


class IdResponse(BaseModel):
    id: int


class JSONResponse(ORJSONResponse):
    pass
