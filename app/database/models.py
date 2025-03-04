import os

from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Загружаем переменные окружения
load_dotenv()
database_url = os.getenv('SQLALCHEMY_URL')

if not database_url:
    raise ValueError("Переменная окружения 'SQLALCHEMY_URL' не задана!")
print(f"SQLALCHEMY_URL: {database_url}")

# Создаем асинхронный движок базы данных
engine = create_async_engine(url=database_url)

# Создаем фабрику асинхронных сессий
async_session = async_sessionmaker(engine)


class RegistrationState(StatesGroup):
    waiting_for_sex = State()
    waiting_for_opros = State()
    waiting_for_bot_name = State()
    waiting_for_age = State()
    waiting_for_name = State()


class Avatarka(StatesGroup):
    waiting_for_pic = State()


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
    sex: Mapped[str] = mapped_column(String(120), nullable=False)
    years: Mapped[int] = mapped_column(nullable=False)
    unic_your_id: Mapped[str] = mapped_column(String(120), nullable=False)
    unic_wanted_id: Mapped[str] = mapped_column(String(120), nullable=False)



async def async_main():
    async with engine.begin() as conn:
        # Синхронно выполняем создание всех таблиц
        await conn.run_sync(Base.metadata.create_all)
