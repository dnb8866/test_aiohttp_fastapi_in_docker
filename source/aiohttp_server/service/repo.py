from .database import PostgresDb
from .models import User


class Repository:
    """Базовый класс репозитория."""

    def __init__(self, db: PostgresDb):
        self.db = db


class UserRepository(Repository):
    """Класс, реализующий CRUD операции в БД для пользователей."""

    async def create(self, username: str, password_hash: str) -> User:
        """
        Создание пользователя в БД.

        :param username: Логин пользователя.
        :param password_hash: Хэш пароля пользователя.
        :return: Объект пользователя.
        """
        async with self.db.pool.acquire() as con:
            query = 'INSERT INTO users (username, password_hash) VALUES ($1, $2)'
            await con.execute(query, username, password_hash)
            user_id = await con.fetchval('SELECT lastval()')
            return User(id=user_id, username=username)

    async def get(self, user_id: int) -> User | None:
        """
        Получение пользователя из БД по его идентификатору.

        :param user_id: Идентификатор пользователя.
        :return: Объект пользователя или None, если пользователь не найден.
        """
        async with self.db.pool.acquire() as con:
            query = 'SELECT id, username FROM users WHERE id = $1'
            result = await con.fetchrow(query, user_id)
            return User(id=result['id'], username=result['username']) if result else None

    async def get_by_username(self, username: str) -> User | None:
        """
        Получение пользователя из БД по его логину.

        :param username: Логин пользователя.
        :return: Объект пользователя или None, если пользователь не найден.
        """
        async with self.db.pool.acquire() as con:
            query = 'SELECT id, username FROM users WHERE username = $1'
            result = await con.fetchrow(query, username)
            return User(id=result['id'], username=result['username']) if result else None

    async def get_hashed_password(self, username: str) -> str | None:
        """
        Получение хэша пароля пользователя из БД по его логину.

        :param username: Логин пользователя.
        :return: Хэш пароля пользователя или None, если пользователь не найден.
        """
        await self.db.connect()
        async with self.db.pool.acquire() as con:
            query = 'SELECT password_hash FROM users WHERE username = $1'
            result = await con.fetchval(query, username)
            return result if result else None

    async def update(self, user_id: int, new_password_hash: str) -> User:
        """
        Обновление хеша пароля пользователя в БД.

        :param user_id: Идентификатор пользователя.
        :param new_password_hash: Новый хеш пароля.
        :return: Обновленный объект пользователя.
        """
        async with self.db.pool.acquire() as con:
            user = await self.get(user_id)
            if not user:
                raise ValueError('User not found')
            query = 'UPDATE users SET password_hash = $1 WHERE id = $2'
            await con.execute(query, new_password_hash, user_id)
            return await self.get(user_id)

    async def delete(self, user_id: int) -> None:
        """
        Удаление пользователя из БД по его идентификатору.
        :param user_id: Идентификатор пользователя.
        """
        async with self.db.pool.acquire() as con:
            if not await self.get(user_id):
                raise ValueError('User not found')
            query = 'DELETE FROM users WHERE id = $1'
            await con.execute(query, user_id)
