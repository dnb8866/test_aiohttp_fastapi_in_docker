from engine import task_repo, app
from service.schemas import BaseTaskSchema, TaskSchema


@app.post('/tasks', response_model=TaskSchema)
async def create_task(task: BaseTaskSchema) -> TaskSchema:
    """Создание задачи."""
    return await task_repo.create(task)


@app.get('/tasks', response_model=list[TaskSchema])
async def get_tasks(user_id: int) -> list[TaskSchema]:
    """Получение задач пользователя."""
    return await task_repo.filter(user_id)


@app.get('/tasks/filter', response_model=list[TaskSchema])
async def filter_tasks(user_id: int, status: str) -> list[TaskSchema]:
    """Фильтрация задач пользователя по статусу."""
    return await task_repo.filter(user_id, status)


@app.put('/tasks/{task_id}', response_model=TaskSchema)
async def update_task(task_id: int, task: BaseTaskSchema) -> TaskSchema:
    """Обновление задачи."""
    return await task_repo.update(task_id, task)


@app.delete('/tasks/{task_id}')
async def delete_task(task_id: int):
    """Удаление задачи."""
    await task_repo.delete(task_id)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8010)