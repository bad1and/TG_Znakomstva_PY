import os

from dotenv import load_dotenv
from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Создаем асинхронный движок базы данных
load_dotenv()
engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'))

# Создаем фабрику асинхронных сессий
async_session = async_sessionmaker(engine)


# Базовый класс для моделей
class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserInfo(Base):
    __tablename__ = 'UsersInfo'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    tg_username: Mapped[str] = mapped_column(String(120), nullable=False)
    first_name: Mapped[str] = mapped_column(String(120), nullable=True)
    last_name: Mapped[str] = mapped_column(String(120), nullable=True)
    number: Mapped[int] = mapped_column(nullable=False)
    in_bot_name: Mapped[str] = mapped_column(String(120), nullable=False)
    years: Mapped[int] = mapped_column(nullable=False)

    # ORM связь
    unic_ids: Mapped[list["Unic_ID"]] = relationship(back_populates="user_info", cascade="all, delete-orphan")


class Unic_ID(Base):
    __tablename__ = 'UnicID"s'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey('UsersInfo.tg_id'), nullable=False)
    voprosi: Mapped[str] = mapped_column(String(120), nullable=False)
    unic_your_id: Mapped[str] = mapped_column(String(120), nullable=False)
    unic_wanted_id: Mapped[str] = mapped_column(String(120), nullable=False)

    # ORM связь
    user_info: Mapped[UserInfo] = relationship(back_populates="unic_ids")


# Асинхронная функция для создания таблиц
async def async_main():
    async with engine.begin() as conn:
        # Синхронно выполняем создание всех таблиц
        await conn.run_sync(Base.metadata.create_all)
