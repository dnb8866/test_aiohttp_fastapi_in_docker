# Тестовое задание на FastAPI и aiohttp с использованием PostgreSQL, Redis, Docker Compose

## Установка
1. Клонируйте репозиторий.
2. Выполните из корневой папки команду docker compose up --build

## Использование
- Основной сервис доступен по адресу localhost:8080.
- Сервис FastAPI доступен по адресу localhost:8010.
- Всё взаимодействие через основной сервис.
- Прямой доступ к FastAPI не закрыт, для демонстрации работы.
- Используется аутентификация с использованием access и refresh токенов.
- 