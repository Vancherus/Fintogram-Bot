from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import asyncio
import logging

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from database.engine import create_db, drop_db, session_maker  # noqa: E402

from handlers.user_private import user_private_router  # noqa: E402
from common.bot_cmds_list import private  # noqa: E402

from middlewares.db import DataBaseSession, UserMiddleware  # noqa: E402

import os # noqa: E402

# ALLOWED_UPDATES = ['message, edited_message', 'callback_query']

bot = Bot(token=os.getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML)) # type: ignore

dp = Dispatcher()

dp.include_router(user_private_router)

async def on_startup(bot):

    await drop_db() # comment out on production so that the database is not deleted during each debug

    await create_db()


async def on_shutdown(bot):
    print('бот лег')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    
    dp.update.middleware(UserMiddleware())

    
    await bot.delete_webhook(drop_pending_updates=True) # avoid replying after bot finishes
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) 
    try:
        asyncio.run(main())  
    except KeyboardInterrupt:
        print('Exit')  
    