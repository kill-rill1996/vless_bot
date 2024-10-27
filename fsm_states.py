from aiogram.fsm.state import StatesGroup, State


class AddUserByAdminFSM(StatesGroup):
    contact = State()