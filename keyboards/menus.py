from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from config import i18n
from models.roles import Role

_ = i18n.lazy_gettext

# Callback data per la navigazione dei menu
nav_cd = CallbackData("nav", "path")

# Tipo per un nodo di menu
MenuNode = Dict[str, Any]

def make_node(key: str, roles: List[Role], children: List[MenuNode] = None) -> MenuNode:
    return {
        "key": key,
        "title": _(key),  # traduzione lazy
        "roles": roles,
        "children": children or []
    }

# Struttura principale del menu
MENU_STRUCTURE: List[MenuNode] = [
    make_node("sign_up_today",   [Role.FREE, Role.PREMIUM, Role.ADMIN]),
    make_node("view_wod",        [Role.FREE, Role.PREMIUM, Role.ADMIN]),
    make_node("classes",         [Role.FREE, Role.PREMIUM, Role.ADMIN], children=[
        make_node("my_classes",       [Role.PREMIUM, Role.ADMIN]),
        make_node("upcoming_classes", [Role.FREE, Role.PREMIUM, Role.ADMIN]),
    ]),
    make_node("progress",        [Role.FREE, Role.PREMIUM, Role.ADMIN], children=[
        make_node("view_maxes",       []),
        make_node("update_maxes",     []),
        make_node("wod_history",      []),
        make_node("statistics",       []),
    ]),
    make_node("profile",         [Role.FREE, Role.PREMIUM, Role.ADMIN], children=[
        make_node("view_profile",       []),
        make_node("subscription",       []),
        make_node("renew",              []),
        make_node("certificate",        []),
        make_node("upload_certificate", []),
    ]),
    make_node("settings",        [Role.FREE, Role.PREMIUM, Role.ADMIN], children=[
        make_node("reminders",    []),
        make_node("language",     []),
        make_node("community",    []),
    ]),
]

def build_menu(subtree: List[MenuNode], user_role: Role, path: str = "") -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for node in subtree:
        if node["roles"] and user_role not in node["roles"]:
            continue
        title = node["title"]
        new_path = f"{path}/{node['key']}" if path else node["key"]
        kb.add(InlineKeyboardButton(title, callback_data=nav_cd.new(path=new_path)))
    if path:
        parent_path = "/".join(path.split("/")[:-1])
        kb.add(InlineKeyboardButton(_("back"), callback_data=nav_cd.new(path=parent_path)))
    return kb
