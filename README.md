# ToDO


## Требования

- Python 3.12.2
- [Poetry](https://python-poetry.org/docs/#installation)

## Установка и запуск

### Шаг 1: Клон репозитория


Сначала клонируйте репозиторий и перейдите в директорию проекта:

```sh
git clone https://github.com/tema2395/ToDo
```


### Шаг 2: Установка зависимостей

Установите зависимости и активируйте виртуальное окружение

```sh
poetry install
poetry shell
```

### Шаг 3: Запуск приложения

```sh
poetry run uvicorn app.main:app --reload
```
## Эндпоинты

- `POST /users/` - Регистрация пользователя
- `GET /token` - Вход для получения токена
- `GET /users/me` - Просмотр своего id
- `POST /tasks/` -  Создание задачи
- `GET /tasks/` - Просмотр задач
- `PUT /tasks/{task_id}` - Обновление существующей задачи
- `DELETE /tasks/{task_id}` - Удаление задачи
- `POST /tasks/{task_id}/permissions/` - Разрешение на просмотр и обновление задач другому пользователю
- `DELETE /tasks/{task_id}/permissions/` - Удаление разрешения на просмотр и обновление задач другому пользователю