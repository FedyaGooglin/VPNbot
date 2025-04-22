import logging
import os
import uuid

from dotenv import find_dotenv, load_dotenv
from py3xui import AsyncApi, Client, Inbound

load_dotenv(find_dotenv())

HTTP = os.getenv('HTTP')
LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')

api = AsyncApi(HTTP, LOGIN, PASSWORD, use_tls_verify=False)
logger = logging.getLogger(__name__)


async def safe_api_call(desc: str, coro):
    try:
        return await coro
    except Exception as e:
        logger.error(f"[API] Ошибка : {desc}:{e}")


# Логин при старте бота(в душе не ебу как он работает)
async def login_on_startup():
    await api.login()


###ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗВОАТЕЛЯМИ###
async def get_online():
    return await api.client.online()


async def add_user(name: str):
    new_client = Client(id=str(uuid.uuid4()), email=name, enable=True)
    inbound = await api.inbound.get_by_id(1)

    await api.client.add(inbound.id, [new_client])

    return new_client


async def api_get_user(name: str):
    user: Client = await api.client.get_by_email(name)
    return user


async def api_get_ips(name: str):
    return await api.client.get_ips(name)


async def api_toggle_user(client: Client, enable: bool) -> Client:
    client.enable = enable
    await api.client.update(client.id, client)
    return client


###ФУНКЦИИ ДЛЯ РАБОТЫ С Подключением(inbound)###
async def api_inbound_info(inbound_id: int) :
    inbound = await api.inbound.get_by_id(inbound_id)
    return inbound
