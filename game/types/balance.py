from dataclasses import dataclass

from models import User
from pymongo.collection import ObjectId


@dataclass
class AllCurrenciesBalance:
    main: float = 0.0
    pasyucoin: float = 0.0

    def __getitem__(self, item):
        return getattr(self, item)


class Balance:
    def __init__(self,
                 user_model_id: ObjectId = None):
        self.user_model_id = user_model_id

    @property
    def main_currency_balance(self) -> float:
        print(f'{self.user_model_id=}')
        if self.user_model_id:
            user = User.get(id=self.user_model_id)
            return user.main_currency_balance
        return 0.0

    @property
    def pasyucoin_currency_balance(self) -> float:
        # get value through API

        return 0.0

    async def get_all_currencies_balance(self) -> AllCurrenciesBalance:
        return AllCurrenciesBalance(main=self.main_currency_balance,
                                    pasyucoin=self.pasyucoin_currency_balance)

    async def add_money_to_main_currency_balance(self, value: float):
        user = User.get(id=self.user_model_id)
        user.inc_main_currency_balance(value)

    async def add_money(self, currency: str, value: float):
        if currency == 'main':
            await self.add_money_to_main_currency_balance(value)
        # waiting for api to finish
        pass

    def to_python(self):
        return {"main_currency": self.main_currency_balance,
                "pasyucoin_currency": self.pasyucoin_currency_balance}

    def __str__(self):
        return str(self.to_python())
