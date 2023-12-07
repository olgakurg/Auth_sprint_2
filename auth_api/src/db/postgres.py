from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ..core.config import settings

dsn = f'postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'
engine = create_async_engine(dsn, echo=settings.db_echo, future=True)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
