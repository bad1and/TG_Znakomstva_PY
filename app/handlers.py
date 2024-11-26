import sqlalchemy.exc
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

import app.database.requests as rq
import app.keyboards as kb

router = Router()


# tg_id: Mapped[int] = mapped_column(BigInteger)
# tg_username: Mapped[str] = mapped_column(String(120))
# first_name: Mapped[str] = mapped_column(String(120))
# last_name: Mapped[str] = mapped_column(String(120))
# number: Mapped[int] = mapped_column()
# in_bot_name: Mapped[str] = mapped_column(String(120))
# years: Mapped[int] = mapped_column()

# TODO: Запросить после старта номер телефона и имя и возраст но перед этим запрашивать наличие в бд
@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(
        tg_id=message.from_user.id,
        username=message.from_user.username or "None",
        first_name=message.from_user.first_name or "None",
        last_name=message.from_user.last_name or "None",
        number=777,
        in_bot_name=message.from_user.username or "None",
        years=777,
    )
    await message.answer('Добро пожаловать в магазин!', reply_markup=kb.main)

# @router.message(F.text == 'Каталог')
# async def catalog(message: Message):
#     await message.answer('Выберите категорию товара', reply_markup=await kb.categories())
#
#
# @router.callback_query(F.data.startswith('category_'))
# async def category(callback: CallbackQuery):
#     await callback.answer('Вы выбрали категорию')
#     await callback.message.answer('Выберите товар по категории',
#                                   reply_markup=await kb.items(callback.data.split('_')[1]))
#
#
# @router.callback_query(F.data.startswith('item_'))
# async def category(callback: CallbackQuery):
#     item_data = await rq.get_item(callback.data.split('_')[1])
#     await callback.answer('Вы выбрали категорию')
#     await callback.message.answer(
#         f'Название {item_data.name}\nОписание: {item_data.description}\nЦена: {item_data.price}',
#         reply_markup=await kb.items(callback.data.split('_')[1]))
