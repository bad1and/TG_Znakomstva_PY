from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from app.questions import questions,questions_wanted


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

back = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back")]]
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
    input_field_placeholder='Выберите пункт меню...'
)

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Искать партнера 🥵'), KeyboardButton(text='Моя анкета 🤥')
            # , KeyboardButton(text='Изменить анкету')
         ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню... 🤭'
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Искать партнера 🥵'), KeyboardButton(text='Моя анкета 🤥'),
         KeyboardButton(text='Изменить анкету'),
         KeyboardButton(text='Админ-панель')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню... 🤭'
)

admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Регистрация 🚀', request_contact=True)], [KeyboardButton(text='Назад 👈')]],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню... 🤭'
)


# async def send_question(question_id):
#     question_data = questions.get(question_id)
#     if not question_data:
#         return "Вопрос не найден.", None
#
#     keyboard = InlineKeyboardMarkup()
#     for idx, option in enumerate(question_data["options"], start=1):
#         keyboard.add(InlineKeyboardButton(text=option, callback_data=f"answer_{question_id}_{idx}"))
#
#     return question_data["question"], keyboard


# async def categories():
#     all_categories = await get__categories()
#     keyboard = InlineKeyboardBuilder()
#     for category in all_categories:
#         keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
#     keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
#     return keyboard.adjust(2).as_markup()
#
#
# async def items(category_id):
#     all_items = await get_category_item(category_id)
#     keyboard = InlineKeyboardBuilder()
#     for item in all_items:
#         keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f"item_{item.id}"))
#     keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
#     return keyboard.adjust(2).as_markup()
