from typing import Optional, List
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select
from src.domain.entities.api_key import ApiKey
from src.domain.entities.usage_log import UsageLog
from src.application.ports.repository_port import RepositoryPort
import logging

logger = logging.getLogger(__name__)

class SQLiteRepository(RepositoryPort):
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

        # Включение WAL при подключении
        @event.listens_for(self.engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

    async def init_db(self) -> None:
        async with self.engine.begin() as conn:
            # Создание таблиц, если их нет
            await conn.run_sync(SQLModel.metadata.create_all)

    async def get_api_key(self, key: str) -> Optional[ApiKey]:
        async with self.async_session() as session:
            statement = select(ApiKey).where(ApiKey.key == key, ApiKey.enabled == True)
            results = await session.execute(statement)
            return results.scalar_one_or_none()

    async def save_usage_log(self, log: UsageLog) -> None:
        async with self.async_session() as session:
            session.add(log)
            await session.commit()

    async def add_api_keys(self, keys: List[ApiKey]) -> None:
        async with self.async_session() as session:
            for key in keys:
                # Проверка существования по ID или Key
                statement = select(ApiKey).where(ApiKey.key == key.key)
                res = await session.execute(statement)
                if not res.scalar_one_or_none():
                    session.add(key)
            await session.commit()
