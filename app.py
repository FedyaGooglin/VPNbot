import asyncio
import os

from aiogram import Bot, Dispatcher, types
from dotenv import find_dotenv, load_dotenv

from common.bot_cmds_list import private
from database.engine import create_db, drop_db, session_maker
from handlers.admin_private import admin_router
from handlers.user_private import user_private_router
from middlewares.db import DataBaseSession
from x_ui_api import login_on_startup, safe_api_call

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'))
admin_ids = os.getenv("ID","")
admins_list = [int(i) for i in admin_ids.split(",") if i.strip()]
bot.my_admins_list = admins_list

dp = Dispatcher()

dp.include_router(admin_router)
dp.include_router(user_private_router)

ALLOWED_UPDATES = ['message', 'edited_message']


async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def main():
    dp.startup.register(on_startup)
    print(admins_list)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await safe_api_call("Авторизация при запуске", login_on_startup())
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


asyncio.run(main())
