import os

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import VpnKey, User, FreeVpnKey
from x_ui_api import api
from common.vpn_utils import get_connetion_string
load_dotenv(find_dotenv())


# Работа с пользователями.
async def orm_add_user(
        session: AsyncSession,
        telegram_id: int,
        name: str | None = None,
):
    stmt = select(User).where(telegram_id == User.telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        new_user = User(telegram_id=telegram_id, name=name)
        session.add(new_user)
        await session.commit()


async def orm_get_user_id(session: AsyncSession, telegram_id: int) -> int | None:
    result = await session.execute(select(User.id).where(telegram_id == User.telegram_id))
    user_id = result.scalar_one_or_none()
    return user_id


# Работа с ключами
KEY_LIMIT = int(os.getenv("KEY_LIMIT"))


async def orm_check_key_limit(session: AsyncSession, telegram_id: int):
    db_user_id = await orm_get_user_id(session, telegram_id)
    result = await session.execute(select(VpnKey).where(db_user_id == VpnKey.user_id))
    user_keys = result.scalars().all()
    return len(user_keys) >= KEY_LIMIT


async def orm_add_key(session: AsyncSession, user_id: int, name: str, config: str):
    new_key = VpnKey(
        user_id=user_id,
        name=name,
        config=config,

    )
    session.add(new_key)
    await session.commit()


async def orm_get_user_keys(session: AsyncSession, telegram_id: int):
    db_user_id = await orm_get_user_id(session, telegram_id)
    result = await session.execute(select(VpnKey).where(db_user_id == VpnKey.user_id))
    user_keys = result.scalars().all()
    return user_keys


#Бесплатные ключи.
async def orm_sync_free_keys_from_panel(session: AsyncSession, suffix: str = "-free"):
    inbounds = await api.inbound.get_list()

    added = 0
    updated = 0

    for inbound in inbounds:
        for client in inbound.settings.clients:
            if not client.email.endswith(suffix):
                continue

            result = await session.execute(
                select(FreeVpnKey).where(FreeVpnKey.name == client.email)
            )
            existing = result.scalar_one_or_none()

            if existing is None:
                config_string = get_connetion_string(inbound, user_uuid=client.id, name=client.email)
                key = FreeVpnKey(
                    name=client.email,
                    uuid=client.id,
                    is_active=client.enable,
                    config=config_string
                )
                session.add(key)
                added += 1
            else:
                if existing.is_active != client.enable:
                    existing.is_active = client.enable
                    updated += 1

    await session.commit()
    return added, updated


async def orm_get_free_key(session: AsyncSession)-> FreeVpnKey:
    key = session.execute(select(FreeVpnKey).where(FreeVpnKey.is_active == False))