FROM python:3.12-slim

WORKDIR /app

# Отключаем создание виртуального окружения и взаимодействие
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock /app/

# Обновляем pip, устанавливаем Poetry и зависимости
RUN pip install --upgrade pip && \
    pip install poetry

RUN poetry install --no-root

# Копируем весь проект в контейнер
COPY . /app

# Запускаем приложение с uvicorn, который теперь установлен глобально
CMD ["bash", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
