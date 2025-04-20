from dotenv import load_dotenv
import os

dotenv_path = "/Users/fmondora/wip/ExuviaAgent/.env"
load_dotenv(dotenv_path,override=True, verbose=True)

print("Directory corrente:", os.getcwd())
print("TELEGRAM_TOKEN:", os.getenv("TELEGRAM_TOKEN"))
