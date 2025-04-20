from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
import datetime
from notion.crud import get_user_role, get_classes_for_date, enroll_user
from config import _

schedule_cd = CallbackData("sched", "level", "week_id", "date", "class_id")

async def show_schedule(message: types.Message):
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    kb = await menu_week(week_start)
    await message.answer(_("📅 Seleziona un giorno:"), reply_markup=kb)

async def menu_week(week_start: datetime.date) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=4)
    for i in range(7):
        day = week_start + datetime.timedelta(days=i)
        label = day.strftime("%a %d/%m")
        kb.insert(
            InlineKeyboardButton(
                label,
                callback_data=schedule_cd.new(
                    level="day",
                    week_id=week_start.isoformat(),
                    date=day.isoformat(),
                    class_id=""
                )
            )
        )
    prev_w = (week_start - datetime.timedelta(days=7)).isoformat()
    next_w = (week_start + datetime.timedelta(days=7)).isoformat()
    kb.row(
        InlineKeyboardButton(_("◀️ Settimana prec."), callback_data=schedule_cd.new(level="week", week_id=prev_w, date="", class_id="")),
        InlineKeyboardButton(_("Settimana succ. ▶️"), callback_data=schedule_cd.new(level="week", week_id=next_w, date="", class_id=""))
    )
    return kb

async def on_day_selected(call: types.CallbackQuery, callback_data: dict):
    date = callback_data["date"]
    classes = await get_classes_for_date(date)
    kb = InlineKeyboardMarkup(row_width=1)
    for cls in classes:
        kb.add(
            InlineKeyboardButton(
                f"{cls.time} – {cls.name}",
                callback_data=schedule_cd.new(level="class", week_id=callback_data["week_id"], date=date, class_id=cls.id)
            )
        )
    kb.add(InlineKeyboardButton(_("◀️ Indietro"), callback_data=schedule_cd.new(level="week", week_id=callback_data["week_id"], date="", class_id="")))
    await call.message.edit_text(_("📅 Classi disponibili per il {date}").format(date=date), reply_markup=kb)
    await call.answer()

async def on_class_selected(call: types.CallbackQuery, callback_data: dict):
    class_id = callback_data["class_id"]
    # Dettagli eventuali
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(_("✅ Iscrivimi"), callback_data=schedule_cd.new(level="enroll", week_id=callback_data["week_id"], date=callback_data["date"], class_id=class_id)))
    kb.add(InlineKeyboardButton(_("◀️ Indietro"), callback_data=schedule_cd.new(level="day", week_id=callback_data["week_id"], date=callback_data["date"], class_id="")))
    await call.message.edit_text(_("Dettagli classe {class_id}").format(class_id=class_id), reply_markup=kb)
    await call.answer()

async def on_enroll(call: types.CallbackQuery, callback_data: dict):
    await enroll_user(call.from_user.id, callback_data["class_id"])
    await call.answer(_("Iscrizione avvenuta con successo! 💪"), show_alert=True)


def register_schedule(dp: Dispatcher):
    dp.register_message_handler(show_schedule, commands=["schedule"])
    dp.register_callback_query_handler(on_day_selected, schedule_cd.filter(level="day"))
    dp.register_callback_query_handler(on_class_selected, schedule_cd.filter(level="class"))
    dp.register_callback_query_handler(on_enroll, schedule_cd.filter(level="enroll"))