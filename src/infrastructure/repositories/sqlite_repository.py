import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select

from src.application.ports.repository_port import RepositoryPort
from src.domain.entities.api_key import ApiKey
from src.domain.entities.usage_log import UsageLog

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
            statement = select(ApiKey).where(ApiKey.key == key, ApiKey.enabled)
            results = await session.execute(statement)
            return results.scalar_one_or_none()

    async def save_usage_log(self, log: UsageLog) -> None:
        async with self.async_session() as session:
            session.add(log)
            await session.commit()

    async def get_all_api_keys(self) -> List[ApiKey]:
        async with self.async_session() as session:
            statement = select(ApiKey).order_by(ApiKey.created_at.desc())
            results = await session.execute(statement)
            return list(results.scalars().all())

    async def update_api_key_status(self, key_id: str, enabled: bool) -> None:
        async with self.async_session() as session:
            statement = select(ApiKey).where(ApiKey.id == key_id)
            result = await session.execute(statement)
            api_key = result.scalar_one_or_none()
            if api_key:
                api_key.enabled = enabled
                await session.commit()

    async def get_recent_logs(self, limit: int = 50) -> List[UsageLog]:
        async with self.async_session() as session:
            statement = (
                select(UsageLog).order_by(UsageLog.timestamp.desc()).limit(limit)
            )
            results = await session.execute(statement)
            return list(results.scalars().all())

    async def create_api_key(self, name: str, key: Optional[str] = None) -> ApiKey:
        import secrets

        generated_key = key or f"zr-{secrets.token_urlsafe(24)}"
        new_key = ApiKey(key=generated_key, name=name)
        async with self.async_session() as session:
            session.add(new_key)
            await session.commit()
            await session.refresh(new_key)
            return new_key

    async def add_api_keys(self, keys: List[ApiKey]) -> None:
        async with self.async_session() as session:
            for k in keys:
                # Check if exists
                stmt = select(ApiKey).where(ApiKey.id == k.id)
                existing = (await session.execute(stmt)).scalar_one_or_none()
                if not existing:
                    session.add(k)
            await session.commit()

    async def delete_api_key(self, key_id: str) -> None:
        async with self.async_session() as session:
            statement = select(ApiKey).where(ApiKey.id == key_id)
            result = await session.execute(statement)
            api_key = result.scalar_one_or_none()
            if api_key:
                await session.delete(api_key)
                await session.commit()

    async def get_stats_summary(self) -> Dict[str, Any]:
        from sqlalchemy import func

        async with self.async_session() as session:
            # Общее кол-во
            count_stmt = select(func.count(UsageLog.id))
            total_calls = (await session.execute(count_stmt)).scalar() or 0

            # Успешные
            success_stmt = select(func.count(UsageLog.id)).where(UsageLog.success)
            success_calls = (await session.execute(success_stmt)).scalar() or 0

            # Среднее время
            avg_time_stmt = select(func.avg(UsageLog.duration_ms))
            avg_duration = (await session.execute(avg_time_stmt)).scalar() or 0

            return {
                "total_calls": total_calls,
                "success_calls": success_calls,
                "error_calls": total_calls - success_calls,
                "avg_duration_ms": round(float(avg_duration), 2) if avg_duration else 0,
            }
