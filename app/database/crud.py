from sqlalchemy.orm import Session
from . import models
from .. import schemas, auth


def get_user(db: Session, user_id: int):
    """
    Получает пользователя по его ID.

    Args:
        db (Session): Сессия базы данных.
        user_id (int): ID пользователя.

    Returns:
        User: Объект пользователя или None, если пользователь не найден.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    """
    Получает пользователя по его имени пользователя.

    Args:
        db (Session): Сессия базы данных.
        username (str): Имя пользователя.

    Returns:
        User: Объект пользователя или None, если пользователь не найден.
    """
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Создает нового пользователя.

    Args:
        db (Session): Сессия базы данных.
        user (schemas.UserCreate): Данные для создания пользователя.

    Returns:
        User: Созданный объект пользователя.
    """
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_task(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """
    Получает список задач пользователя.

    Args:
        db (Session): Сессия базы данных.
        user_id (int): ID пользователя.
        skip (int, optional): Количество пропускаемых задач. По умолчанию 0.
        limit (int, optional): Максимальное количество возвращаемых задач. По умолчанию 10.

    Returns:
        List[Task]: Список задач пользователя.
    """
    return (
        db.query(models.Task)
        .filter(
            (models.Task.owner_id == user_id)
            | (
                models.Task.id.in_(
                    db.query(models.TaskPermission.task_id).filter(
                        models.TaskPermission.user_id == user_id
                    )
                )
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    """
    Создает новую задачу.

    Args:
        db (Session): Сессия базы данных.
        task (schemas.TaskCreate): Данные для создания задачи.
        user_id (int): ID пользователя, создающего задачу.

    Returns:
        Task: Созданный объект задачи.
    """
    db_task = models.Task(**task.model_dump(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def give_task_permission(
    db: Session, task_id: int, owner_id: int, user_id: int, permission_type: str
):
    """
    Предоставляет разрешение на задачу другому пользователю.

    Args:
        db (Session): Сессия базы данных.
        task_id (int): ID задачи.
        owner_id (int): ID владельца задачи.
        user_id (int): ID пользователя, которому предоставляется разрешение.
        permission_type (str): Тип разрешения.

    Returns:
        TaskPermission: Объект разрешения на задачу или None, если задача не найдена.
    """
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.owner_id == owner_id)
        .first()
    )
    if not task:
        return None
    db_permission = models.TaskPermission(
        task_id=task_id, user_id=user_id, permission_type=permission_type
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def update_task(db: Session, task_id: int, task_data: schemas.TaskUpdate, user_id: int):
    """
    Обновляет задачу.

    Args:
        db (Session): Сессия базы данных.
        task_id (int): ID задачи.
        task_data (schemas.TaskUpdate): Данные для обновления задачи.
        user_id (int): ID пользователя, обновляющего задачу.

    Returns:
        Task: Обновленный объект задачи или None, если задача не найдена или нет прав на обновление.
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return None

    if task.owner_id != user_id:
        permission = (
            db.query(models.TaskPermission)
            .filter(
                models.TaskPermission.task_id == task_id,
                models.TaskPermission.user_id == user_id,
                models.TaskPermission.permission_type == "update",
            )
            .first()
        )
        if not permission:
            return None

    for key, value in task_data.model_dump().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int, user_id: int):
    """
    Удаляет задачу.

    Args:
        db (Session): Сессия базы данных.
        task_id (int): ID задачи.
        user_id (int): ID пользователя, удаляющего задачу.

    Returns:
        Task: Удаленный объект задачи или None, если задача не найдена или нет прав на удаление.
    """
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.owner_id == user_id)
        .first()
    )
    if not task:
        return None
    db.delete(task)
    db.commit()
    return task


def revoke_task_permission(db: Session, task_id: int, owner_id: int, user_id: int):
    """
    Отзывает разрешение на задачу у пользователя.

    Args:
        db (Session): Сессия базы данных.
        task_id (int): ID задачи.
        owner_id (int): ID владельца задачи.
        user_id (int): ID пользователя, у которого отзывается разрешение.

    Returns:
        TaskPermission: Объект разрешения на задачу или None, если разрешение не найдено.
    """
    permission = (
        db.query(models.TaskPermission)
        .filter(
            models.TaskPermission.task_id == task_id,
            models.TaskPermission.user_id == user_id,
        )
        .first()
    )
    if not permission:
        return None
    db.delete(permission)
    db.commit()
    return permission
