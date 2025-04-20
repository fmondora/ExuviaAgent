import logging
from aiogram import executor, Dispatcher
from config import bot, storage, i18n
from handlers.start import register_start
from handlers.navigation import register_navigation
from handlers.schedule import register_schedule
from handlers.classes import register_classes  


# Abilita logging per vedere gli update in console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crea Dispatcher e registra middleware e handler
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(i18n)
register_start(dp)
register_navigation(dp)
register_schedule(dp)
register_classes(dp)  

async def on_startup(dispatcher: Dispatcher):
    me = await bot.get_me()
    logger.info(f"🚀 ExuviaAgent avviato come @{me.username} (ID: {me.id})")

if __name__ == "__main__":
    print("ExuviaAgent è in esecuzione…")
    # skip_updates=True ignora messaggi non letti durante downtime
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
