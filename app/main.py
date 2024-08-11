from contextlib import asynccontextmanager
from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import models, crud, db
from .database.db import engine
from . import schemas, auth


models.Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(db.get_db)):
    """
    Создает нового пользователя.

    Args:
        user (schemas.UserCreate): Данные для создания пользователя.
        db (Session): Сессия базы данных.

    Returns:
        schemas.User: Созданный пользователь.

    Raises:
        HTTPException: Если имя пользователя уже зарегистрировано.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400, detail="Имя пользователя уже зарегистрировано"
        )
    return crud.create_user(db=db, user=user)


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db.get_db)
):
    """
    Аутентифицирует пользователя и возвращает токен доступа.

    Args:
        form_data (OAuth2PasswordRequestForm): Данные формы аутентификации.
        db (Session): Сессия базы данных.

    Returns:
        schemas.Token: Токен доступа.

    Raises:
        HTTPException: Если аутентификация не удалась.
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(
    current_user: schemas.User = Depends(auth.get_current_active_user),
):
    """
    Возвращает информацию о текущем пользователе.

    Args:
        current_user (schemas.User): Текущий аутентифицированный пользователь.

    Returns:
        schemas.User: Информация о текущем пользователе.
    """
    return current_user


@app.post("/tasks/", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(db.get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user),
):
    """
    Создает новую задачу для текущего пользователя.

    Args:
        task (schemas.TaskCreate): Данные для создания задачи.
        db (Session): Сессия базы данных.
        current_user (schemas.User): Текущий аутентифицированный пользователь.

    Returns:
        schemas.Task: Созданная задача.
    """
    return crud.create_task(db=db, task=task, user_id=current_user.id)


@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(db.get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user),
):
    """
    Возвращает список задач текущего пользователя.

    Args:
        skip (int): Количество пропускаемых задач.
        limit (int): Максимальное количество возвращаемых задач.
        db (Session): Сессия базы данных.
        current_user (schemas.User): Текущий аутентифицированный пользователь.

    Returns:
        list[schemas.Task]: Список задач пользователя.
    """
    tasks = crud.get_task(db, user_id=current_user.id, skip=skip, limit=limit)
    return tasks


@app.put("/tasks/{task_id}/", response_model=schemas.Task)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(db.get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user),
):
    """
    Обновляет задачу.

    Args:
        task_id (int): ID задачи для обновления.
        task (schemas.TaskUpdate): Данные для обновления задачи.
        db (Session): Сессия базы данных.
        current_user (schemas.User): Текущий аутентифицированный пользователь.

    Returns:
        schemas.Task: Обновленная задача.

    Raises:
        HTTPException: Если задача не найдена или у пользователя нет прав на её обновление.
    """
    db_task = crud.update_task(
        db=db, task_id=task_id, task_data=task, user_id=current_user.id
    )
    if db_task is None:
        raise HTTPException(
            status_code=404, detail="Задача не найдена или у вас нет прав на её обновление"
        )
    return db_task


@app.delete("/tasks/{task_id}/", response_model=schemas.Task)
def delete_task(
    task_id: int,
    db: Session = Depends(db.get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user),
):
    """
    Удаляет задачу.

    Args:
        task_id (int): ID задачи для удаления.
        db (Session): Сессия базы данных.
        current_user (schemas.User): Текущий аутентифицированный пользователь.

    Returns:
        schemas.Task: Удаленная задача.

    Raises:
        HTTPException: Если задача не найдена или пользователь не является её владельцем.
    """
    db_task = crud.delete_task(db=db, task_id=task_id, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(
            status_code=404, detail="Задача не найдена или вы не являетесь его владельцем"
        )
    return db_task


@app.post("/tasks/{task_id}/permissions/", response_model=schemas.TaskPermission)
def give_task_permission(
    task_id: int,
    permission: schemas.TaskPermissionCreate,
    db: Session = Depends(db.get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user),
):
    """
    Предоставляет разрешение на задачу другому пользователю.

    Args:
        task_id (int): ID задачи.
        permission (schemas.TaskPermissionCreate): Данные о разрешении.
        db (Session): Сессия базы данных.
        current_user (schemas.User): Текущий аутентифицированный пользователь.

    Returns:
        schemas.TaskPermission: Созданное разрешение.

    Raises:
        HTTPException: Если задача не найдена или пользователь не является её владельцем.
    """
    db_permission = crud.give_task_permission(
        db, task_id, current_user.id, permission.user_id, permission.permission_type
    )
    if db_permission is None:
        raise HTTPException(
            status_code=404, detail="Задача не найдена или вы не являетесь его владельцем"
        )
    return db_permission


@app.delete("/tasks/{task_id}/permissions/", response_model=schemas.TaskPermission)
def revoke_task_permission(
    task_id: int,
    user_id: int,
    db: Session = Depends(db.get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user),
):
    """
    Отзывает разрешение на задачу у пользователя.

    Args:
        task_id (int): ID задачи.
        user_id (int): ID пользователя, у которого отзывается разрешение.
        db (Session): Сессия базы данных.
        current_user (schemas.User): Текущий аутентифицированный пользователь.

    Returns:
        schemas.TaskPermission: Отозванное разрешение.

    Raises:
        HTTPException: Если разрешение не найдено или пользователь не является владельцем задачи.
    """
    db_permission = crud.revoke_task_permission(db, task_id, current_user.id, user_id)
    if db_permission is None:
        raise HTTPException(
            status_code=404, detail="Разрешение не найдено или вы не являетесь владельцем"
        )
    return db_permission
