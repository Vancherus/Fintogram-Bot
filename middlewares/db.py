# this module contains an intermediate layer for working with the database (so as not to create an asynchronous context manager for working with sessions inside the user_private.py file with handlers (since this is inconvenient)
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from database.orm_query import orm_add_user, orm_get_user
from database.engine import session_maker
from sqlalchemy.ext.asyncio import async_sessionmaker



class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool


    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)
        

class UserMiddleware(BaseMiddleware): # middleware layer for creating user id and username in the database at /start
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        current_event = (
            event.message
            or event.callback_query
            or event.inline_query
            or event.chosen_inline_result
        )

        user_id = current_event.from_user.id
        username = current_event.from_user.username

        async with session_maker() as session:
            # Добавить если нет
            await orm_add_user(session, user_id, username)
            # Получить из базы
            user = await orm_get_user(session, user_id)

        data['user'] = user
        return await handler(event, data)
