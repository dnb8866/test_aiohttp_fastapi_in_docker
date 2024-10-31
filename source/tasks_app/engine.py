import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import POSTGRES_URL
from service.database import Database
from service.repo import TaskRepository

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Запуск приложения.")
    time.sleep(10)
    await db.connect()
    await db.create_tables()
    yield
    await db.disconnect()
    logger.debug("Остановка приложения.")

app = FastAPI(lifespan=lifespan)
db = Database(POSTGRES_URL)
task_repo = TaskRepository(db)
