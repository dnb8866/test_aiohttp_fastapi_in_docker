# Тестовое задание на FastAPI и aiohttp с использованием PostgreSQL, Redis, Docker Compose

## Установка
1. Клонируйте репозиторий.
2. Переименуйте .env.example в .env
3. Выполните из корневой папки команду docker compose up --build

## Использование
- Основной сервис доступен по адресу localhost:8080.
- Сервис FastAPI доступен по адресу localhost:8010.
- Всё взаимодействие через основной сервис.
- Прямой доступ к FastAPI не закрыт, для демонстрации работы.
- Используется аутентификация с использованием access и refresh токенов.


Регистрация пользователя (POST /auth/register): принимает username и password.

Вход в систему (POST /auth/login): возвращает access и refresh токены.

Обновление access токена (POST /auth/refresh) с использованием refresh токена.

Создание задачи (POST /tasks) с полями: title, description, status.

Получение списка всех задач пользователя (GET /tasks).

Обновление задачи (PUT /tasks/{id}) — редактирование названия, описания и статуса.

Удаление задачи (DELETE /tasks/{id}).
