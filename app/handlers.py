import os

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputFile
from sqlalchemy import select
from aiogram.filters import Filter, CommandStart, Command
from app.database.models import async_session, UserInfo, RegistrationState, Unic_ID
import app.database.requests as rq
import app.keyboards as kb

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
    await message.answer("Кажется, вы не проходили опрос! Испугался? Не бойся! Давай пройдем его. (если вы не с ФКТИ)", reply_markup=kb.opros_keyboard)


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


# Обработчик для ввода возраста
@router.message(RegistrationState.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    try:
        if 16<=int(message.text)<=40:
            age = int(message.text)
        else:
            await message.answer("Пожалуйста, введите нормальный возраст.", reply_markup=None)
            return
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение возраста.", reply_markup=None)
        return

    user_name = await state.get_data()
    name = user_name.get("name")

    await rq.unic_data_user(
        tg_id=message.from_user.id,
        in_bot_name=name,
        years=age,
        voprosi='None',
        unic_your_id=0,
        unic_wanted_id=0
    )

    # Здесь можно сохранить имя и возраст в базу данных, если нужно
    await message.answer(f"Видишь не стоило бояться! Ты прошел регистрацию!", reply_markup=None)
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer(f"P.S Когда то тут будет опросник о тебе и желаемом партнере", reply_markup=kb.admin_menu)
    else:
        await message.answer(f"P.S Когда то тут будет опросник о тебе и желаемом партнере", reply_markup=kb.menu)

    await state.clear()


@router.message(F.text == 'Назад 👈')
async def menu(message: Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer("Панель", reply_markup=kb.admin_menu)
    else:
        await message.answer("Выберите действие", reply_markup=kb.menu)

@router.message(F.text == 'Искать партнера 🥵')
async def find_partner(message: Message):
    await message.answer("Когда то тут будет поиск...", reply_markup=kb.back)


@router.message(F.text == 'Моя анкета 🤥')
async def find_partner(message: Message):
    async with async_session() as session:
        # Получаем данные пользователя из базы
        user = await session.scalar(select(Unic_ID).where(Unic_ID.tg_id == message.from_user.id))
        if not user:
            await message.answer(
                "Анкета не найдена. Сначала зарегистрируйтесь через 'Регистрация 🚀'.",
                reply_markup=kb.reg_keyboard
            )
            return

#TODO: СДЕЛАЙ АВЫ ДЛЯ ПРОФИЛЯ
        profile_text = f"**Твоя анкета:**\n\n" \
                       f"Имя: {user.in_bot_name or 'Не указано'}\n" \
                       f"Возраст: {user.years or 'Не указан'}\n\n"\
                        "Аватарки в скором времени будут подгружаться в качестве авы(пните админа)"

        await message.answer(profile_text,reply_markup=kb.back)


@router.message(F.text == 'Админ-панель')
async def admin(message: Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer("Панель", reply_markup=kb.admin)
    else:
        await message.answer("Не понимаю тебя ", reply_markup=kb.menu)


