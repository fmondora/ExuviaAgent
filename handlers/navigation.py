from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified
from aiogram.utils.callback_data import CallbackData
from keyboards.menus import nav_cd, MENU_STRUCTURE, build_menu
from notion.crud import (
    get_user_role,
    get_my_classes,
    get_upcoming_classes,
    enroll_user
)
from config import _ as gettext
import datetime

# ----------------------------------------------------------------
# CallbackData per il flusso “classi” (più compatto dell'UUID)
classes_cd = CallbackData('cs', 'action', 'date', 'idx')
# ----------------------------------------------------------------

async def handle_classes(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    action = callback_data['action']
    date = callback_data.get('date', '')
    idx = int(callback_data.get('idx', 0))

    # --- 1) My Classes ---
    if action == 'my':
        my_classes = await get_my_classes(user_id)
        kb = InlineKeyboardMarkup(row_width=1)
        for i, cls in enumerate(my_classes):
            # icone basate su subscribers_count e waiting_count
            if cls.subscribers_count < cls.capacity:
                icon = "✅"
            elif cls.waiting_count > 0:
                icon = "⏳"
            else:
                icon = "➕"
            label = f"{icon} {cls.date} {cls.time} – {cls.name}"
            kb.add(InlineKeyboardButton(
                label,
                callback_data=classes_cd.new(action='toggle_my', date='', idx=i)
            ))
        kb.add(InlineKeyboardButton(
            gettext("back"),
            callback_data=nav_cd.new(path="classes")
        ))
        await call.message.edit_text(gettext("my_classes_title"), reply_markup=kb)
        await call.answer()
        return

    # --- 1b) Toggle enroll/unenroll in My Classes ---
    if action == 'toggle_my':
        my_classes = await get_my_classes(user_id)
        cls = my_classes[idx]
        result = await enroll_user(user_id, cls.id)
        await call.answer(gettext(f"{result}_success"), show_alert=True)
        # ri-mostra la lista aggiornata
        return await handle_classes(call, {'action': 'my', 'date': '', 'idx': 0})

    # --- 2) Upcoming Classes: calendar view ---
    if action == 'calendar':
        kb = InlineKeyboardMarkup(row_width=4)
        today = datetime.date.today()
        for i in range(7):
            d = today + datetime.timedelta(days=i)
            kb.insert(InlineKeyboardButton(
                d.strftime("%a %d/%m"),
                callback_data=classes_cd.new(action='day', date=d.isoformat(), idx=i)
            ))
        kb.add(InlineKeyboardButton(
            gettext("back"),
            callback_data=nav_cd.new(path="classes")
        ))
        await call.message.edit_text(gettext("upcoming_calendar_title"), reply_markup=kb)
        await call.answer()
        return

    # --- 3) Lista delle classi di un giorno ---
    if action == 'day':
        classes = await get_upcoming_classes(date)
        kb = InlineKeyboardMarkup(row_width=1)
        for i, cls in enumerate(classes):
            if cls.subscribers_count < cls.capacity:
                icon = "✅"
            elif cls.waiting_count > 0:
                icon = "⏳"
            else:
                icon = "➕"
            label = f"{icon} {cls.time} – {cls.name} ({cls.subscribers_count} subs)"
            kb.add(InlineKeyboardButton(
                label,
                callback_data=classes_cd.new(action='toggle_up', date=date, idx=i)
            ))
        kb.add(InlineKeyboardButton(
            gettext("back"),
            callback_data=classes_cd.new(action='calendar', date='', idx=0)
        ))
        await call.message.edit_text(gettext("classes_on_date").format(date=date), reply_markup=kb)
        await call.answer()
        return

    # --- 4) Toggle enroll/unenroll/waiting in Upcoming ---
    if action == 'toggle_up':
        classes = await get_upcoming_classes(date)
        cls = classes[idx]
        result = await enroll_user(user_id, cls.id)
        await call.answer(gettext(f"{result}_success"), show_alert=True)
        # ri-mostra la lista del giorno aggiornato
        return await handle_classes(call, {'action': 'day', 'date': date, 'idx': idx})

    # fallback sul callback delle classi (non dovrebbe mai succedere)
    await call.answer()

async def navigate_menu(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    user_role = await get_user_role(user_id)
    path = callback_data.get("path", "")

    # override per la sezione “Classes”
    if path == "classes":
        kb = InlineKeyboardMarkup(row_width=1)
        # Mostra “My Classes” solo a chi ha ruolo PREMIUM o superiore
        if user_role in {Role.PREMIUM, Role.COACH, Role.ADMIN}:
            kb.add(InlineKeyboardButton(
                gettext("my_classes_title"),
                callback_data=classes_cd.new(action='my', date='', idx=0)
            ))
        # Sempre disponibile: Upcoming Classes
        kb.add(InlineKeyboardButton(
            gettext("upcoming_calendar_title"),
            callback_data=classes_cd.new(action='calendar', date='', idx=0)
        ))
        kb.add(InlineKeyboardButton(
            gettext("back"),
            callback_data=nav_cd.new(path="")
        ))
        await call.message.edit_text(gettext("classes_title"), reply_markup=kb)
        await call.answer()
        return

    # navigazione generica
    node_list = MENU_STRUCTURE
    if path:
        for segment in path.split("/"):
            node_list = next(item for item in node_list if item["key"] == segment)["children"]

    kb = build_menu(node_list, user_role=user_role, path=path)
    crumb_key = path.split("/")[-1] if path else "main_menu_title"
    breadcrumb = gettext("breadcrumb_prefix").format(crumb=gettext(crumb_key))
    try:
        await call.message.edit_text(breadcrumb, reply_markup=kb)
    except MessageNotModified:
        pass
    await call.answer()

def register_navigation(dp: Dispatcher):
    # Il flusso “classi” ha priorità
    dp.register_callback_query_handler(handle_classes, classes_cd.filter())
    # Poi la navigazione generica
    dp.register_callback_query_handler(navigate_menu, nav_cd.filter())
