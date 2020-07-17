import logging
import typing
from aiohttp import ClientSession
from urlpath import URL

from .exceptions import *


class SendermanRoulletteApi:
    _base_url = URL('https://rouletteapi.herokuapp.com/users/')

    def __init__(self, bot_token: str = None, session: ClientSession = None):
        self._bot_token = bot_token
        self._session = session or ClientSession()

    async def get_balance(self, user_id: int) -> typing.Optional[int]:
        url = self._generate_url('getBalance', False, user_id=user_id)
        result = await self._session.get(url)
        result = await self._get_result_or_raise(result, 'getBalance', user_id=user_id)
        coins = result['coins']
        if coins == -1:
            return None
        return coins

    async def update_coins(self, user_id: int, coins: int):
        url = self._generate_url('updateCoins', True, user_id=user_id, coins=coins)
        result = await self._session.put(url)
        await self._get_result_or_raise(result, 'updateCoins', user_id=user_id, coins=coins)

    @classmethod
    async def _get_result_or_raise(cls,
                                   response,
                                   request_path,
                                   **kwargs):
        log_append = ''
        for kwarg in kwargs:
            log_append += f' with {kwarg} {kwargs[kwarg]}'
        try:
            result = await response.json()
        except:
            log = f'{request_path} request was unsuccessfull'
            logging.error(log + log_append)
            raise SendermanRoulleteApiException(response.status)

        if response.status == 200:
            return result

        if response.status == 404:
            log = f'{request_path} request was unseccessful, 404, {result.get("message")}'
            logging.error(log + log_append)
            raise UserNotFound(result.get('message'))
        elif response.status == 400 and result.get('message') == 'Not enough coins will remain on balance (must be at least 400)':
            log = f'{request_path} request was unsuccessfull, 400, {result.get("message")}'
            logging.error(log + log_append)
            raise NotEnoughCoinsRemaining(result.get('message'))
        elif response.status == 400:
            log = f'{request_path} request was unsuccessfull, 400, {result.get("message")}'
            logging.error(log + log_append)
            raise BadRequest(result.get('message'))
        elif response.status == 401:
            log = f'{request_path} request was unsuccessfull, 401, {result.get("message")}'
            logging.error(log + log_append)
            raise Unauthorized(result.get('message'))
        else:
            log = f'{request_path} request was unsuccessfull, {result.status}, {result.get("message")}'
            logging.error(log + log_append)
            raise SendermanRoulleteApiException(response.status)

    def _generate_url(self, path: str, needs_auth: bool = True, **kwargs):
        query = {k: v for k, v in kwargs.items()}
        if needs_auth:
            query.update({'token': self._bot_token})
        return str((self._base_url / path).add_query(query))

    async def disconnect(self):
        await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
