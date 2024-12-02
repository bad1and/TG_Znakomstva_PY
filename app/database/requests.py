from sqlalchemy import select

from app.database.models import UserInfo, Unic_ID
from app.database.models import async_session


async def set_user(tg_id, username, first_name, last_name, number):
    async with async_session() as session:
        user = await session.scalar(select(UserInfo).where(UserInfo.tg_id == tg_id))

        if not user:
            session.add(UserInfo(
                tg_id=tg_id,
                tg_username=username,
                first_name=first_name,
                last_name=last_name,
                number=number,
            ))
            await session.commit()


async def unic_data_user(tg_id, in_bot_name, years, voprosi, unic_your_id, unic_wanted_id):
    async with async_session() as session:
        session.add(Unic_ID(
            tg_id=tg_id,
            in_bot_name=in_bot_name,
            years=years,
            voprosi=voprosi,
            unic_your_id=unic_your_id,
            unic_wanted_id=unic_wanted_id
        ))
        await session.commit()

#
# async def get__categories():
#     async with async_session() as session:
#         return await session.scalars(select(Category))
#
#
# async def get_category_item(category_id):
#     async with async_session() as session:
#         return await session.scalars(select(Item).where(Item.category == category_id))
#
#
# async def get_item(item_id):
#     async with async_session() as session:
#         return await session.scalar(select(Item).where(Item.id == item_id))
