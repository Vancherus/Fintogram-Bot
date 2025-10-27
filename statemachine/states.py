from aiogram.fsm.state import StatesGroup, State

class ThoughtStates(StatesGroup):
    writing = State()  # the user enters a new thought form
    
class TransferStates(StatesGroup): 
    input_username_and_thought_id = State()  # step 1: enter @username и ID thoughtform
    choosing_blockchain = State()            # step 2: choose blockchain
    waiting_response = State()               # step 3: waiting for the recipient's response
    
class DeleteStates(StatesGroup):
    input_thought_id = State()
