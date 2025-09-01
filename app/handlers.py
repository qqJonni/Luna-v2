from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.generate import ai_generate, PERSONALITIES
from app.personality_manager import select_personality
import asyncio

router = Router()


class Gen(StatesGroup):
    wait = State()
    questionnaire = State()
    personality_selection = State()


# Временное хранилище данных пользователей
user_data = {}


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # Приветствие без излишней фамильярности
    welcome_text = """Привет! 👋 Я твой собеседник в этом чате.

Чтобы наше общение было комфортным, давай немного познакомимся. 
Это займет всего минуту!"""

    # Клавиатура для начала анкеты
    start_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Давай начнем!")]],
        resize_keyboard=True
    )

    await message.answer(welcome_text, reply_markup=start_keyboard)
    await state.set_state(Gen.questionnaire)


@router.message(Gen.questionnaire, F.text == "Давай начнем!")
async def start_questionnaire(message: Message, state: FSMContext):
    questions = [
        "Как мне тебя называть?",
        "Какой возраст собеседницы тебе комфортен? (молодая/сверстница/старше)",
        "Какой характер предпочитаешь? (сдержанная/дружелюбная/нейтральная)"
    ]

    await state.update_data(current_question=0, answers=[], questions=questions)
    await message.answer(questions[0], reply_markup=None)


@router.message(Gen.questionnaire)
async def handle_questionnaire(message: Message, state: FSMContext):
    data = await state.get_data()
    current_question = data['current_question']
    answers = data['answers']
    questions = data['questions']

    answers.append(message.text)
    current_question += 1

    if current_question < len(questions):
        await state.update_data(current_question=current_question, answers=answers)
        await message.answer(questions[current_question])
    else:
        # Все вопросы answered
        name, age_pref, temperament = answers

        # Сохраняем данные пользователя
        user_data[message.from_user.id] = {
            'name': name,
            'age_preference': age_pref,
            'temperament': temperament,
            'personality': select_personality(age_pref, temperament)
        }

        personality = user_data[message.from_user.id]['personality']

        await message.answer(
            f"Отлично! Буду общаться с тобой как {personality['name']} - {personality['traits']} 🌸\n\n"
            f"Теперь можешь писать мне что угодно, {name}!"
        )
        await state.clear()


@router.message(Gen.wait)
async def stop_flood(message: Message):
    await message.answer('Дай мне секунду подумать... 💭')


@router.message()
async def generating(message: Message, state: FSMContext, bot):
    user_id = message.from_user.id

    # Если пользователь еще не заполнил анкету
    if user_id not in user_data:
        await cmd_start(message, state)
        return

    await state.set_state(Gen.wait)

    # ПРАВИЛЬНЫЙ вызов действия "печатает"
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await asyncio.sleep(1)

    try:
        personality = user_data[user_id]['personality']
        response = await ai_generate(message.text, personality)
        await message.answer(response)
    except Exception as e:
        await message.answer("Давай попробуем еще раз? Что-то пошло не совсем так...")
        print(f"Error: {e}")

    await state.clear()


# Команда для смены персоналии
@router.message(Command("change"))
async def change_personality(message: Message, state: FSMContext):
    await message.answer("Давай выберем другую персоналию!")
    await start_questionnaire(message, state)