from aiogram import F, types, Router
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_user, orm_get_user_keys
from filters.chat_types import ChatTypeFilter
from kbds.reply import get_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    # Проверка на наличие в базе и создание пользователя
    user = message.from_user
    await orm_add_user(
        session,
        telegram_id=user.id,
        name=user.first_name

    )
    # Стартовое меню
    await message.answer(
        f"Привет, {message.from_user.first_name} (@{message.from_user.username})! 👋\n\n"
        f"Ты участвуешь в тестировании VPN-бота <b>T:AYK</b>.\n\n"
        f"Для взаимодействия с ботом тебе доступны:\n\n"
        f"🔑 <b>Команда /admin</b> — откроет админ-панель, где ты можешь:\n"
        f"• Добавлять ключи (VPN-подключения, лимит 3 штуки на пользователя.)\n"
        f"• Просматривать созданные ключи\n"
        f"• Тестировать интерфейс\n\n"
        f"🏠 Используй кнопку <b>«Главное меню»</b>, чтобы вернуться к началу в любой момент.\n\n"
        f"💬 Если найдёшь ошибку или что-то непонятно — сразу сообщи!\n",
        parse_mode="HTML",
        reply_markup=get_keyboard(
            "📊 Профиль",
            "🛠 Поддержка",
            placeholder="WELCOME",
        )
    )


@user_private_router.message(F.text == "📊 Профиль")
async def user_profile(message: types.Message, session: AsyncSession):
    user_tg_id = message.from_user.id

    user_keys = await orm_get_user_keys(session, user_tg_id)
    # if not user_keys:
    #     await message.answer('Вы еще не зарегистрированы.')
    #     return

    keys_count = len(user_keys)

    profile_text = (
        f"📇 <b>Профиль</b>\n\n"
        f"👤 Имя: <b>{message.from_user.first_name or '—'}</b>\n"
        f"🆔 Telegram ID: <code>{message.from_user.id}</code>\n"
        f"🔐 Кол-во ключей: <b>{keys_count}</b>\n"
    )

    reply_kb = get_keyboard(
        "🔑 Мои ключи",
        "🏠 Главное меню",
        placeholder="Выберите действие",
        sizes=(2,)
    )
    await message.answer(profile_text, parse_mode="HTML", reply_markup=reply_kb)


@user_private_router.message(F.text == "🔑 Мои ключи")
async def user_keys_list(message: types.Message, session: AsyncSession):
    user_tg_id = message.from_user.id

    user_keys = await orm_get_user_keys(session, user_tg_id)
    if not user_keys:
        await message.answer('У Вас нет ни одного ключа доступа.')
        return

    for key in user_keys[:3]:
        text = (
            f"🔐 <b>Имя ключа:</b> <code>{key.name}</code>\n"
            f"🔗 <b>Конфигурация:</b>\n<code>{key.config}</code>"
        )
        await message.answer(text, parse_mode="HTML")

#TODO проверить работают ли эти функции тут и в админке
@user_private_router.message(F.text == "🏠 Главное меню")
async def main_menu(message: types.Message):
    await message.answer(
        '🏠 Главное меню',
        reply_markup=get_keyboard(
            "📊 Профиль",
            "🛠 Поддержка",
            placeholder="WELCOME",
        )
    )
