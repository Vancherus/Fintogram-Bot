from aiogram.fsm.state import StatesGroup, State

class ThoughtStates(StatesGroup):
    writing = State()  # пользователь вводит новую мыслеформу
    
class TransferStates(StatesGroup): 
    input_username_and_thought_id = State()  # Шаг 1: ввод @юзернейма и ID мыслеформы
    choosing_blockchain = State()            # Шаг 2: выбор блокчейна
    waiting_response = State()               # Шаг 3: ожидание ответа получателя
    
class DeleteStates(StatesGroup):
    input_thought_id = State()