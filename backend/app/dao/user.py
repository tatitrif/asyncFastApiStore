from typing import Type

from sqlalchemy import update
from sqlalchemy.engine import Result

from dao.base import BaseDAO
from models import user as models


class UserDAO(BaseDAO):
    model = models.User

    async def update_one_by_name(self, name: str, **values) -> Type[model]:
        """
        Асинхронно обновляет экземпляр модели, удовлетворяющий критерию,
        новыми значениями, указанными в values.

        Аргументы:
            name: Критерии фильтрации в виде именованного параметра.
            **values: Именованные параметры для обновления значений экземпляров модели.

        Возвращает:
            Обновленный экземпляр модели.
        """
        query = (
            update(self.model)
            .filter(self.model.username == name)
            .values(**values)
            .returning(self.model)
        )
        _obj: Result | None = await self.session.execute(query)
        await self.session.commit()
        return _obj.unique().scalar_one_or_none()
