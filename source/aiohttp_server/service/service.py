import datetime

import jwt
from passlib.context import CryptContext

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, REFRESH_TOKEN_EXPIRE_DAYS
from engine import redis_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_access_token(
        data: dict,
        expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    """
    Создание access токена.

    :param data: Входной словарь для создания access токена.
    :param expires_delta: Время жизни access токена (в минутах).
    :return: Access токен в формате JWT.
    """
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def create_refresh_token(data: dict) -> str:
    """
    Создание refresh токена.

    :param data: Входной словарь для создания refresh токена.
    :return: Refresh токен в формате JWT.
    """
    refresh_token = jwt.encode(data.copy(), SECRET_KEY, algorithm=ALGORITHM)
    await redis_db.set(refresh_token, data['sub'], ex=datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    return refresh_token


async def verify_password(plain_password, hashed_password) -> bool:
    """
    Проверка пароля.

    :param plain_password: Пароль в открытом виде.
    :param hashed_password: Хеш пароля.
    :return: True, если пароли совпадают, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password) -> str:
    """
    Получение хеша пароля.

    :param password: Пароль в открытом виде.
    :return: Хеш пароля.
    """
    return pwd_context.hash(password)

async def refresh_access_token(refresh_token: str) -> str | bool:
    """
    Обновление access токена по refresh токену.

    :param refresh_token: Refresh токен.
    :return: Access токен в формате JWT.
    """
    username = await redis_db.get(refresh_token)
    if not username:
        return False
    new_access_token = await create_access_token({"sub": username.decode('utf-8')})
    return new_access_token