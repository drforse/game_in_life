import typing
from mongoengine import Document
from bson import ObjectId

from models import MyDocument


class GameInLifeDbBaseObject:
    model_type = None
    """
    Base object for objects depending on db documents
    """
    def __init__(self, model: typing.Union[Document, MyDocument] = None, **kwargs):
        """

        :param model: mongoengine Document and MyDocument subclass object
        :param kwargs: object fields
        """
        self.model: typing.Union[Document, MyDocument] = model
        self.id: ObjectId = self.model.id if self.model else None
        self._update_from_db_kwargs: dict = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not self.model:
            self.update_from_db()
        else:
            for k, v in self.model.to_mongo().items():
                setattr(self, k, self._resolve_field_from_db(k, v))

    def update_from_db(self):
        if self.model:
            self.model = self.model.reload()
        else:
            self.model = self.model_type.get(**{k: v for k, v in self._update_from_db_kwargs.items()})
        for k, v in self.model.to_mongo().items():
            setattr(self, k, self._resolve_field_from_db(k, v))
        self.id = self.model.id

    async def save_to_db(self):
        for k in self.model.to_mongo():
            setattr(self.model, k, self._resolve_field_to_db(k, getattr(self, k)))
        self.model.save()

    @staticmethod
    def _resolve_field_to_db(name, value):
        return value

    @staticmethod
    def _resolve_field_from_db(name, value):
        return values
