from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from common.vpn_utils import get_connetion_string
from database.orm_query import orm_add_key, orm_get_user_id, orm_check_key_limit, orm_sync_free_keys_from_panel
from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.reply import get_keyboard
from x_ui_api import add_user, api, safe_api_call, api_inbound_info, api_toggle_user, api_get_user

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


@admin_router.message(F.text == "Синхронизация бесплатных ключей")
async def sync_free_keys(message: types.Message, session: AsyncSession):
    added, updated = await orm_sync_free_keys_from_panel(session)
    await message.answer(f"Синхронизация завершена:{added} добавлено, {updated} обновлено.")

ADMIN_KB = get_keyboard(
    "Добавить ключ",
    "Пользователи онлайн",
    "Получить IP пользователя",
    "Активировать/деактивировать пользователя",
    "Все пользователи?",
    "Синхронизация бесплатных ключей",
    "🏠 Главное меню",

    placeholder="Клавиатура админа",
    sizes=(2,)

)


class ApiAddUser(StatesGroup):
    name = State()


# Перевод в первое состояние-получение имени
@admin_router.message(StateFilter(None), F.text == "Добавить ключ")
async def api_add_user(message: types.Message, state: FSMContext):
    await message.answer("Введите имя ключа.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ApiAddUser.name)


@admin_router.message(ApiAddUser.name)
async def add_name(message: types.Message, state: FSMContext, session: AsyncSession):
    await message.answer("⏳ Ожидайте...")

    # Сохраняем имя ключа во временное состояние FSM
    await state.update_data(name=message.text)
    data = await state.get_data()
    key_name = data["name"]

    # Получаем inbound объект по ID
    inbound = await api.inbound.get_by_id(1)

    # Получаем user.id из базы по telegram_id
    user_tg_id = message.from_user.id
    user_db_id = await orm_get_user_id(session, user_tg_id)
    if await orm_check_key_limit(session, user_tg_id):
        await message.answer("❗ Вы достигли лимита ключей. Удалите один или обратитесь в поддержку.")
        await state.clear()
        return

    # Создаём VPN-клиента в панели
    key = await safe_api_call("Создание нового ключа", add_user(key_name))
    if not key:
        await message.answer("Произошла ошибка при создании ключа \n Скорее всего ключ с таким именем уже есть.")
        await state.clear()
        return
    key_uuid = uuid.UUID(key.id)
    key_name = key_uuid.hex[:8] + key_name
    config_string = get_connetion_string(inbound, key.id, key_name)

    # Сохраняем ключ в базу данных
    await orm_add_key(session, user_db_id, key_name, config_string)

    # Отправляем сообщение пользователю
    await message.answer(
        f"✅ Ключ <b>{key_name}</b> успешно добавлен!\n\n<code>{config_string}</code>",
        parse_mode="HTML"
    )

    # Очищаем состояние FSM
    await state.clear()


@admin_router.message(F.text == "Пользователи онлайн" )

@admin_router.message(Command("admin"))
async def admin_kb(message: types.Message):
    await message.answer("Админ панель.", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "🏠 Главное меню")
async def main_menu(message: types.Message):
    await message.answer(
        '🏠 Главное меню',
        reply_markup=get_keyboard(
            "📊 Профиль",
            "🛠 Поддержка",
            placeholder="WELCOME",
        )
    )
