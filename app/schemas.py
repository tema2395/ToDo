from pydantic import BaseModel


class UserBase(BaseModel):
    """
    Базовая схема пользователя.

    Attributes:
        username (str): Имя пользователя.
    """
    username: str


class UserCreate(UserBase):
    """
    Схема для создания пользователя.

    Attributes:
        password (str): Пароль пользователя.
    """
    password: str


class User(UserBase):
    """
    Схема пользователя с дополнительной информацией.

    Attributes:
        id (int): Уникальный идентификатор пользователя.
    """
    id: int

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    """
    Базовая схема задачи.

    Attributes:
        title (str): Заголовок задачи.
        description (str | None): Описание задачи (опционально).
    """
    title: str
    description: str | None = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    """
    Схема задачи с дополнительной информацией.

    Attributes:
        id (int): Уникальный идентификатор задачи.
        owner_id (int): Идентификатор владельца задачи.
    """
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class TaskPermissionCreate(BaseModel):
    """
    Схема для создания разрешения на задачу.

    Attributes:
        user_id (int): Идентификатор пользователя, которому выдается разрешение.
        permission_type (str): Тип разрешения.
    """
    user_id: int
    permission_type: str


class TaskPermission(TaskPermissionCreate):
    """
    Схема разрешения на задачу с дополнительной информацией.

    Attributes:
        id (int): Уникальный идентификатор разрешения.
        task_id (int): Идентификатор задачи, к которой относится разрешение.
    """
    id: int
    task_id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    """
    Схема токена аутентификации.

    Attributes:
        access_token (str): Токен доступа.
        token_type (str): Тип токена.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Схема данных токена.

    Attributes:
        username (str | None): Имя пользователя (опционально).
    """
    username: str | None = None


class TaskUpdate(BaseModel):
    """
    Схема для обновления задачи.

    Attributes:
        title (str | None): Новый заголовок задачи (опционально).
        description (str | None): Новое описание задачи (опционально).
    """
    title: str | None = None
    description: str | None = None
