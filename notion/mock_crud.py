from .schemas import UserPage, ClassPage
from models.roles import Role
import datetime
from typing import List, Dict
from config import USER_TG_ID_FRANCESCO, USER_TG_ID_LUCIA, USER_TG_ID_MANUEL

# In-memory mock storage for development
today = datetime.date.today()
mock_classes: Dict[str, List[ClassPage]] = {}
mock_subscriptions: Dict[str, List[int]] = {}

# Generate mock classes for next 7 days and subscriptions
for i in range(7):
    d = today + datetime.timedelta(days=i)
    date_str = d.isoformat()
    class_page = ClassPage(
        id=str(i),
        name=f"Demo Class {date_str}",
        time="10:00",
        date=date_str,
        location="Online",
        spots_left=5
    )
    mock_classes[date_str] = [class_page]
    # Even days: Francesco and Lucia subscribed
    if i % 2 == 0:
        mock_subscriptions[class_page.id] = [28576633, 5941599694]
    else:
        # Odd days: Manuel subscribed
        mock_subscriptions[class_page.id] = [1003]

# Predefined mock users with correct roles

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
        role=Role.FREE.value,
        full_name="Manuel Mario"
    ),
}


async def get_or_create_user(telegram_id: int, default_role: Role = Role.FREE) -> UserPage:
    if telegram_id not in mock_users:
        mock_users[telegram_id] = UserPage(
            id=str(telegram_id),
            telegram_id=telegram_id,
            role=default_role.value,
            full_name="Anonymous"
        )
    return mock_users[telegram_id]

async def get_user_role(telegram_id: int) -> Role:
    user = await get_or_create_user(telegram_id)
    return Role(user.role)

async def get_my_classes(telegram_id: int) -> List[ClassPage]:
    results: List[ClassPage] = []
    for classes in mock_classes.values():
        for cls in classes:
            if telegram_id in mock_subscriptions.get(cls.id, []):
                results.append(cls)
    return results

async def get_upcoming_classes(date: str) -> List[ClassPage]:
    return mock_classes.get(date, [])

async def get_subscribers_for_class(class_id: str) -> List[int]:
    return mock_subscriptions.get(class_id, [])

async def enroll_user(telegram_id: int, class_id: str) -> bool:
    subs = mock_subscriptions.setdefault(class_id, [])
    if telegram_id in subs:
        subs.remove(telegram_id)
        return False
    subs.append(telegram_id)
    return True

# Alias for compatibility with schedule handler
get_classes_for_date = get_upcoming_classes