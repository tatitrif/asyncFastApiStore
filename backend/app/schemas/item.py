from pydantic import BaseModel, Field

from schemas.base import IdResponse


class Item(BaseModel):
    description: str | None = None
    price: float | None = Field(None, description="Price for the item")


class ItemRequest(Item):
    name: str


class ItemUpdateRequest(Item):
    name: str | None = None


class ItemImageResponse(BaseModel):
    image: str | None = None


class ItemResponse(ItemRequest, ItemImageResponse, IdResponse): ...


class ItemListResponse:
    data: list[ItemResponse]
