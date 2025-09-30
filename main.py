from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

TOKEN = "8053516713:AAHiRPoKBXqqV6vZpChX2W8nAhFswB5TQ64"
GROUP_CHAT_ID = -4886669467

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    full_name = State()
    birth_date = State()
    problem = State()
    phone = State()

@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer(
        "Рад Вашему обращению! Ответьте, пожалуйста, на эти вопросы, чтобы мой ассистент мог связаться с Вами и подобрать удобное время для консультации.\n\n"
        "1️⃣ Как вас зовут? (Фамилия, имя и отчество)"
    )
    await Form.full_name.set()

@dp.message_handler(state=Form.full_name)
async def process_fullname(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("2️⃣ Ваша дата рождения (число, месяц, год):")
    await Form.birth_date.set()

@dp.message_handler(state=Form.birth_date)
async def process_birth(message: types.Message, state: FSMContext):
    await state.update_data(birth_date=message.text)
    await message.answer(
        "3️⃣ Опишите вашу проблему кратко.\n"
        "(Если уже есть диагноз — укажите его, если
