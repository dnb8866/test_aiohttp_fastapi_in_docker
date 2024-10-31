import asyncpg


class Database:
    """Класс для работы с БД."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None

    async def connect(self):
        """Создание пула соединений с БД."""
        self.pool = await asyncpg.create_pool(self.database_url)

    async def disconnect(self):
        """Закрытие пула соединений с БД."""
        await self.pool.close()

    async def create_tables(self):
        """Создание таблиц в БД."""
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(30) NOT NULL,
                    user_id INTEGER NOT NULL 
                );
                """
            )
