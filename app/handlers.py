import os
from io import BytesIO

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile, CallbackQuery
from sqlalchemy import select, func

import app.database.requests as rq
import app.keyboards as kb
from app.database.models import async_session, UserInfo, RegistrationState
from app.questions import questions, questions_wanted
from app.matching import find_matching_users, show_partner_profile

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
    await rq.unic_data_user(
        tg_id=tg_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        number=number,
        sex=None,
        in_bot_name=None,
        years=None,
        unic_your_id=None,
        unic_wanted_id=None,
        status=1
    )

    await message.answer(
        "Спасибо за регистрацию! Добро пожаловать! \nКажется, вы не проходили опрос! Испугался? Не бойся! Давай пройдем его.",
        reply_markup=kb.opros_keyboard)


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
    await message.answer("Выберите ваш пол", reply_markup=kb.sex)
    await state.set_state(RegistrationState.waiting_for_sex)


# Обработчик для ввода имени
@router.message(RegistrationState.waiting_for_sex)
async def process_sex(message: Message, state: FSMContext):
    sex = message.text
    try:
        if sex == "Мужской 🙋‍♂️":
            sex = "men"
        elif sex == "Женский 🙋‍♀️":
            sex = "woman"
        else:
            await message.answer("Нет такого варианта", reply_markup=None)
            return
    except ValueError:
        # await message.answer("Нет такого варианта", reply_markup=None)
        return
    await state.update_data(sex=sex)
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
    sex = user_data.get("sex")

    await rq.unic_data_user(
        tg_id=message.from_user.id,  # Передаем корректный ID пользователя
        in_bot_name=name,
        years=age,
        sex=sex,
        unic_your_id=0,
        unic_wanted_id=0,
        username=None,
        first_name=None,
        last_name=None,
        number=None,
        status=1
    )

    await message.answer("Теперь давай заполним анкету о тебе и твоих предпочтениях в партнере!",
                         reply_markup=kb.start_opros)
    await state.clear()


@router.message(F.text.in_(['Пройти опросик 👻', 'Перепройти опрос 🔄']))
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
        await message.answer(questions_wanted[question_id]["question"],
                             reply_markup=kb.get_wanted_question_keyboard(question_id))
    else:
        data = await state.get_data()
        unic_your_id = ";".join(data.get("your_answers", []))
        unic_wanted_id = ";".join(data.get("wanted_answers", []))

        # Получаем дополнительные данные из БД, чтобы передать в функцию обновления
        async with async_session() as session:
            user = await session.scalar(select(UserInfo).where(UserInfo.tg_id == user_id))

        await rq.unic_data_user(
            tg_id=user_id,
            in_bot_name=user.in_bot_name if user else None,
            sex=user.sex if user else None,
            years=user.years if user else None,
            unic_your_id=unic_your_id,
            unic_wanted_id=unic_wanted_id,
            username=user.tg_username if user else None,
            first_name=user.first_name if user else None,
            last_name=user.last_name if user else None,
            number=user.number if user else None,
            status=user.status if user else None
        )

        if user_id == int(os.getenv('ADMIN_ID')):
            await message.answer(f"Готово админ", reply_markup=kb.admin_menu)
        elif F.text == 'Пройти опросик 👻))':
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


@router.message(F.text == 'Искать партнера 😏')
async def find_partner(message: Message, state: FSMContext):
    async with async_session() as session:
        user = await session.scalar(select(UserInfo).where(UserInfo.tg_id == message.from_user.id))

        check_user_status = await session.scalar(select(UserInfo.status).where(UserInfo.tg_id == message.from_user.id))
        if check_user_status:
            matched_users = await find_matching_users(user)
            if not matched_users:
                await message.answer("Совпадений не найдено.")
                return

            await state.update_data(matched_users=matched_users)
            await show_partner_profile(message, matched_users, 0)
        else:
            await message.answer(
                'Ваша анкета отключена. Для поиска включите ее в меню "Моя анкета 🫵"',
                reply_markup=kb.admin_menu if message.from_user.id == int(os.getenv('ADMIN_ID')) else kb.menu
            )


@router.callback_query(F.data.startswith("prev_"))
async def prev_partner(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1]) - 1
    user_data = await state.get_data()
    users = user_data.get("matched_users", [])

    if index < 0:
        index = len(users) - 1

    await show_partner_profile(callback.message, users, index)
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data.startswith("next_"))
async def next_partner(callback: CallbackQuery, state: FSMContext):
    index = int(callback.data.split("_")[1]) + 1
    user_data = await state.get_data()
    users = user_data.get("matched_users", [])

    if index >= len(users):
        index = 0

    await show_partner_profile(callback.message, users, index)
    await callback.message.delete()
    await callback.answer()


@router.message(F.text == 'Назад 👈')
async def menu(message: Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer("Панель", reply_markup=kb.admin_menu)
    else:
        await message.answer("Выберите действие", reply_markup=kb.menu)


@router.message(F.text == 'Моя анкета 🫵')
async def my_anket(message: Message):
    async with async_session() as session:
        user = await session.scalar(select(UserInfo).where(UserInfo.tg_id == message.from_user.id))
        if (not user) and (message.from_user.id != int(os.getenv('ADMIN_ID'))):
            await message.answer(
                "Анкета не найдена. Сначала зарегистрируйтесь через 'Регистрация 🚀'.",
                reply_markup=kb.reg_keyboard
            )
            return

        # Получаем аватарку пользователя
        user_profile_photo = await message.bot.get_user_profile_photos(message.from_user.id, limit=1)

        if user.status == 1:
            status = 'Участвует в поиске)'
        else:
            status = 'Не участвует в поиске('

        profile_text = f"Имя: {user.in_bot_name if user and user.in_bot_name else 'Не указано'}\n" \
                       f"Пол: {user.sex if user and user.sex else 'Не указан'}\n" \
                       f"Возраст: {user.years if user and user.years else 'Не указан'}\n\n" \
                       f"Состояние анкеты: {status}"

        await message.answer('Твоя анкета:', reply_markup=kb.myanket_menu)
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
                caption=profile_text,
                photo=BufferedInputFile(file_bytes.read(), filename="avatar.jpg")
            )
        else:
            # Если аватарки нет, отправляем сообщение
            await message.answer(f"Кажется у вас нет аватарки, либо она скрыта(\n\n {profile_text}")


@router.message(F.text == 'Изменить статус 🕐')
async def change_status(message: Message):
    await message.answer(
        "Выберите статус анкеты:",
        reply_markup=kb.status_keyboard()
    )


@router.callback_query(F.data.in_({"enable_profile", "disable_profile"}))
async def update_status(call: CallbackQuery):
    new_status = 1 if call.data == "enable_profile" else 0

    async with async_session() as session:
        user = await session.execute(select(UserInfo).where(UserInfo.tg_id == call.from_user.id))
        user = user.scalars().first()
        if user:
            user.status = new_status
            await session.commit()

    await call.message.delete()
    await call.answer("Статус анкеты обновлен ✅")

    # После обновления статуса отправляем анкету


@router.message(F.text == 'Админ-панель 👑')
async def admin(message: Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer("Ты авторизовался в админку", reply_markup=kb.admin)
    else:
        await message.answer("Не понимаю тебя ", reply_markup=kb.menu)


@router.message(F.text == 'К-во userов')
async def users_count(message: Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        async with async_session() as session:
            result = await session.scalar(select(func.count()).select_from(UserInfo))
            await message.answer(f'Пользователей: {result}', reply_markup=kb.admin)
    else:
        await message.answer('Мая-твая не понимать', reply_markup=kb.menu)
