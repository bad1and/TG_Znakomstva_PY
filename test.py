import os
from io import BytesIO

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile, CallbackQuery
from sqlalchemy import select

import app.database.requests as rq
import app.keyboards as kb
from app.database.models import async_session, UserInfo, RegistrationState, Unic_ID
from app.questions import questions, questions_wanted

router = Router()


# Команда /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    async with async_session() as session:
        user = await session.scalar(select(UserInfo).where(UserInfo.tg_id == message.from_user.id))

        if not user:
            await message.answer(
                "Вы у нас первый раз! Нажмите 'Регистрация 🚀' ниже, чтобы отправить ваш контакт.",
                reply_markup=kb.reg_keyboard
            )
        else:
            await message.answer("Добро пожаловать!", reply_markup=kb.menu)


# Регистрация пользователя
@router.message(F.contact)
async def handle_contact(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username or "None"
    first_name = message.from_user.first_name or "None"
    last_name = message.from_user.last_name or "None"
    number = message.contact.phone_number

    await rq.set_user(
        tg_id=tg_id, username=username, first_name=first_name,
        last_name=last_name, number=number
    )
    await message.answer("Спасибо за регистрацию! Теперь пройди опрос!", reply_markup=kb.opros_keyboard)


# Начало опроса или его изменение
@router.message(F.text.in_({'Пройти опрос 🤙', 'Изменить опрос'}))
async def start_survey(message: Message, state: FSMContext):
    await state.update_data(your_answers=[], wanted_answers=[])
    await ask_question(message, state, 1)


async def ask_question(message: Message, state: FSMContext, question_id: int):
    if question_id in questions:
        await message.answer(questions[question_id]["question"], reply_markup=kb.get_question_keyboard(question_id))
    else:
        await ask_wanted_question(message, state, 1, message.from_user.id)



async def ask_wanted_question(message: Message, state: FSMContext, question_id: int, user_id: int):
    if question_id in questions_wanted:
        await message.answer(questions_wanted[question_id]["question"], reply_markup=kb.get_wanted_question_keyboard(question_id))
    else:
        data = await state.get_data()
        unic_your_id = ";".join(data.get("your_answers", []))
        unic_wanted_id = ";".join(data.get("wanted_answers", []))

        await rq.unic_data_user(
            tg_id=user_id,  # Передаем корректный ID пользователя
            in_bot_name=None,
            years=None,
            unic_your_id=unic_your_id,
            unic_wanted_id=unic_wanted_id
        )

        await message.answer("Опрос завершен!", reply_markup=kb.back)
        await state.clear()



@router.callback_query(F.data.startswith("answer_you_"))
async def handle_you_answer(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id  # Исправлено: используем callback.from_user.id
    data = callback.data.split("_")
    question_id, answer_index = int(data[2]), data[3]

    user_data = await state.get_data()
    your_answers = user_data.get("your_answers", [])
    your_answers.append(answer_index)
    await state.update_data(your_answers=your_answers)

    await callback.message.delete()
    await ask_question(callback.message, state, question_id + 1)
    await callback.answer()


@router.callback_query(F.data.startswith("answer_wanted_"))
async def handle_wanted_answer(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id  # Исправлено: используем callback.from_user.id
    data = callback.data.split("_")
    question_id, answer_index = int(data[2]), data[3]

    user_data = await state.get_data()
    wanted_answers = user_data.get("wanted_answers", [])
    wanted_answers.append(answer_index)
    await state.update_data(wanted_answers=wanted_answers)

    await callback.message.delete()
    await ask_wanted_question(callback.message, state, question_id + 1, callback.from_user.id)

    await callback.answer()


@router.message(F.text == 'Моя анкета 🤥')
async def show_profile(message: Message):
    async with async_session() as session:
        user = await session.scalar(select(Unic_ID).where(Unic_ID.tg_id == message.from_user.id))
        if not user:
            await message.answer("Анкета не найдена. Сначала зарегистрируйтесь через 'Регистрация 🚀'.", reply_markup=kb.reg_keyboard)
            return

        profile_text = f"**Твоя анкета:**\n\n" \
                       f"Имя: {user.in_bot_name or 'Не указано'}\n" \
                       f"Возраст: {user.years or 'Не указан'}"
        await message.answer(profile_text, reply_markup=kb.back)
