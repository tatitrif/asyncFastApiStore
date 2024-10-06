from dao.base import BaseDAO
from models import item as models


class ItemsDAO(BaseDAO):
    model = models.Item
