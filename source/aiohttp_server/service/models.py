from dataclasses import dataclass


@dataclass
class User:
    """Дата класс пользователя."""

    id: int
    username: str
