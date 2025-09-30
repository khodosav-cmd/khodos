from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# === ВАЖНО: токен и chat_id уже вставлены ===
TOKEN = "8053516713:AAHiRPoKBXqqV6vZpChX2W8nAhFswB5TQ64"
GROUP_CHAT_ID = -4886669467  # ID вашей группы/канала

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Определяем шаги диалога
class Form(StatesGroup):
    full_name = State()
    birth_date = State()
    problem = State()
    phone = State()

# Стартовое сообщение
@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer(
        "Рад Вашему обращению! Ответьте, пожалуйста, на эти вопросы, "
        "чтобы мой ассистент мог связаться с Вами и подобрать удобное время для консультации.\n\n"
        "1️⃣ Как вас зовут? (Фамилия, имя и отчество)"
    )
    await Form.full_name.set()

# ФИО
@dp.message_handler(state=Form.full_name)
async def process_fullname(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("2️⃣ Ваша дата рождения (число, месяц, год):")
    await Form.birth_date.set()

# Дата рождения
@dp.message_handler(state=Form.birth_date)
async def process_birth(message: types.Message, state: FSMContext):
    await state.update_data(birth_date=message.text)
    await message.answer(
        "3️⃣ Опишите вашу проблему кратко.\n"
        "(Если уже есть диагноз — укажите его, если нет — опишите своими словами. "
        "Например: «уплотнение в груди» или «странная родинка»)"
    )
    await Form.problem.set()

# Проблема
@dp.message_handler(state=Form.problem)
async def process_problem(message: types.Message, state: FSMContext):
    await state.update_data(problem=message.text)
    await message.answer("4️⃣ Укажите свой контактный номер для нашего ассистента:")
    await Form.phone.set()

# Телефон + итог
@dp.message_handler(state=Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()

    # Формируем текст заявки
    text = (
        "📩 Новая заявка:\n"
        f"👤 ФИО: {data['full_name']}\n"
        f"🎂 Дата рождения: {data['birth_date']}\n"
        f"📝 Проблема: {data['problem']}\n"
        f"📞 Телефон: {data['phone']}"
    )

    # Отправляем в группу
    await bot.send_message(chat_id=GROUP_CHAT_ID, text=text)

    # Ответ пользователю
    await message.answer("✅ Спасибо! Ваши данные отправлены, наш ассистент скоро свяжется с вами.")

    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
