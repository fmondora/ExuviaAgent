from config import APP_ENV

if APP_ENV == 'development':
    # In sviluppo, usa il mock completo
    from .mock_crud import (
        get_or_create_user,
        get_user_role,
        get_my_classes,
        get_upcoming_classes,
        get_subscribers_for_class,
        get_waiting_list,
        get_my_class_status,
        enroll_user,
        get_classes_for_date
    )

else:
    # In produzione, chiamate reali a Notion
    from config import notion_client, NOTION_DB_USERS, NOTION_DB_CLASSES
    from .schemas import UserPage, ClassPage
    from models.roles import Role
    from typing import List

    def _page_to_user(page) -> UserPage:
        props = page["properties"]
        return UserPage(
            id=page["id"],
            telegram_id=int(props["Telegram ID"]["number"]),
            first_name=props["Firstname"]["rich_text"][0]["plain_text"] if props["Firstname"]["rich_text"] else "",
            last_name=props["Surname"]["rich_text"][0]["plain_text"] if props["Surname"]["rich_text"] else "",
            role=props["Role"]["select"]["name"].lower() if props["Role"]["select"] else Role.FREE.value,
            subscriptions=[r["id"] for r in props["Classes"]["relation"]],
            waiting_list=[r["id"] for r in props["WaitinglistInClass"]["relation"]],
        )

    def _page_to_class(page) -> ClassPage:
        props = page["properties"]
        subs = props["Subscriptions"]["relation"]
        wait = props["Waitinglist"]["relation"]
        return ClassPage(
            id=page["id"],
            name=props["Name"]["title"][0]["plain_text"] if props["Name"]["title"] else "",
            date=props["Date"]["date"]["start"] or "",
            time=props["Class time"]["select"]["name"] if props["Class time"]["select"] else "",
            location=props["Location"]["select"]["name"] if props["Location"]["select"] else "",
            capacity=int(props["Capacity"]["number"] or 0),
            spots_left=int(props["Spot Left"]["formula"]["number"] or 0),
            subscriptions=[r["id"] for r in subs],
            waiting_list=[r["id"] for r in wait],
            subscribers_count=len(subs),
            waiting_count=len(wait),
        )

    async def get_or_create_user(telegram_id: int) -> UserPage:
        resp = notion_client.databases.query(
            database_id=NOTION_DB_USERS,
            filter={"property": "Telegram ID", "number": {"equals": telegram_id}}
        )
        if resp["results"]:
            return _page_to_user(resp["results"][0])

        page = notion_client.pages.create(
            parent={"database_id": NOTION_DB_USERS},
            properties={
                "Telegram ID": {"number": telegram_id},
                "Name": {"title": [{"text": {"content": f"User {telegram_id}"}}]},
                "Firstname": {"rich_text": []},
                "Surname": {"rich_text": []},
                "Role": {"select": {"name": "Free"}},
                "Classes": {"relation": []},
                "WaitinglistInClass": {"relation": []},
            }
        )
        return _page_to_user(page)

    async def get_user_role(telegram_id: int) -> Role:
        user = await get_or_create_user(telegram_id)
        return Role(user.role)

    async def get_classes_for_date(date_str: str) -> List[ClassPage]:
        resp = notion_client.databases.query(
            database_id=NOTION_DB_CLASSES,
            filter={"property": "Date", "date": {"equals": date_str}}
        )
        return [_page_to_class(p) for p in resp["results"]]

    async def get_my_classes(telegram_id: int) -> List[ClassPage]:
        resp = notion_client.databases.query(
            database_id=NOTION_DB_USERS,
            filter={"property": "Telegram ID", "number": {"equals": telegram_id}}
        )
        if not resp["results"]:
            return []

        class_rels = resp["results"][0]["properties"]["Classes"]["relation"]
        classes = []
        for rel in class_rels:
            page = notion_client.pages.retrieve(rel["id"])
            classes.append(_page_to_class(page))
        return classes

    # alias
    get_upcoming_classes = get_classes_for_date

    async def get_subscribers_for_class(class_id: str) -> List[int]:
        # per dettagli, recupera telegram_id di ogni utente
        cls = notion_client.pages.retrieve(class_id)
        rels = cls["properties"]["Subscriptions"]["relation"]
        telegrams = []
        for r in rels:
            user_page = notion_client.pages.retrieve(r["id"])
            telegrams.append(int(user_page["properties"]["Telegram ID"]["number"]))
        return telegrams

    async def get_waiting_list(class_id: str) -> List[int]:
        cls = notion_client.pages.retrieve(class_id)
        rels = cls["properties"]["Waitinglist"]["relation"]
        telegrams = []
        for r in rels:
            user_page = notion_client.pages.retrieve(r["id"])
            telegrams.append(int(user_page["properties"]["Telegram ID"]["number"]))
        return telegrams

    async def get_my_class_status(telegram_id: int, class_id: str) -> str:
        subs = await get_subscribers_for_class(class_id)
        waiting = await get_waiting_list(class_id)
        if telegram_id in subs:
            return "enrolled"
        if telegram_id in waiting:
            return "waiting"
        return "none"

    async def enroll_user(telegram_id: int, class_id: str) -> str:
        user = await get_or_create_user(telegram_id)
        uid = user.id

        cls_page = notion_client.pages.retrieve(class_id)
        props = cls_page["properties"]

        subs = [r["id"] for r in props["Subscriptions"]["relation"]]
        waiting = [r["id"] for r in props["Waitinglist"]["relation"]]
        spots_left = int(props["Spot Left"]["formula"]["number"] or 0)

        # unenroll
        if uid in subs:
            subs.remove(uid)
            notion_client.pages.update(
                page_id=class_id,
                properties={"Subscriptions": {"relation": [{"id": s} for s in subs]}}
            )
            if waiting:
                p = waiting.pop(0)
                subs.append(p)
                notion_client.pages.update(
                    page_id=class_id,
                    properties={
                        "Subscriptions": {"relation": [{"id": s} for s in subs]},
                        "Waitinglist": {"relation": [{"id": w} for w in waiting]}
                    }
                )
            return "unenrolled"

        # enroll
        if spots_left > 0:
            subs.append(uid)
            notion_client.pages.update(
                page_id=class_id,
                properties={"Subscriptions": {"relation": [{"id": s} for s in subs]}}
            )
            return "enrolled"

        # unwaiting
        if uid in waiting:
            waiting.remove(uid)
            notion_client.pages.update(
                page_id=class_id,
                properties={"Waitinglist": {"relation": [{"id": w} for w in waiting]}}
            )
            return "unwaiting"

        # waiting
        waiting.append(uid)
        notion_client.pages.update(
            page_id=class_id,
            properties={"Waitinglist": {"relation": [{"id": w} for w in waiting]}}
        )
        return "waiting"
