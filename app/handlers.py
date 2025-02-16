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
from app.questions import questions,questions_wanted
router = Router()



# Команда /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    async with async_session() as session:
        if message.from_user.id == int(os.getenv('ADMIN_ID')):
            await message.answer("Привет админ!", reply_markup=kb.admin_menu)
        else:
            user = await session.scalar(select(UserInfo).where(UserInfo.tg_id == message.from_user.id))

            if not user:
                # Если пользователь не зарегистрирован, предлагаем регистрацию
                await message.answer(
                    "Вы у нас первый раз! Нажмите 'Регистрация 🚀' ниже, чтобы отправить ваш контакт.",
                    reply_markup=kb.reg_keyboard
                )
            else:
                # Если пользователь уже зарегистрирован
                await message.answer("Добро пожаловать!", reply_markup=kb.menu)


# Обработчик для получения контакта
@router.message(F.contact)
async def handle_contact(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username or "None"
    first_name = message.from_user.first_name or "None"
    last_name = message.from_user.last_name or "None"
    number = message.contact.phone_number

    # Сохраняем пользователя в базе данных
    await rq.set_user(
        tg_id=tg_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        number=number,
    )
    await message.answer("Спасибо за регистрацию! Добро пожаловать!", reply_markup=None)
    await message.answer("Кажется, вы не проходили опрос! Испугался? Не бойся! Давай пройдем его. (если вы не с ФКТИ)",
                         reply_markup=kb.opros_keyboard)

# @router.message(F.text == 'Изменить анкету')
# async def start_survey(message: Message, state: FSMContext):
#     await message.answer("Как тебя зовут?", reply_markup=None)
#     await state.set_state(RegistrationState.waiting_for_name)


# Начало опроса
@router.message(F.text == 'Пройти опрос 🤙')
async def start_survey(message: Message, state: FSMContext):
    await message.answer("Как тебя зовут?", reply_markup=None)
    await state.set_state(RegistrationState.waiting_for_name)


# Обработчик для ввода имени
@router.message(RegistrationState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer("Сколько тебе лет?", reply_markup=None)
    await state.set_state(RegistrationState.waiting_for_age)


@router.message(RegistrationState.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    try:
        # Проверка возраста
        if 16 <= int(message.text) <= 40:
            age = int(message.text)
        else:
            await message.answer("Пожалуйста, введите нормальный возраст.", reply_markup=None)
            return
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение возраста.", reply_markup=None)
        return

    # Получаем имя из состояния
    user_data = await state.get_data()
    name = user_data.get("name")

    await rq.unic_data_user(
        tg_id=message.from_user.id,  # Передаем корректный ID пользователя
        in_bot_name=name,
        years=age,
        unic_your_id=0,
        unic_wanted_id=0
    )

    await message.answer("Теперь давай заполним анкету о тебе и твоих предпочтениях в партнере!", reply_markup=kb.start_opros)
    await state.clear()



@router.message(F.text == 'Искать партнера 🥵')
async def start_survey(message: Message, state: FSMContext):
    await message.answer(f"Алгоритм поиска временно отсутствует", reply_markup=kb.back)



@router.message(F.text.in_(['Пройти опросик))', 'Изменить анкету']))
async def start_survey(message: Message, state: FSMContext):
    """Запускает опрос"""
    await state.update_data(your_answers=[])
    await state.update_data(wanted_answers=[])
    await ask_question(message, state, 1)


async def ask_question(message: Message, state: FSMContext, question_id: int):
    """Задает следующий вопрос про пользователя"""
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

        if user_id == int(os.getenv('ADMIN_ID')):
            await message.answer(f"Готово админ", reply_markup=kb.admin_menu)
        elif F.text == 'Пройти опросик))':
            await message.answer(f"Видишь, не стоило бояться! Ты прошел регистрацию!", reply_markup=kb.menu)
        elif F.text == 'Изменить анкету':
            await message.answer(f"Анкета успешно изменена", reply_markup=kb.menu)
        await state.clear()




@router.callback_query(F.data.startswith("answer_you_"))
async def handle_you_answer(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает ответы пользователя"""
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





@router.message(F.text == 'Назад 👈')
async def menu(message: Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer("Панель", reply_markup=kb.admin_menu)
    else:
        await message.answer("Выберите действие", reply_markup=kb.menu)


@router.message(F.text == 'Моя анкета 🤥')
async def find_partner(message: Message):
    async with async_session() as session:
        user = await session.scalar(select(Unic_ID).where(Unic_ID.tg_id == message.from_user.id))
        if (not user) and (message.from_user.id != int(os.getenv('ADMIN_ID'))):
            await message.answer(
                "Анкета не найдена. Сначала зарегистрируйтесь через 'Регистрация 🚀'.",
                reply_markup=kb.reg_keyboard
            )
            return

        # Получаем аватарку пользователя
        user_profile_photo = await message.bot.get_user_profile_photos(message.from_user.id, limit=1)

        if user_profile_photo.total_count > 0:
            # Берем фото самого высокого качества
            photo = user_profile_photo.photos[0][-1]  # последнее фото из списка

            # Скачиваем файл
            file = await message.bot.download(photo.file_id)

            # Читаем файл в BytesIO
            file_bytes = BytesIO(file.read())
            file_bytes.seek(0)

            # Отправляем аватарку
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=BufferedInputFile(file_bytes.read(), filename="avatar.jpg")
            )
        else:
            # Если аватарки нет, отправляем сообщение
            await message.answer("У вас нет аватарки! Загрузите её в Telegram, чтобы она отображалась здесь.")

        # Профиль

        profile_text = f"**Твоя анкета:**\n\n" \
                       f"Имя: {user.in_bot_name if user and user.in_bot_name else 'Не указано'}\n" \
                       f"Возраст: {user.years if user and user.years else 'Не указан'}"

        await message.answer(profile_text, reply_markup=kb.back)


@router.message(F.text == 'Админ-панель')
async def admin(message: Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer("Ты авторизовался в админку", reply_markup=kb.admin)
    else:
        await message.answer("Не понимаю тебя ", reply_markup=kb.menu)
