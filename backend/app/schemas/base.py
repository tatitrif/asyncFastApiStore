from datetime import datetime

from fastapi.responses import ORJSONResponse
from pydantic import PlainSerializer, BaseModel
from typing_extensions import Annotated


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


custom_datetime = Annotated[
    datetime,
    PlainSerializer(
        lambda _datetime: _datetime.strftime("%d/%m/%Y, %H:%M:%S"), return_type=str
    ),
]
