import os
from notion_client import Client
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Inizializza il client Notion
notion = Client(auth=os.getenv("NOTION_TOKEN"))

# ID dei database
NOTION_DB_USERS = os.getenv("NOTION_DB_USERS")
NOTION_DB_CLASSES = os.getenv("NOTION_DB_CLASSES")

def describe_database(db_id, name):
    print(f"\n📘 Schema del database: {name}")
    try:
        db = notion.databases.retrieve(database_id=db_id)
        props = db["properties"]
        for prop_name, prop_data in props.items():
            prop_type = prop_data["type"]
            print(f"• {prop_name} → {prop_type}")
            if prop_type in ["select", "multi_select"]:
                options = prop_data[prop_type].get("options", [])
                option_names = [opt["name"] for opt in options]
                print(f"   ↳ Opzioni: {', '.join(option_names)}")
            elif prop_type == "relation":
                related_db = prop_data["relation"].get("database_id", "N/A")
                print(f"   ↳ Relazione con database ID: {related_db}")
    except Exception as e:
        print(f"Errore nel recupero del database {name}: {e}")

if __name__ == "__main__":
    describe_database(NOTION_DB_USERS, "Users")
    describe_database(NOTION_DB_CLASSES, "Classes")
