from aiogram.fsm.state import StatesGroup, State


class AddUserByAdminFSM(StatesGroup):
    contact = State()


class DeleteUserFSM(StatesGroup):
    start = State()
    client = State()
    confirm = State()
