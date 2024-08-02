from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from .database import models, db
from . import schemas


SECRET_KEY = "403ddc0d53f555e12662e042e516e19f569790e1da8532bdd5ee00d225e947d1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """
    Проверяет соответствие открытого пароля хешированному.

    Args:
        plain_password (str): Открытый пароль.
        hashed_password (str): Хешированный пароль.

    Returns:
        bool: True, если пароли совпадают, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Создает хеш пароля.

    Args:
        password (str): Пароль для хеширования.

    Returns:
        str: Хешированный пароль.
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    """
    Аутентифицирует пользователя.

    Args:
        db (Session): Сессия базы данных.
        username (str): Имя пользователя.
        password (str): Пароль пользователя.

    Returns:
        User: Объект пользователя, если аутентификация успешна, иначе False.
    """
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Создает JWT токен доступа.

    Args:
        data (dict): Данные для включения в токен.
        expires_delta (timedelta, optional): Время жизни токена.

    Returns:
        str: Закодированный JWT токен.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(db.get_db)
):
    """
    Получает текущего пользователя по токену.

    Args:
        token (str): JWT токен.
        db (Session): Сессия базы данных.

    Returns:
        User: Объект текущего пользователя.

    Raises:
        HTTPException: Если токен недействителен или пользователь не найден.
    """
    data_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise data_exception
    except JWTError:
        raise data_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise data_exception
    return user


async def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user),
):
    """
    Получает текущего активного пользователя.

    Args:
        current_user (schemas.User): Текущий пользователь.

    Returns:
        User: Объект текущего активного пользователя.
    """
    return current_user
