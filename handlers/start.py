from aiogram import types, Dispatcher
from notion.crud import get_user_role
from keyboards.menus import build_menu, MENU_STRUCTURE
from config import _, APP_ENV, logger

async def cmd_start(message: types.Message):
    user_role = await get_user_role(message.from_user.id)
    
    # Aggiunto logging in modalità sviluppo
    if APP_ENV == "development":
        await message.answer(
            f"🔧 DEV MODE\n"
            f"Your Telegram ID is: <b>{message.from_user.id}</b>\n"
            f"Your role is: <b>{user_role.name}</b>"
        )
    logger.info(f"DEV MODE - User ID: {message.from_user.id}, Role: {user_role}")

    kb = build_menu(MENU_STRUCTURE, user_role=user_role)
    await message.answer(_("main_menu_title"), reply_markup=kb)

def register_start(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
