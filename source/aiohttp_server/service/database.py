import asyncpg


class Database:
    """Базовый класс для БД."""

    def __init__(self, database_url: str):
        self.database_url = database_url


class PostgresDb(Database):
    """Класс для работы с PostgreSQL."""

    def __init__(self, database_url: str):
        super().__init__(database_url)
        self.pool = None

    async def connect(self) -> None:
        """Создание пула соединений с БД."""
        self.pool = await asyncpg.create_pool(self.database_url)

    async def disconnect(self) -> None:
        """Закрытие пула соединений с БД."""
        self.pool.close()

    async def create_tables(self) -> None:
        """Создание таблиц в БД."""
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL
                );
                """
            )
