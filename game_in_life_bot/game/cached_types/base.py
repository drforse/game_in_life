from typing import Type, Optional

from pydantic import BaseModel, PrivateAttr

from ...redis_models import Model


class GameInLifeCachedBaseObject(BaseModel):
    _model_type: Type[Model] = PrivateAttr(None)
    _model: Optional[Model] = PrivateAttr(None)

    """
    Base object for objects depending on db documents
    """

    @classmethod
    def from_db(cls, model: Model = None, **kwargs):
        if model:
            if not isinstance(model, cls._model_type):
                raise ValueError("model must be instance of cls._model_type")
            model = model
        else:
            model = cls._model_type.query.filter(**kwargs).execute()
        obj = cls.from_orm(model)
        obj._model = model
        return obj

    def update_from_db(self, model: Model = None):
        self._model = model or self._model
        if self._model:
            self._model = self._model.refresh()
        else:
            self._model = self._model_type.query.filter(**self.__fields__).execute()
        for k, v in self._model.to_dict().items():
            setattr(self, k, v)

    def save_to_db(self):
        if not self._model:
            self._model = self._model_type(**self.__dict__)
        else:
            for k in self._model.to_dict():
                setattr(self._model, k, getattr(self, k))
        self._model.save()

    def __setattr__(self, name, value):
        if not name.startswith("_"):
            self.validate({name: value})
        super().__setattr__(name, value)

    class Config:
        orm_mode = True
