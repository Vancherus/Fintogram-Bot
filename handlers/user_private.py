from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

from common.services import get_menu_text, get_user_thoughts_text, get_user_info_text

from database.orm_query import (orm_add_thought, 
                                orm_get_user_by_username,
                                orm_delete_thought,
                                orm_transfer_thought,
                                orm_get_thought_by_id,
                                has_been_transferred,
                                User
                                )

from kbds.inline import MenuCallback, get_menu_with_back, ChainCallback # inline_chains
from kbds.reply import start_kb, transfer_kb

from database.engine import session_maker

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from statemachine.states import ThoughtStates, TransferStates, DeleteStates


user_private_router = Router()


##################### INLINE 1 #####################################

@user_private_router.message(CommandStart()) # handler for /start
async def cmd_start(message: Message):
    
    # Основное меню с inline-кнопками
    text = get_menu_text("main", user_first_name=message.from_user.first_name)
    markup = get_menu_with_back(level=0, current="main")
    await message.answer(text, reply_markup=markup) # inline-buttons
    
    # Доп. сообщение с reply-кнопками
    await message.answer("Выберите команду:", reply_markup=start_kb) 
    

########################################################

@user_private_router.callback_query(MenuCallback.filter())
async def process_menu(callback: CallbackQuery, callback_data: MenuCallback):
    menu_name = callback_data.menu_name
    level = callback_data.level
    user_id = callback.from_user.id

    if menu_name == "my_thoughts":
        text = await get_user_thoughts_text(user_id)
    elif menu_name == "my_data":
        text = await get_user_info_text(user_id)  
    else:
        text = get_menu_text(menu_name, user_first_name=callback.from_user.first_name)

    markup = get_menu_with_back(level=level, current=menu_name)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    
##################### INLINE 2 #####################################
    
# Словарь описаний сетей
CHAIN_DESCRIPTIONS = {
    '🪐 НепTON': '🪐 НепTON — второе поколение блокчейна TON. Назван в честь далёкой ледяной планеты. Газ минимален, сигналы проходят мгновенно.',
    '💠 ETHирида': '💠 ETHирида — мастодонт галактического DeFi. Валидаторы первой версии ETH считаются одними из самых могущественных в Галактике. Вышел в эфир ещё в 2015 году.',
    '🧊 BITкурий': '🧊 BITкурий — холодный, быстрый и старый потомок Великого Первоблокa. Выбирают те, кто ценит надёжность биткоина, но не готов ждать эпоху подтверждений.',
    '🛰️ ПлуTRON': '🛰️ ПлуTRON — Децентрализованная блокчейн-платформа, где космо-пользователи участвуют в голосованиях и запускают DAO-станции. Иногда там бывает весело.',
    '🌞 SOLнце': '🌞 SOLнце — поговаривают, на первом поколении этого блокчейна проходили одни из самых горячих транзакций. Известен скоростью, как у света. Ярчайшая звезда в системе блокчейнов.'
}

@user_private_router.callback_query(ChainCallback.filter())
async def chain_selected_handler(callback: CallbackQuery, callback_data: ChainCallback):
    chain_name = callback_data.name
    description = CHAIN_DESCRIPTIONS.get(chain_name, "Описание пока недоступно.")

    # Кнопка Назад к списку сетей
    back_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=MenuCallback(level=1, menu_name="chains").pack()
            )
        ]
    ])

    await callback.message.edit_text(
        text=f"<b>{chain_name}</b>\n\n{description}",
        reply_markup=back_markup,
        parse_mode="HTML"
    )    
##################### REPLY #####################################    
    
##################### FSM-handlers #######################################    
    
# We're processing the reply button "✍ Добавить мыслеформу"
@user_private_router.message(F.text == "✍ Добавить мыслеформу")
async def prompt_for_thought(message: Message, state: FSMContext):
    await message.answer("Введите текст новой мыслеформы:")
    await state.set_state(ThoughtStates.writing)    
    
@user_private_router.message(ThoughtStates.writing)
async def save_thought(message: Message, state: FSMContext, session: AsyncSession):
    # Check if the message is a command or the text of another reply button
    if message.text in ["📧 Поделиться мыслеформой", "✍️ Добавить мыслеформу", "🗑️ Удалить мыслеформу"]:
        await message.answer("Вы начали другое действие. Ввод мыслеформы отменен.")
        await state.clear()  
        return
    
    text = message.text.strip() # type: ignore
    
    if not text:
        await message.answer("Пожалуйста, введите текст мыслеформы.")
        return

    if len(text) > 500:
        await message.answer("Слишком длинная мыслеформа. Пожалуйста, сократите до 500 символов.")
        return

    try:
        await orm_add_thought(session, message.from_user.id, text)
        await message.answer("✅ Ваша мыслеформа успешно сохранена!")
    except Exception as e:
        await message.answer("❌ Произошла ошибка при сохранении мыслеформы. Пожалуйста, введите текст или попробуйте еще раз.")
        # logging:
        print(f"[Ошибка] Не удалось сохранить мыслеформу: {e}")

    await state.clear()    
    
# We're processing the reply button "📧 Поделиться мыслеформой"  
@user_private_router.message(F.text == "📧 Поделиться мыслеформой")
async def start_transfer(message: Message, state: FSMContext):
    await message.answer("Введите юзернейм и ID мыслеформы через пробел в формате:\n@username S0kr_JTZZzk")
    await state.set_state(TransferStates.input_username_and_thought_id)
    
@user_private_router.message(TransferStates.input_username_and_thought_id)
async def process_input(message: Message, state: FSMContext):
    # Check if the message is a command or the text of another reply button
    if message.text in ["📧 Поделиться мыслеформой", "✍️ Добавить мыслеформу", "🗑️ Удалить мыслеформу"]:
        await message.answer("Вы начали другое действие. Удаление мыслеформы отменено.")
        await state.clear()  # Очищаем состояние
        return
    
    try:
        username, thought_id = message.text.strip().split()
    except ValueError:
        return await message.answer("Неверный формат. Используйте: @username S0kr_JTZZzk")

    # check: does the sender have such a thoughtform?
    # check: is the recipient registered?

    await state.update_data(recipient_username=username, thought_id=thought_id)  
    
    await message.answer("Выберите блокчейн:", reply_markup=ReplyKeyboardMarkup(keyboard=transfer_kb, resize_keyboard=True))
    await state.set_state(TransferStates.choosing_blockchain) 

@user_private_router.message(TransferStates.choosing_blockchain)
async def choose_blockchain(message: Message, state: FSMContext, bot: Bot):

    blockchain = message.text.strip()
    data = await state.get_data()
    recipient_username = data["recipient_username"]
    thought_id = data["thought_id"]

    if recipient_username.startswith("@"):
        recipient_username = recipient_username[1:]

    await state.update_data(blockchain=blockchain)

    # Get the recipient's user_id by username
    async with session_maker() as session:
        recipient = await orm_get_user_by_username(session, recipient_username)
    
    if not recipient:
        await message.answer("Пользователя нет в боте или вы ввели несуществующий юзернейм. Попробуйте отправить мыслеформу еще раз.", reply_markup=start_kb)
        await state.clear()
        return  
    
    # Checking whether such a thought form exists
    async with session_maker() as session:
        thought = await orm_get_thought_by_id(session, thought_id)

    if not thought:
        await message.answer("❌ Мыслеформа с таким ID не найдена.", reply_markup=start_kb)
        await state.clear()
        return
    
    # 🔒 Check: has this thought form already been transferred to this recipient?
    async with session_maker() as session:
        already_transferred = await has_been_transferred(session, thought_id, recipient_username)

    if already_transferred:
        await message.answer(
            f"⚠️ Вы уже отправляли эту мыслеформу пользователю @{recipient_username}.",
            reply_markup=start_kb
        )
        await state.clear()
        return
    
    recipient_id = recipient.id
    
    sender = message.from_user
    sender_link = (f"@{sender.username}" if sender.username else f'<a href="tg://user?id={sender.id}">Пользователь</a>')
    await bot.send_message(
        recipient_id,
        f"{sender_link} хочет передать вам мыслеформу с ID: `{thought_id}` в блокчейне {blockchain}. Принять?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Да", callback_data=f"accept:{thought_id}:{message.from_user.id}"),
                    InlineKeyboardButton(text="❌ Нет", callback_data=f"decline:{message.from_user.id}:{thought_id}"),
                ]
            ]
        )
    )

    await message.answer("Запрос отправлен. Ожидаем ответ.", reply_markup=start_kb)
    await state.clear()

@user_private_router.callback_query(F.data.startswith("accept"))
async def handle_accept_thought(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Обработчик кнопки принятия мыслеформы.
    Пример callback_data: "accept:<thought_id>:<sender_id>"
    """

    try:
        _, thought_id, sender_id = callback.data.split(":")
        sender_id = int(sender_id)
    except (ValueError, AttributeError):
        await callback.message.edit_text("❌ Некорректные данные при передаче мыслеформы.")
        return

    receiver_username = callback.from_user.username  or f"id{callback.from_user.id}"
    
    # Get the sender's name from the database
    stmt = select(User).where(User.id == sender_id)
    result = await session.execute(stmt)
    sender = result.scalar_one_or_none()
    sender_link = (f"@{sender.username}" if sender.username else f'<a href="tg://user?id={sender.id}">пользователя</a>')
    #sender_username = sender.username if sender and sender.username else f"id{sender_id}"

    try:
        _, new_thought = await orm_transfer_thought(
            session=session,
            thought_id=thought_id,
            sender_id=sender_id,
            receiver_username=receiver_username,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        await callback.message.edit_text("❌ Ошибка при передаче мыслеформы.")
        return

    await callback.message.edit_text(f"✅ Отлично! Вашей мыслеформе присвоен новый ID: <code>{new_thought.id}</code>. Вы получили ее от {sender_link}. Cписок мыслеформ обновлен.",
                                     parse_mode="HTML")
    await bot.send_message(sender_id, f"✅ Получатель @{receiver_username} принял вашу мыслеформу!", parse_mode="HTML")

@user_private_router.callback_query(F.data.startswith("decline"))
async def decline_thought_transfer(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    _, sender_id, _ = callback.data.split(":")
    sender_id = int(sender_id)
    
    receiver_username = callback.from_user.username or f"id{callback.from_user.id}"
    
    # Get the sender's name from the database
    stmt = select(User).where(User.id == sender_id)
    result = await session.execute(stmt)
    sender = result.scalar_one_or_none()
    sender_link = (f"@{sender.username}" if sender.username else f'<a href="tg://user?id={sender.id}">пользователя</a>')


    await callback.message.edit_text(f"❌ Вы отклонили мыслеформу от {sender_link}.", parse_mode='HTML')
    await bot.send_message(sender_id, f"❌ Получатель @{receiver_username} отклонил вашу мыслеформу.", parse_mode='HTML') 
    
# We're processing the reply button "✍️ Удалить мыслеформу"
@user_private_router.message(F.text == "🗑️ Удалить мыслеформу")
async def delete_for_thought(message: Message, state: FSMContext):
    await message.answer("Введите ID мыслеформы, которую вы хотите удалить:")
    await state.set_state(DeleteStates.input_thought_id)           
    
@user_private_router.message(DeleteStates.input_thought_id)
async def delete_thought(message: Message, state: FSMContext, session: AsyncSession):
    # Check if the message is a command or the text of another reply button
    if message.text in ["📧 Поделиться мыслеформой", "✍️ Добавить мыслеформу", "🗑️ Удалить мыслеформу"]:
        await message.answer("Вы начали другое действие. Удаление мыслеформы отменено.")
        await state.clear()  
        return
    
    text = message.text.strip() # type: ignore
    
    if not text:
        await message.answer("Пожалуйста, введите действительный ID мыслеформы.")
        return

    if len(text) > 11:
        await message.answer("Слишком длинный ID. Пожалуйста, попробуйте заново.")
        return

    try:
        success = await orm_delete_thought(session, text, message.from_user.id)
        if success:
            await message.answer("✅ Ваша мыслеформа успешно удалена!")
        else:
            await message.answer("❌ Мыслеформа не найдена или вы не являетесь её владельцем.")
    except Exception as e:
        await message.answer("❌ Произошла ошибка при удалении мыслеформы. Пожалуйста, попробуйте еще раз.")
        print(f"[Ошибка] Не удалось удалить мыслеформу: {e}")    

    await state.clear()        
    
##################### OTHER COMMANDS #####################################    
    
@user_private_router.message(F.text == '/info')
async def get_info(message: Message):
    await message.answer('🚀 <b>Fintogram</b> - это первая децентрализованная биржа мыслеформ, кошелек, '
                          'позволяющий их хранить/передавать, и целая межгалактическая экосистема.\n\n' 
                          '🧠 <b>Мыслеформа</b> — это цифровой контейнер твоей идеи, снабжённый уникальным ID. Что делать со своими мыслеформами, '
                          'решать только тебе. Но помни, что в настоящий момент знания - самая ценная валюта в Галактике!\n\n'
                          '🔗 Функция <i>"Поделиться мыслеформой"</i> позволяет клонировать твою идею для определенного пользователя' 
                          ' (для него мыслеформа получит свой уникальный ID), однако ее авторство в межгалактической базе данных остается за тобой. Приятного "share-инга"!', parse_mode='HTML')    

@user_private_router.message(Command("developer"))
async def get_developer(message: Message):
    await message.answer('Сообщить что-то/поболтать с разработчиком: здесь укажите свой username')
      
@user_private_router.message()
async def fallback_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await message.answer("⛔️ Вы начали другое действие. Завершите его или нажмите /start для сброса.")
    else:
        await message.answer("🙋 Выберите действие через меню.", reply_markup=start_kb)

@user_private_router.message(Command("cancel")) # command /cancel
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Действие отменено.", reply_markup=start_kb)
   
           
