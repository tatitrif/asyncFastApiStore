from typing import Sequence, Type

from sqlalchemy import insert, select, update, delete, func
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from helpers.paginator import create_pagination_info


class BaseDAO:
    """
    A basic data access that implements basic CRUD functions with a base table using the SqlAlchemy library

    params:
        - model: SQLAlchemy DeclarativeBase child class
    """

    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_one_or_none(self, _id: int):
        """
        Асинхронно находит и возвращает один экземпляр модели по указанным критериям или None.

        Аргументы:
            **kwargs: Критерии фильтрации в виде идентификатора записи.

        Возвращает:
            Экземпляр модели или None, если ничего не найдено.
        """

        query = select(self.model).filter_by(id=_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_by_page(
        self, limit: int, offset: int = 0, **kwargs
    ) -> tuple[dict, Sequence[Type[model]]]:
        """
        Асинхронно находит и возвращает все экземпляры модели, удовлетворяющие указанным критериям.

        Аргументы:
            page_number: Критерии номера страницы,
            page_size: Критерии количества объектов на странице.

        Возвращает:
            Словарь с информацией о странице и список экземпляров модели.
        """

        query = select(self.model).filter_by(**kwargs)
        query_count = select(func.count(self.model.id)).filter_by(**kwargs)

        query = query.limit(limit).offset(offset)
        res: Result = await self.session.execute(query)
        res_count: Result = await self.session.execute(query_count)
        page_entities = res.unique().scalars().all()
        all_entities_count = res_count.unique().scalars().first()
        pagination_info = create_pagination_info(
            page_size=limit, page_number=offset, count=all_entities_count
        )
        return pagination_info, page_entities

    async def add_one_and_return(self, **kwargs) -> Type[model]:
        """
        Асинхронно создает новый экземпляр модели с указанными значениями.

        Аргументы:
            **kwargs: Именованные аргументы для создания нового экземпляра модели.

        Возвращает:
            Созданный экземпляр модели.
        """
        query = insert(self.model).values(**kwargs).returning(self.model)
        _obj: Result = await self.session.execute(query)
        await self.session.commit()
        return _obj.unique().scalar_one()

    async def update_one_by_id(self, _id: int, **values) -> Type[model]:
        """
        Асинхронно обновляет экземпляр модели, удовлетворяющий критерию,
        новыми значениями, указанными в values.

        Аргументы:
            id: Критерии фильтрации в виде именованного параметра.
            **values: Именованные параметры для обновления значений экземпляров модели.

        Возвращает:
            Обновленный экземпляр модели.
        """
        query = (
            update(self.model)
            .filter(self.model.id == _id)
            .values(**values)
            .returning(self.model)
        )
        _obj: Result | None = await self.session.execute(query)
        await self.session.commit()
        return _obj.unique().scalar_one_or_none()

    async def delete(self, delete_all: bool = False, **filter_by):
        """
        Асинхронно удаляет экземпляры модели, удовлетворяющие критериям фильтрации, указанным в filter_by.

        Аргументы:
            delete_all: Если True, удаляет все экземпляры модели без фильтрации.
            **filter_by: Критерии фильтрации в виде именованных параметров.

        Возвращает:
            Количество удаленных экземпляров модели.
        """

        if delete_all is False:
            if not filter_by:
                raise ValueError(
                    "Необходимо указать хотя бы один параметр для удаления."
                )

        query = delete(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        await self.session.commit()

        return result.rowcount
