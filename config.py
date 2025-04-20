import os
import logging
from pathlib import Path
from aiogram import Bot, types
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from notion_client import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
dotenv_path = Path(__file__).parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path, override=True, verbose=True)
    logger.info(f"Loaded .env from {dotenv_path}")
else:
    logger.warning(f".env file not found at {dotenv_path}")

# Application environment: 'development' or 'production'
APP_ENV = os.getenv('APP_ENV', 'production')
logger.info(f"Running in {APP_ENV} mode")

# Required environment variables
TELEGRAM_TOKEN    = os.getenv('TELEGRAM_TOKEN')
NOTION_TOKEN      = os.getenv('NOTION_TOKEN')
NOTION_DB_USERS   = os.getenv('NOTION_DB_USERS_ID')
NOTION_DB_CLASSES = os.getenv('NOTION_DB_CLASSES_ID')

#Mock users
USER_TG_ID_FRANCESCO = int(os.getenv("USER_TG_ID_FRANCESCO", 1001))
USER_TG_ID_LUCIA = int(os.getenv("USER_TG_ID_LUCIA", 1002))
USER_TG_ID_MANUEL = int(os.getenv("USER_TG_ID_MANUEL", 1003))

CLASS_MAX_CAPACITY = int(os.getenv("CLASS_MAX_CAPACITY", 9))


# Initialize Telegram Bot
bot = Bot(token=TELEGRAM_TOKEN, parse_mode='HTML')  # use HTML to avoid MarkdownV2 parsing issues

storage = MemoryStorage()
I18N_DOMAIN = 'exuviaagent'
LOCALES_DIR = 'locales'

# Custom localization middleware to use user's language_code
class UILocalization(I18nMiddleware):
    async def get_user_locale(self, action, args):
        user = None
        if isinstance(action, types.Message):
            user = action.from_user
        elif hasattr(action, 'from_user'):
            user = action.from_user
        if user and user.language_code:
            return user.language_code
        return await super().get_user_locale(action, args)

i18n = UILocalization(I18N_DOMAIN, LOCALES_DIR)
_ = i18n.gettext

# Notion client (use in production)
notion_client = Client(auth=NOTION_TOKEN)



