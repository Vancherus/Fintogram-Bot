from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

all_chains = ['🪐 НепTON', '💠 ETHирида', '🧊 BITкурий', '🛰️ ПлуTRON', '🌞 SOLнце'] # chain list

class MenuCallback(CallbackData, prefix="menu"): 
    level: int
    menu_name: str
    
class ChainCallback(CallbackData, prefix='chain'):
    name: str        

def get_menu_with_back(*, level: int, current: str, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    if current == 'chains':
        # Show a list of networks and the "Back" button
        for chain in all_chains:
            keyboard.add(InlineKeyboardButton(
                text=chain,
                callback_data=ChainCallback(name=chain).pack()  # or create a separate CallbackData
            ))
        keyboard.add(InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=MenuCallback(level=level - 1, menu_name="main").pack()
        ))
    else:
        # Regular menu
        buttons = {
            "🧠 Мои мыслеформы": "my_thoughts",
            "👤 Мои данные": "my_data",
            "🌐 Веб-сайт": "website",
            "📎 Ссылки": "links",
            "🔗 Доступные блокчейны": 'chains',
        }

        for text, menu in buttons.items():
            if menu == "website":
                keyboard.add(InlineKeyboardButton(
                    text=text,
                    url="https://example.com"
                ))
            elif menu == current:
                keyboard.add(InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data=MenuCallback(level=level - 1, menu_name="main").pack()
                ))
            else:
                keyboard.add(InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallback(level=level, menu_name=menu).pack()
                ))

    return keyboard.adjust(*sizes).as_markup()