import time

import jwt
from aiohttp import web, ClientSession

from config import SECRET_KEY, ALGORITHM, TASK_API_URL
from engine import user_repo, redis_db
from service.service import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    refresh_access_token
)


async def init_app(app: web.Application):
    time.sleep(10)
    await user_repo.db.connect()
    await user_repo.db.create_tables()


@web.middleware
async def auth_middleware(request, handler):
    """Middleware для авторизации пользователя."""
    if request.path.startswith('/auth'):
        return await handler(request)

    auth_header = request.headers.get("Authorization")
    refresh_token = request.headers.get("refresh_token")

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request["username"] = payload['sub']
        except jwt.ExpiredSignatureError:
            if refresh_token:
                try:
                    new_access_token = await refresh_access_token(refresh_token)
                    if not new_access_token:
                        return web.json_response({"error": "Invalid refresh token"}, status=401)
                    else:
                        payload = jwt.decode(new_access_token, SECRET_KEY, algorithms=[ALGORITHM])
                        request["username"] = payload['sub']
                        response = await handler(request)
                        response.headers['Authorization'] = f"Bearer {new_access_token}"
                        return response
                except web.HTTPUnauthorized:
                    return web.json_response({"error": "Invalid refresh token"}, status=401)
        except jwt.PyJWTError:
            return web.json_response({"error": "Invalid token"}, status=401)

    else:
        return web.json_response({"error": "Invalid credentials"}, status=400)

    return await handler(request)


# Маршрут для регистрации пользователя
async def register(request):
    """Регистрация пользователя."""
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return web.json_response({"error": "Missing username or password"}, status=400)

    if await user_repo.get_by_username(username):
        return web.json_response({"error": "User already exists"}, status=400)

    user = await user_repo.create(username, await get_password_hash(password))
    return web.json_response({"msg": f"User registered successfully. ID {user.id}"}, status=201)


# Маршрут для входа в систему
async def login(request):
    """Вход в систему."""
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    hashed_password = await user_repo.get_hashed_password(username)
    if not hashed_password or not await verify_password(password, hashed_password):
        return web.json_response({"error": "Invalid credentials"}, status=400)

    access_token = await create_access_token({"sub": username})
    refresh_token = await create_refresh_token({"sub": username})

    return web.json_response({"access_token": access_token, "refresh_token": refresh_token})


# Маршрут для обновления access токена
async def refresh(request):
    """Обновление access токена."""
    data = await request.json()
    refresh_token = data.get("refresh_token")
    username = await redis_db.get(refresh_token)

    if not username:
        return web.json_response({"error": "Invalid refresh token"}, status=401)

    new_access_token = await create_access_token({"sub": username.decode('utf-8')})
    return web.json_response({"access_token": new_access_token})


async def create_task(request):
    """Создание новой задачи через API."""
    data = await request.json()
    user = await user_repo.get_by_username(request.get('username'))
    data['user_id'] = str(user.id)
    async with ClientSession() as session:
        async with session.post(f'{TASK_API_URL}/tasks', json=data) as response:
            return web.json_response(await response.json())


async def get_tasks(request):
    """Получение списка задач от API."""
    user = await user_repo.get_by_username(request.get('username'))
    async with ClientSession() as session:
        async with session.get(f'{TASK_API_URL}/tasks?user_id={user.id}') as response:
            data = await response.json()
            return web.json_response({"tasks": data})


async def update_task(request):
    """Обновление задачи через API."""
    task_id = request.match_info.get('id')
    async with ClientSession() as session:
        async with session.put(f'{TASK_API_URL}/tasks/{task_id}', json=await request.json()) as response:
            return web.json_response(await response.json())


async def delete_task(request):
    """Удаление задачи через API."""
    task_id = request.match_info.get('id')
    async with ClientSession() as session:
        async with session.delete(f'{TASK_API_URL}/tasks/{task_id}') as response:
            return web.json_response(await response.json())


app = web.Application(middlewares=[auth_middleware])
app.on_startup.append(init_app)

app.router.add_post('/auth/register', register)
app.router.add_post('/auth/login', login)
app.router.add_post('/auth/refresh', refresh)

app.router.add_post('/tasks', create_task)
app.router.add_get('/tasks', get_tasks)
app.router.add_put('/tasks/{id}', update_task)
app.router.add_delete('/tasks/{id}', delete_task)


if __name__ == '__main__':
    web.run_app(app, port=8080)
