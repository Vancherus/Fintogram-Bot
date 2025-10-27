# This module implements helper functions for handlers that process menus. (async def process_menu) and command /start (async def cmd_start)

from database.engine import session_maker
from database.orm_query import orm_get_user_thoughts, User


##################### функции-помощники #####################################

def get_menu_text(menu_name: str, user_first_name: str = "") -> str:
    if menu_name == "main":
        return f"👋 Привет, <b>{user_first_name}</b>! Добро пожаловать в Fintogram — первый космический IdeaFI!\n\n⚠️ ВАЖНО! Для отправки мыслеформы убедитесь, что получатель зашел в бота и у него есть <b>username</b>. ⚠️\n\nЧтобы узнать подробности, введите команду /info."
    elif menu_name == "links":
        return "Здесь вы можете указать необходимые ссылки"
    else:
        return "🔗 Выберите доступный блокчейн и прочтите его описание:"


async def get_user_thoughts_text(user_id: int) -> str:
    async with session_maker() as session:
        thoughts = await orm_get_user_thoughts(session, user_id)

    if thoughts:
        text_lines = ["🧠 Твои мыслеформы <i>(нажмите на ID, чтобы скопировать)</i>:"]
        for thought in thoughts:
            text_lines.append(f"— {thought.content} (ID: <code>{thought.id}</code>)")
        return "\n".join(text_lines)
    else:
        return "У тебя пока нет мыслеформ."

async def get_user_info_text(user_id: int) -> str:
    async with session_maker() as session:
        user = await session.get(User, user_id)  
        thoughts = await orm_get_user_thoughts(session, user_id)

    joined_date = user.created if user else "неизвестно"
    thoughts_count = len(thoughts)
    return f"👤 Ты с нами с {joined_date}.\n🧠 У тебя {thoughts_count} мыслеформ(ы)."