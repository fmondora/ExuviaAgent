from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified
from keyboards.menus import nav_cd, MENU_STRUCTURE, build_menu
from notion.crud import (
    get_user_role,
    get_my_classes,
    get_upcoming_classes,
    get_subscribers_for_class,
    enroll_user
)
from config import _ as gettext
import datetime

async def navigate(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    user_role = await get_user_role(user_id)
    path = callback_data.get("path", "")

    # 1. My Classes
    if path == "classes/my_classes":
        my_classes = await get_my_classes(user_id)
        kb = InlineKeyboardMarkup(row_width=1)
        for cls in my_classes:
            label = f"{cls.date} {cls.time} – {cls.name}"
            kb.add(InlineKeyboardButton(label, callback_data=nav_cd.new(path=f"classes/my_classes/{cls.id}")))
        kb.add(InlineKeyboardButton(gettext("back"), callback_data=nav_cd.new(path="classes")))
        await call.message.edit_text(gettext("my_classes_title"), reply_markup=kb)
        await call.answer()
        return

    # 1b. Toggle unenroll from My Classes
    if path.startswith("classes/my_classes/") and path.count("/") == 2:
        _, _, class_id = path.split("/")
        success = await enroll_user(user_id, class_id)
        text = gettext("unenroll_success") if not success else gettext("enroll_success")
        await call.answer(text, show_alert=True)
        my_classes = await get_my_classes(user_id)
        kb = InlineKeyboardMarkup(row_width=1)
        for cls in my_classes:
            label = f"{cls.date} {cls.time} – {cls.name}"
            kb.add(InlineKeyboardButton(label, callback_data=nav_cd.new(path=f"classes/my_classes/{cls.id}")))
        kb.add(InlineKeyboardButton(gettext("back"), callback_data=nav_cd.new(path="classes")))
        await call.message.edit_text(gettext("my_classes_title"), reply_markup=kb)
        return

    # 2. Upcoming Classes – calendar
    if path == "classes/upcoming_classes":
        kb = InlineKeyboardMarkup(row_width=4)
        today = datetime.date.today()
        for i in range(7):
            d = today + datetime.timedelta(days=i)
            label = d.strftime("%a %d/%m")
            kb.insert(InlineKeyboardButton(label, callback_data=nav_cd.new(path=f"classes/upcoming_classes/{d.isoformat()}")))
        kb.add(InlineKeyboardButton(gettext("back"), callback_data=nav_cd.new(path="classes")))
        await call.message.edit_text(gettext("upcoming_calendar_title"), reply_markup=kb)
        await call.answer()
        return

    # 3. List of classes for a date
    if path.startswith("classes/upcoming_classes/") and path.count("/") == 2:
        _, _, date_str = path.split("/")
        classes = await get_upcoming_classes(date_str)
        kb = InlineKeyboardMarkup(row_width=1)
        for cls in classes:
            subs = await get_subscribers_for_class(cls.id)
            icon = "✅" if user_id in subs else "➕"
            label = f"{icon} {cls.time} – {cls.name} ({len(subs)} subs)"
            kb.add(InlineKeyboardButton(label, callback_data=nav_cd.new(path=f"classes/upcoming_classes/{date_str}/{cls.id}")))
        kb.add(InlineKeyboardButton(gettext("back"), callback_data=nav_cd.new(path="classes/upcoming_classes")))
        await call.message.edit_text(gettext("classes_on_date").format(date=date_str), reply_markup=kb)
        await call.answer()
        return

    # 4. Toggle enrollment and re-render
    if path.startswith("classes/upcoming_classes/") and path.count("/") == 3:
        _, _, date_str, class_id = path.split("/")
        success = await enroll_user(user_id, class_id)
        text = gettext("enroll_success") if success else gettext("unenroll_success")
        await call.answer(text, show_alert=True)
        classes = await get_upcoming_classes(date_str)
        kb = InlineKeyboardMarkup(row_width=1)
        for cls in classes:
            subs = await get_subscribers_for_class(cls.id)
            icon = "✅" if user_id in subs else "➕"
            label = f"{icon} {cls.time} – {cls.name} ({len(subs)} subs)"
            kb.add(InlineKeyboardButton(label, callback_data=nav_cd.new(path=f"classes/upcoming_classes/{date_str}/{cls.id}")))
        kb.add(InlineKeyboardButton(gettext("back"), callback_data=nav_cd.new(path="classes/upcoming_classes")))
        await call.message.edit_text(gettext("classes_on_date").format(date=date_str), reply_markup=kb)
        return

    # 5. Fallback navigation
    node_list = MENU_STRUCTURE
    if path:
        for segment in path.split("/"):
            try:
                node = next(item for item in node_list if item["key"] == segment)
            except StopIteration:
                await call.answer(gettext("invalid_path"), show_alert=True)
                node_list = MENU_STRUCTURE
                path = ""
                break
            node_list = node.get("children", [])

    kb = build_menu(node_list, user_role=user_role, path=path)
    breadcrumb_parts = path.split("/")
    breadcrumb_key = breadcrumb_parts[-1] if breadcrumb_parts else "main_menu_title"
    breadcrumb_text = gettext("breadcrumb_prefix").format(crumb=gettext(breadcrumb_key))
    try:
        await call.message.edit_text(breadcrumb_text, reply_markup=kb)
    except MessageNotModified:
        pass
    await call.answer()

def register_navigation(dp: Dispatcher):
    dp.register_callback_query_handler(navigate, nav_cd.filter())
