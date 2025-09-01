from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.generate import ai_generate
import asyncio

router = Router()


class Gen(StatesGroup):
    wait = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = """Привет! 🌸 Я Луна - твоя виртуальная подруга. 

Я здесь, чтобы поболтать, поддержать тебя или просто составить компанию. 
Расскажи, как прошел твой день? 😊"""

    await message.answer(welcome_text)


@router.message(Gen.wait)
async def stop_flood(message: Message):
    # Более женственный ответ ожидания
    await message.answer('Подожди немного, милый, я обдумываю твой вопрос... 💭')


@router.message()
async def generating(message: Message, state: FSMContext):
    await state.set_state(Gen.wait)

    try:
        response = await ai_generate(message.text, message.from_user.first_name)
        await message.answer(response)
    except Exception as e:
        await message.answer("Ой, что-то пошло не так... 😅 Давай попробуем еще раз?")
        print(f"Error: {e}")

    await state.clear()