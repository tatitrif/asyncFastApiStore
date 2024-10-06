from fastapi import Query


class PaginatedParams:
    default_page_number = 1
    page_number_ge = 1
    default_page_size = 10
    page_size_ge = 1


async def pagination(
    size: int = Query(
        PaginatedParams.default_page_size,
        ge=PaginatedParams.page_size_ge,
        description="Pagination page size",
        alias="page[size]",
    ),
    page: int = Query(
        PaginatedParams.default_page_number,
        ge=PaginatedParams.page_size_ge,
        description="Pagination page number",
        alias="page[number]",
    ),
):
    return {"limit": size, "offset": page}


def create_pagination_info(
    page_size: int, page_number: int, count: int
) -> dict[str, int | None]:
    last_page = count // page_size + 1 if count % page_size else count // page_size
    next_page = page_number + 1 if page_number < last_page else None
    prev_page = page_number - 1 if (page_number - 1) > 0 else None

    pagination_info = {
        "total": count,
        "page": page_number,
        "size": page_size,
        "first": 1,
        "last": last_page,
        "previous": prev_page,
        "next": next_page,
    }

    return pagination_info
