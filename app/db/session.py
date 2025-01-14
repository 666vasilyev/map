from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings

async_engine: AsyncEngine = create_async_engine(settings.ASYNC_DATABASE_URL, future=True)

# Создание асинхронной фабрики сеансов
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)