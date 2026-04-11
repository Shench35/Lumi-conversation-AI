import asyncio
import sys
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.services.config import Config

# Windows compatibility fix for asyncio loop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# For Neon/Render, we often need to ensure SSL is handled correctly by the driver
connect_args = {}
if "neon.tech" in Config.DATABASE_URL or "ssl=require" in Config.DATABASE_URL:
    connect_args["ssl"] = True

engine = create_async_engine(
    Config.DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=connect_args
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session
