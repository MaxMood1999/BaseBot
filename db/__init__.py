from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncAttrs
from sqlalchemy.orm import sessionmaker, DeclarativeBase, declared_attr
from db.config import Config


class Base(AsyncAttrs, DeclarativeBase):
    pass


class AsyncDatabaseSession:
    def __init__(self):
        self._session = None
        self._engine = None

    def __getattr__(self, name):
        return getattr(self._session, name)

    def init(self):
        self._engine = create_async_engine(
            Config.DB_CONFIG,
            future=True,
            echo=False,
            isolation_level="AUTOCOMMIT"

        )
        self._session = sessionmaker(self._engine, expire_on_commit=False,class_=AsyncSession)() # noqa

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self):
        """Asinxron sessiya yaratish uchun kontekst menejeri"""
        async with self._session_factory() as session:
            yield session

db = AsyncDatabaseSession()