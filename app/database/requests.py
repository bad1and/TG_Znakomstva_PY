from sqlalchemy import select, update

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


async def unic_data_user(tg_id, in_bot_name, years, unic_your_id, unic_wanted_id):
    async with async_session() as session:


        user = await session.scalar(select(Unic_ID).where(Unic_ID.tg_id == tg_id))

        if not user:
            # Если юзер не найден — создаем нового
            session.add(Unic_ID(
                tg_id=tg_id,
                in_bot_name=in_bot_name or "",  # Заглушка, если нет имени
                years=years or 0,  # Заглушка, если нет возраста
                unic_your_id=unic_your_id or 0,
                unic_wanted_id=unic_wanted_id or 0
            ))
        else:
            # Если юзер есть — обновляем только переданные значения
            update_values = {}

            if in_bot_name is not None:
                update_values["in_bot_name"] = in_bot_name
            if years is not None:
                update_values["years"] = years
            if unic_your_id is not None:
                update_values["unic_your_id"] = unic_your_id
            if unic_wanted_id is not None:
                update_values["unic_wanted_id"] = unic_wanted_id

            if update_values:
                await session.execute(
                    update(Unic_ID)
                    .where(Unic_ID.tg_id == tg_id)
                    .values(update_values)
                )

        await session.commit()
