FROM python:3.13-slim
LABEL authors="zuko1337"

RUN pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry install --only main --no-root

COPY ./src /app/src

WORKDIR /app
