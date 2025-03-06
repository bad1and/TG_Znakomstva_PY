from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from app.questions import questions, questions_wanted


def status_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Включить анкету ✅", callback_data="enable_profile"),
                InlineKeyboardButton(text="Отключить анкету ❌", callback_data="disable_profile")
            ]
        ]
    )
    return keyboard


def partner_navigation_keyboard(index: int, total: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⬅', callback_data=f'prev_{index}'),
         InlineKeyboardButton(text=f'{index + 1}/{total}', callback_data='none'),
         InlineKeyboardButton(text='➡', callback_data=f'next_{index}')]
    ])


def get_question_keyboard(question_id: int) -> InlineKeyboardMarkup:
    """Генерирует inline-клавиатуру для вопросов про пользователя"""
    buttons = [
        [InlineKeyboardButton(text=option, callback_data=f"answer_you_{question_id}_{i}")]
        for i, option in enumerate(questions[question_id]["options"])
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_wanted_question_keyboard(question_id: int) -> InlineKeyboardMarkup:
    """Генерирует inline-клавиатуру для вопросов про партнера"""
    buttons = [
        [InlineKeyboardButton(text=option, callback_data=f"answer_wanted_{question_id}_{i}")]
        for i, option in enumerate(questions_wanted[question_id]["options"])
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


myanket_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Назад 👈'), KeyboardButton(text='Изменить статус 🕐')]
    ],
    resize_keyboard=True,
)

sex = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Мужской 🙋‍♂️'), KeyboardButton(text='Женский 🙋‍♀️')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пол...👁️'
)

start_opros = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Пройти опросик 👻')]
    ],
    resize_keyboard=True
)

reg_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Регистрация 🚀', request_contact=True)]
    ],
    resize_keyboard=True
)
opros_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Пройти опрос 🤙')]
    ],
    resize_keyboard=True
)

back = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Назад 👈')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...📜'
)

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Искать партнера 😏'), KeyboardButton(text='Моя анкета 🫵')
            , KeyboardButton(text='Перепройти опрос 🔄')
         ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...📜'
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Искать партнера 😏'), KeyboardButton(text='Моя анкета 🫵'),
         KeyboardButton(text='Перепройти опрос 🔄'),
         KeyboardButton(text='Админ-панель 👑')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...📜'
)

admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Регистрация 🚀', request_contact=True)],
        [KeyboardButton(text='Назад 👈'), KeyboardButton(text='К-во userов')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...📜'
)
