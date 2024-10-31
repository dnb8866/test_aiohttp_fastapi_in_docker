from .database import Database
from .schemas import BaseTaskSchema, TaskSchema


class Repository:
    """Базовый класс для репозитория."""
    def __init__(self, db: Database):
        self.db = db


class TaskRepository(Repository):
    """Репозиторий для работы с задачами."""

    async def create(self, task: BaseTaskSchema) -> TaskSchema:
        """
        Создание новой задачи.

        :param task: Задача для создания.
        :return: Созданная задача.
        """
        async with self.db.pool.acquire() as con:
            query = 'INSERT INTO tasks (title, description, status, user_id) VALUES ($1, $2, $3, $4)'
            await con.execute(query, task.title, task.description, task.status, task.user_id)
            task_id = await con.fetchval('SELECT lastval()')
            return TaskSchema(
                id=task_id,
                title=task.title,
                description=task.description,
                status=task.status,
                user_id=task.user_id,
            )

    async def get(self, task_id: int) -> TaskSchema:
        """
        Получение задачи по идентификатору.

        :param task_id: Идентификатор задачи.
        :return: Задача или None, если такой задачи нет.
        """
        async with self.db.pool.acquire() as con:
            query = 'SELECT * FROM tasks WHERE id = $1'
            result = await con.fetchrow(query, task_id)
            return TaskSchema(
                id=result['id'],
                title=result['title'],
                description=result['description'],
                status=result['status'],
                user_id=result['user_id']
            ) if result else None

    async def filter(self, user_id: int, status: str = None) -> list:
        """
        Получение списка задач для конкретного пользователя с опциональным фильтром по статусу.

        :param user_id: Идентификатор пользователя.
        :param status: Статус задачи (optional).
        :return: Список задач.
        """
        async with self.db.pool.acquire() as con:
            query = 'SELECT * FROM tasks WHERE user_id = $1'
            if status:
                query += ' AND status = $2'
                result = await con.fetch(query, user_id, status)
            else:
                result = await con.fetch(query, user_id)
            return [TaskSchema(**row) for row in result]

    async def update(self, task_id, task: TaskSchema) -> TaskSchema:
        """
        Обновление задачи.

        :param task_id: Идентификатор задачи.
        :param task: Задача с новыми данными.
        :return: Обновленная задача.
        """
        async with self.db.pool.acquire() as con:
            if not await self.get(task_id):
                raise ValueError('Task not found')
            query = 'UPDATE tasks SET title = $1, description = $2, status = $3 WHERE id = $4'
            await con.execute(query, task.title, task.description, task.status, task_id)
            return await self.get(task_id)

    async def delete(self, task_id: int) -> None:
        """
        Удаление задачи.

        :param task_id: Идентификатор задачи.
        """
        async with self.db.pool.acquire() as con:
            if not await self.get(task_id):
                raise ValueError('Task not found')
            query = 'DELETE FROM tasks WHERE id = $1'
            await con.execute(query, task_id)
