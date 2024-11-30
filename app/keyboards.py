from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
# from app.database.requests import get__categories, get_category_item

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
        [KeyboardButton(text='Искать партнера 🥵'), KeyboardButton(text='Моя анкета 🤥')]
    ],
    resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню... 🤭'
)


admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Искать партнера 🥵'), KeyboardButton(text='Моя анкета 🤥'), KeyboardButton(text='Админ-панель')]
    ],
    resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню... 🤭'
)

admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Что то будет'), KeyboardButton(text='Назад 👈')]
    ],
    resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню... 🤭'
)

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
