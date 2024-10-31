import redis.asyncio as redis
from aiohttp import web

import config
from service.database import PostgresDb
from service.repo import UserRepository

app = web.Application()

redis_db = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
postgres_db = PostgresDb(config.POSTGRES_URL)
user_repo = UserRepository(postgres_db)
