from config import APP_ENV, notion_client, NOTION_DB_USERS, NOTION_DB_CLASSES
from typing import List
from .schemas import UserPage, ClassPage
from models.roles import Role

if APP_ENV == 'development':
    from .mock_crud import *
else:
    async def get_or_create_user(telegram_id: int, default_role: Role = Role.FREE) -> UserPage:
        client = notion_client
        response = client.databases.query(
            database_id=NOTION_DB_USERS,
            filter={'property': 'TelegramID', 'number': {'equals': telegram_id}}
        )
        results = response.get('results', [])
        if not results:
            page = client.pages.create(
                parent={'database_id': NOTION_DB_USERS},
                properties={
                    'TelegramID': {'number': telegram_id},
                    'Role': {'select': {'name': default_role.value.capitalize()}}
                }
            )
        else:
            page = results[0]
        return UserPage(
            id=page['id'],
            telegram_id=page['properties']['TelegramID']['number'],
            role=page['properties']['Role']['select']['name'].lower()
        )

    async def get_user_role(telegram_id: int) -> Role:
        user_page = await get_or_create_user(telegram_id)
        return Role(user_page.role)

    async def set_user_role(telegram_id: int, new_role: Role):
        user_page = await get_or_create_user(telegram_id)
        notion_client.pages.update(
            page_id=user_page.id,
            properties={'Role': {'select': {'name': new_role.value.capitalize()}}}
        )

    async def get_classes_for_date(date: str) -> List[ClassPage]:
        client = notion_client
        response = client.databases.query(
            database_id=NOTION_DB_CLASSES,
            filter={'property': 'Date', 'date': {'equals': date}}
        )
        return [
            ClassPage(
                id=record['id'],
                name=record['properties']['Name']['title'][0]['plain_text'],
                time=record['properties']['Time']['rich_text'][0]['plain_text'],
                date=record['properties']['Date']['date']['start'],
                location=record['properties']['Location']['rich_text'][0]['plain_text'],
                spots_left=record['properties']['SpotsLeft']['number']
            ) for record in response.get('results', [])
        ]

    async def enroll_user(telegram_id: int, class_id: str) -> bool:
        # TODO: implement real enrollment logic
        return True