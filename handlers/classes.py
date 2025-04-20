from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from notion.crud import get_my_classes, get_subscribers_for_class, enroll_user
from config import _
import datetime

classes_cd = CallbackData('classes', 'action', 'date', 'class_id')

async def cq_my_classes(call: types.CallbackQuery, callback_data: dict):
    """Show the list of classes the user is subscribed to."""
    user_id = call.from_user.id
    classes = await get_my_classes(user_id)
    kb = InlineKeyboardMarkup(row_width=1)
    for cls in classes:
        subs = await get_subscribers_for_class(cls.id)
        # Show class + subscriber count
        kb.add(InlineKeyboardButton(
            f"{cls.date} {cls.time} – {cls.name} ({len(subs)} subs)",
            callback_data=classes_cd.new(action='details', date=cls.date, class_id=cls.id)
        ))
        # Allow deregistration
        kb.add(InlineKeyboardButton(
            _('unenroll_success'),  # e.g. “Unenroll”
            callback_data=classes_cd.new(action='toggle', date=cls.date, class_id=cls.id)
        ))
    # Back to main “Classes” menu
    kb.add(InlineKeyboardButton(
        _('back'),
        callback_data=classes_cd.new(action='back', date='', class_id='')
    ))
    await call.message.edit_text(_('my_classes_title'), reply_markup=kb)
    await call.answer()

def register_classes(dp: Dispatcher):
    # message handler (optional) if you still want /my_classes
    dp.register_message_handler(cq_my_classes, commands=['my_classes'])
    # callback handler for the inline button “My Classes”
    dp.register_callback_query_handler(
        cq_my_classes,
        classes_cd.filter(action='my_classes')
    )