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

# In-memory mock storage
today = datetime.date.today()
mock_classes: Dict[str, List[ClassPage]] = {}
mock_subscriptions: Dict[str, List[int]] = {}
mock_waiting_list: Dict[str, List[int]] = {}

# Generate mock classes for next 7 days
for i in range(7):
    d = today + datetime.timedelta(days=i)
    date_str = d.isoformat()
    class_page = ClassPage(
        id=str(i),
        name=f"Demo Class {date_str}",
        time="10:00",
        date=date_str,
        location="Online",
        spots_left=CLASS_MAX_CAPACITY  # Impostato inizialmente al massimo
    )
    mock_classes[date_str] = [class_page]

    # Imposta 9 iscritti per la classe del secondo giorno (i == 1), senza Francesco e Lucia
    if i == 1:
        mock_subscriptions[class_page.id] = [
            USER_TG_ID_MANUEL,  # Solo Manuel
            1111, 2222, 3333, 4444, 5555, 6666, 7777, 8888  # 8 utenti fittizi per arrivare a 9
        ]
    else:
        # Alternate subscription pattern per le altre classi
        mock_subscriptions[class_page.id] = (
            [USER_TG_ID_FRANCESCO, USER_TG_ID_LUCIA]
            if i % 2 == 0 else
            [USER_TG_ID_MANUEL]
        )

    # Aggiorna spots_left in base agli iscritti
    class_page.spots_left = CLASS_MAX_CAPACITY - len(mock_subscriptions[class_page.id])

    mock_waiting_list[class_page.id] = []

# Predefined mock users
mock_users: Dict[int, UserPage] = {
    USER_TG_ID_FRANCESCO: UserPage(
        id=str(USER_TG_ID_FRANCESCO),
        telegram_id=USER_TG_ID_FRANCESCO,
        role=Role.PREMIUM.value,
        full_name="Francesco Mondora"
    ),
    USER_TG_ID_LUCIA: UserPage(
        id=str(USER_TG_ID_LUCIA),
        telegram_id=USER_TG_ID_LUCIA,
        role=Role.FREE.value,
        full_name="Lucia Longoni"
    ),
    USER_TG_ID_MANUEL: UserPage(
        id=str(USER_TG_ID_MANUEL),
        telegram_id=USER_TG_ID_MANUEL,
        role=Role.PREMIUM.value,
        full_name="Manuel Mario"
    ),
}

# Get or create mock user
async def get_or_create_user(telegram_id: int, default_role: Role = Role.FREE) -> UserPage:
    if telegram_id not in mock_users:
        mock_users[telegram_id] = UserPage(
            id=str(telegram_id),
            telegram_id=telegram_id,
            role=default_role.value,
            full_name="Anonymous"
        )
    return mock_users[telegram_id]

# Get role
async def get_user_role(telegram_id: int) -> Role:
    user = await get_or_create_user(telegram_id)
    return Role(user.role)

# Get classes where user is subscribed
async def get_my_classes(telegram_id: int) -> List[ClassPage]:
    results: List[ClassPage] = []
    for classes in mock_classes.values():
        for cls in classes:
            is_subscribed = telegram_id in mock_subscriptions.get(cls.id, [])
            is_waiting = telegram_id in mock_waiting_list.get(cls.id, [])
            if is_subscribed or is_waiting:
                results.append(cls)
    return results


# Get class for a day
async def get_upcoming_classes(date: str) -> List[ClassPage]:
    return mock_classes.get(date, [])

# Get subscribers
async def get_subscribers_for_class(class_id: str) -> List[int]:
    return mock_subscriptions.get(class_id, [])

# Get waiting list
async def get_waiting_list(class_id: str) -> List[int]:
    return mock_waiting_list.get(class_id, [])

# Get my class status
async def get_my_class_status(telegram_id: int, class_id: str) -> str:
    if telegram_id in mock_subscriptions.get(class_id, []):
        return "enrolled"
    if telegram_id in mock_waiting_list.get(class_id, []):
        return "waiting"
    return "none"


# Enroll logic with waiting list
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

# Alias
get_classes_for_date = get_upcoming_classes