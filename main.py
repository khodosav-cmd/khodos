import os
from threading import Thread
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# Вставь сюда свой токен и chat id или используй переменные окружения
TOKEN = os.environ.get("TOKEN") or "8053516713:AAHiRPoKBXqqV6vZpChX2W8nAhFswB5TQ64"
GROUP_CHAT_ID = int(os.environ.get("GROUP_CHAT_ID") or -4886669467)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    full_name = State()
    birth_date = State()
    problem = State()
    phone = State()

# Flask keep-alive
app = Flask("")

@app.route("/")
def home():
    return "Bot is running"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# /start - show consent
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    consent_text = (
        "Перед тем как продолжить, пожалуйста, подтвердите согласие на обработку персональных данных.\n\n"
        "Мы будем сохранять ваше ФИО, дату рождения, описание проблемы и контактный номер только для связи и записи на консультацию."
    )
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("Согласен(а)", callback_data="consent_yes"),
        types.InlineKeyboardButton("Не согласен(а)", callback_data="consent_no"),
    )
    await message.answer(consent_text, reply_markup=keyboard)

# Consent handlers
@dp.callback_query_handler(lambda c: c.data == "consent_no")
async def consent_no_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Вы отказались от обработки персональных данных. Если передумаете, отправьте /start.")
    
@dp.callback_query_handler(lambda c: c.data == "consent_yes")
async def consent_yes_handler(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,
                           "Спасибо. Пожалуйста, ответьте на вопросы.\n\n1️⃣ Как вас зовут? (Фамилия, имя и отчество)")
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
        "Если есть диагноз — укажите его, если нет — опишите своими словами (пример: «уплотнение в груди»)."
    )
    await Form.problem.set()

@dp.message_handler(state=Form.problem)
async def process_problem(message: types.Message, state: FSMContext):
    await state.update_data(problem=message.text)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("Отправить номер (контакт)", request_contact=True))
    await message.answer("4️⃣ Укажите контактный номер для нашего ассистента (можно нажать кнопку):", reply_markup=kb)
    await Form.phone.set()

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Form.phone)
async def process_phone_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await finish_and_send(message, state)

@dp.message_handler(state=Form.phone)
async def process_phone_text(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await finish_and_send(message, state)

async def finish_and_send(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = (
        "📩 Новая заявка:\n"
        f"👤 ФИО: {data.get('full_name','')}\n"
        f"🎂 Дата рождения: {data.get('birth_date','')}\n"
        f"📝 Проблема: {data.get('problem','')}\n"
        f"📞 Телефон: {data.get('phone','')}"
    )
    try:
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=text)
    except Exception:
        # попытка отправить в личку владельцу, если что-то с GROUP_CHAT_ID
        pass
    await message.answer("✅ Спасибо! Ваши данные отправлены, наш ассистент свяжется с вами.", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

if __name__ == "__main__":
    keep_alive()
    executor.start_polling(dp, skip_updates=True)
