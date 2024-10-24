from sqlalchemy import select, desc, or_
from sqlalchemy.engine import Result
from sqlalchemy.orm import joinedload

from dao.base import BaseDAO
from models import chat as models


class MessageDAO(BaseDAO):
    model = models.Message

    async def get_chat(self, user_id: int, limit: int = 5):
        """
        Асинхронно находит и возвращает все экземпляры модели, удовлетворяющие указанным критериям.

        Аргументы:
            user_id:получатель сообщений
            limit: Критерии кол-ва объектов

        Возвращает:
            Словарь со списком экземпляров модели.
        """
        query = (
            (
                select(self.model)
                .options(joinedload(self.model.sender))
                .options(joinedload(self.model.receiver))
                .where(
                    or_(
                        self.model.sender_id == user_id,
                        self.model.receiver_id.is_(None),
                        self.model.receiver_id == user_id,
                    )
                )
            )
            .order_by(desc(self.model.created))
            .limit(limit)
        )
        result: Result = await self.session.execute(query)
        return result.scalars().all()
