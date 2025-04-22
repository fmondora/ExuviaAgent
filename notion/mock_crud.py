from .schemas import UserPage, ClassPage
from models.roles import Role
import datetime
from typing import List, Dict
from config import (
    USER_TG_ID_FRANCESCO,
    USER_TG_ID_LUCIA,
    USER_TG_ID_MANUEL,
    CLASS_MAX_CAPACITY
)

# In‐memory mock storage
today = datetime.date.today()
mock_classes: Dict[str, List[ClassPage]] = {}
mock_subscriptions: Dict[str, List[int]] = {}
mock_waiting_list: Dict[str, List[int]] = {}

# 1) Genera le classi per i prossimi 7 giorni
for i in range(7):
    d = today + datetime.timedelta(days=i)
    date_str = d.isoformat()
    class_page = ClassPage(
        id=str(i),
        name=f"Demo Class {date_str}",
        time="10:00",
        date=date_str,
        location="Online",
        capacity=CLASS_MAX_CAPACITY,
        spots_left=CLASS_MAX_CAPACITY,          # ← virgola corretta qui
        subscriptions=[],                       # inizialmente vuote
        waiting_list=[]                         # inizialmente vuote
    )
    mock_classes[date_str] = [class_page]

    # Imposta mock_subscriptions: classe '1' piena, altre alternano iscritti
    if i == 1:
        mock_subscriptions[class_page.id] = [
            USER_TG_ID_MANUEL,
            1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888
        ]
    else:
        mock_subscriptions[class_page.id] = (
            [USER_TG_ID_FRANCESCO, USER_TG_ID_LUCIA]
            if i % 2 == 0 else
            [USER_TG_ID_MANUEL]
        )

    # Calcola posti rimasti
    class_page.spots_left = CLASS_MAX_CAPACITY - len(mock_subscriptions[class_page.id])

    # Inizializza lista d’attesa vuota
    mock_waiting_list[class_page.id] = []

# 2) Utenti mock
mock_users: Dict[int, UserPage] = {
    USER_TG_ID_FRANCESCO: UserPage(
        id=str(USER_TG_ID_FRANCESCO),
        telegram_id=USER_TG_ID_FRANCESCO,
        first_name="Francesco",
        last_name="Mondora",
        role=Role.PREMIUM.value,
        subscriptions=[cid for cid, subs in mock_subscriptions.items() if USER_TG_ID_FRANCESCO in subs],
        waiting_list=[cid for cid, wl in mock_waiting_list.items() if USER_TG_ID_FRANCESCO in wl]
    ),
    USER_TG_ID_LUCIA: UserPage(
        id=str(USER_TG_ID_LUCIA),
        telegram_id=USER_TG_ID_LUCIA,
        first_name="Lucia",
        last_name="Longoni",
        role=Role.FREE.value,
        subscriptions=[cid for cid, subs in mock_subscriptions.items() if USER_TG_ID_LUCIA in subs],
        waiting_list=[cid for cid, wl in mock_waiting_list.items() if USER_TG_ID_LUCIA in wl]
    ),
    USER_TG_ID_MANUEL: UserPage(
        id=str(USER_TG_ID_MANUEL),
        telegram_id=USER_TG_ID_MANUEL,
        first_name="Manuel",
        last_name="Mario",
        role=Role.FREE.value,
        subscriptions=[cid for cid, subs in mock_subscriptions.items() if USER_TG_ID_MANUEL in subs],
        waiting_list=[cid for cid, wl in mock_waiting_list.items() if USER_TG_ID_MANUEL in wl]
    ),
}

# 3) Funzioni CRUD mock

async def get_or_create_user(telegram_id: int, default_role: Role = Role.FREE) -> UserPage:
    if telegram_id not in mock_users:
        # Crea utente anonimo
        mock_users[telegram_id] = UserPage(
            id=str(telegram_id),
            telegram_id=telegram_id,
            first_name="Anonymous",
            last_name="User",
            role=default_role.value,
            subscriptions=[],
            waiting_list=[]
        )
    return mock_users[telegram_id]

async def get_user_role(telegram_id: int) -> Role:
    user = await get_or_create_user(telegram_id)
    return Role(user.role)

async def get_my_classes(telegram_id: int) -> List[ClassPage]:
    # Include sia le classi iscritte che quelle in waiting
    result: List[ClassPage] = []
    for day_classes in mock_classes.values():
        for cls in day_classes:
            if telegram_id in mock_subscriptions.get(cls.id, []) \
               or telegram_id in mock_waiting_list.get(cls.id, []):
                result.append(cls)
    return result

async def get_upcoming_classes(date: str) -> List[ClassPage]:
    return mock_classes.get(date, [])

async def get_subscribers_for_class(class_id: str) -> List[int]:
    return mock_subscriptions.get(class_id, [])

async def get_waiting_list(class_id: str) -> List[int]:
    return mock_waiting_list.get(class_id, [])

async def get_my_class_status(telegram_id: int, class_id: str) -> str:
    if telegram_id in mock_subscriptions.get(class_id, []):
        return "enrolled"
    if telegram_id in mock_waiting_list.get(class_id, []):
        return "waiting"
    return "none"

async def enroll_user(telegram_id: int, class_id: str) -> str:
    subs = mock_subscriptions.setdefault(class_id, [])
    waiting = mock_waiting_list.setdefault(class_id, [])

    if telegram_id in subs:
        subs.remove(telegram_id)
        return "unenrolled"

    if len(subs) < CLASS_MAX_CAPACITY:
        subs.append(telegram_id)
        return "enrolled"

    if telegram_id in waiting:
        waiting.remove(telegram_id)
        return "unwaiting"

    waiting.append(telegram_id)
    return "waiting"

# Alias per compatibilità
get_classes_for_date = get_upcoming_classes
