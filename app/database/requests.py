from sqlalchemy import select, update

from app.database.models import UserInfo
from app.database.models import async_session


async def set_user(tg_id, username, first_name, last_name, number, sex):
    async with async_session() as session:
        user = await session.scalar(select(UserInfo).where(UserInfo.tg_id == tg_id))

        if not user:
            session.add(UserInfo(
                tg_id=tg_id,
                tg_username=username,
                sex=sex,
                first_name=first_name,
                last_name=last_name,
                number=number,
                in_bot_name=None,
                years=None,
                unic_your_id=None,
                unic_wanted_id=None,
                status=1
            ))
            await session.commit()


async def unic_data_user(tg_id, in_bot_name, years, sex, unic_your_id, unic_wanted_id, username, first_name, last_name,
                         number, status):
    async with async_session() as session:
        user = await session.scalar(select(UserInfo).where(UserInfo.tg_id == tg_id))

        if not user:
            # Если юзер не найден — создаем нового
            session.add(UserInfo(
                tg_id=tg_id,
                tg_username=username or "",
                sex=sex or "",
                first_name=first_name or "",
                last_name=last_name or "",
                number=number or 0,
                in_bot_name=in_bot_name or "",
                years=years or 0,
                unic_your_id=unic_your_id or "",
                unic_wanted_id=unic_wanted_id or "",
                status=1
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
            if username is not None:
                update_values["tg_username"] = username
            if first_name is not None:
                update_values["first_name"] = first_name
            if last_name is not None:
                update_values["last_name"] = last_name
            if number is not None:
                update_values["number"] = number
            if sex is not None:
                update_values["sex"] = sex
            if status is not None:
                update_values["status"] = status

            if update_values:
                await session.execute(
                    update(UserInfo)
                    .where(UserInfo.tg_id == tg_id)
                    .values(update_values)
                )

        await session.commit()
