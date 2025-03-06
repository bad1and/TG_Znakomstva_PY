from io import BytesIO
from aiogram.types import Message, BufferedInputFile
from sqlalchemy.future import select
from app.database.models import async_session, UserInfo
from app.keyboards import partner_navigation_keyboard


def is_similar(id1: str, id2: str) -> bool:
    """Определяет, насколько два unic_id похожи по заданному критерию."""
    return sum(1 for a, b in zip(id1, id2) if a == b) >= len(id1) - 1  # Допускаем 1 несовпадение


async def find_matching_users(user):
    async with async_session() as session:

        all_users = await session.scalars(select(UserInfo).where(
            (UserInfo.tg_id != user.tg_id) & (UserInfo.sex != user.sex) & (UserInfo.status == user.status)))
        perfect_matches = []
        similar_matches = []

        for candidate in all_users:
            if candidate.unic_your_id == user.unic_wanted_id:
                perfect_matches.append(candidate)
            elif is_similar(candidate.unic_your_id, user.unic_wanted_id):
                similar_matches.append(candidate)

        return perfect_matches + similar_matches


async def show_partner_profile(message: Message, users, index: int):
    partner = users[index]
    async with async_session() as session:
        user = await session.scalar(select(UserInfo.unic_wanted_id))
    user_profile_photo = await message.bot.get_user_profile_photos(partner.tg_id, limit=1)
    file_bytes = None
    if user_profile_photo.total_count > 0:
        photo = user_profile_photo.photos[0][-1]
        file = await message.bot.download(photo.file_id)
        file_bytes = BytesIO(file.read())
        file_bytes.seek(0)

    match_type = "100% совпадение" if partner.unic_your_id == user else "Похожий партнер(не 100% удовлетворяет вашим критериям)"

    profile_text = f"{match_type}\n\nИмя: {partner.in_bot_name} \nВозраст: {partner.years} \nКонтакт: @{partner.tg_username}"
    keyboard = partner_navigation_keyboard(index, len(users))

    if file_bytes:
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=BufferedInputFile(file_bytes.read(), filename="avatar.jpg"),
            caption=profile_text,
            reply_markup=keyboard
        )
    else:
        await message.answer(profile_text, reply_markup=keyboard)
