import contextlib
import redis.asyncio as redis_async
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.conf.config import settings


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     expire_on_commit=False, bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db():
    async with sessionmanager.session() as session:
        yield session


sessionmanager = DatabaseSessionManager(settings.db_local_url)

db_redis = redis_async.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                             decode_responses=True)