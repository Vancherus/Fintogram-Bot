from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='✍ Добавить мыслеформу'),
         KeyboardButton(text='🗑️ Удалить мыслеформу')
        ],
        [KeyboardButton(text='📧 Поделиться мыслеформой')]
    ], resize_keyboard=True
)

transfer_kb = [
        [KeyboardButton(text="🪐 НепTON"),
        KeyboardButton(text="💠 ETHирида")],
        [KeyboardButton(text="🧊 BITкурий"),
        KeyboardButton(text="🛰️ ПлуTRON")],
        [KeyboardButton(text="🌞 SOLнце")]
        
    ]

