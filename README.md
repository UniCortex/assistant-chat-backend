# Университетский AI‑ассистент — бэкенд

Clean Architecture + тактическое DDD‑приложение для постановки вопросов в очередь.  
Собрано на FastAPI, Dishka (DI), NATS, Redis, uvloop.

---

## Обзор архитектуры

```text
src/app/
├── domain/           # Чистые бизнес‑правила — ни одного импорта из фреймворков/библиотек
├── application/      # Обработчики CQRS, порты (интерфейсы), прикладные исключения
├── infrastructure/   # Адаптеры: Redis, NATS (реализации портов слоя application)
├── presentation/     # HTTP‑контроллеры, Pydantic‑схемы, обработчики ошибок
└── setup/            # Фабрика приложения, IoC‑провайдеры Dishka, настройки
```

### Ключевые принципы

| Принцип | Как применяется |
|---|---|
| **Инверсия зависимостей** | Каждая инфраструктурная деталь скрыта за `ABC`‑портом в `application/common/ports/` |
| **Без глобального состояния** | Все подключения (Redis, NATS) принадлежат Dishka‑провайдерам со скоупом `APP` и внедряются через DI — никогда не хранятся в модульных глобальных переменных |
| **CQRS** | Путь записи → `SubmitQuestionHandler` (command); путь чтения → `PollAnswerHandler`, `StreamAnswerHandler` (queries) |
| **Тактическое DDD** | `Message` — агрегатный корень; `SessionId`, `MessageId`, `QuestionText` — value object’ы; `QuestionDomainService` создаёт агрегаты |
| **По‑маршрутная обработка ошибок** | Доменные и прикладные исключения переводятся в HTTP‑ответы на уровне контроллеров и не «протекают» наружу |
| **Скоупы Dishka** | `APP` — для инфраструктурных синглтонов; `REQUEST` — для CQRS‑обработчиков |

---

## Потоки

### Отправка вопроса (`POST /api/v1/queuing/`)

```text
HTTP‑контроллер
  └─ SubmitQuestionCommand
       └─ SubmitQuestionHandler
            ├─ SessionRepository.create_or_renew()        [Redis]
            ├─ QuestionDomainService.create_message()     [чистый домен]
            ├─ MessageStatusRepository.set_processing()   [Redis]
            └─ QuestionPublisher.publish()                [NATS]
```

### Опрос ответа (`GET /api/v1/queuing/`)

```text
HTTP‑контроллер
  └─ PollAnswerQuery
       └─ PollAnswerHandler
            ├─ MessageStatusRepository.get_status()   [Redis]
            └─ MessageResultRepository.get_answer()   [Redis]
```

### Стриминг ответа (`GET /api/v1/queuing/stream`)

```text
HTTP‑контроллер → StreamingResponse(SSE)
  └─ StreamAnswerHandler
       └─ AnswerStreamer.stream()   [подписка на NATS → асинхронный генератор]
```

---

## Требования

- **Python 3.13**
- **Poetry** — управление зависимостями
- **Docker и Docker Compose** — для Redis, NATS и опционально бэкенда

---

## Переменные окружения

Скопируйте пример и при необходимости отредактируйте:

```bash
cp .env.example .env
```

| Переменная | Описание | Пример |
|------------|----------|--------|
| `REDIS_URL` | URL Redis | Локально: `redis://localhost:6379/0`, в Docker: `redis://redis:6379/0` |
| `NATS_URL` | URL NATS | Локально: `nats://localhost:4222`, в Docker: `nats://nats:4222` |
| `NATS_SUBJECT_QUESTIONS` | Топик для вопросов | `assistant.questions` |
| `NATS_SUBJECT_ANSWERS_PREFIX` | Префикс топиков ответов | `assistant.answers.` |
| `SESSION_TTL` | TTL сессии в секундах | `43200` |
| `PROCESSING_TTL` | TTL статуса «в обработке» | `300` |
| `RESULT_TTL` | TTL результата в Redis | `900` |
| `HOST` | Хост uvicorn | `0.0.0.0` |
| `PORT` | Порт приложения | `8000` |
| `WORKERS` | Число воркеров uvicorn | `4` |
| `LOG_LEVEL` | Уровень логов | `INFO` |

---

## Запуск

### Вариант 1: Локальная разработка (бэкенд на хосте)

Инфраструктура в Docker, приложение через Poetry:

```bash
poetry install
cp .env.example .env
# В .env укажите REDIS_URL=redis://localhost:6379/0 и NATS_URL=nats://localhost:4222

# Поднять только Redis и NATS
docker compose up -d redis nats

# Запуск приложения
make run
```

API будет доступен на **http://localhost:8000**.

### Вариант 2: Всё в Docker

```bash
cp .env.example .env
# В .env оставьте REDIS_URL=redis://redis:6379/0 и NATS_URL=nats://nats:4222 (имена сервисов)

docker compose up -d
```

Поднимаются Redis (порт 6379), NATS (4222, мониторинг 8222) и бэкенд (порт 8000). API: **http://localhost:8000**.

### Полезные команды (Makefile)

| Команда | Действие |
|---------|----------|
| `make app` | Запустить все сервисы в фоне (`docker compose up -d`) |
| `make run` | Запустить бэкенд локально через Poetry |
| `make app-build` | Пересобрать образ бэкенда |
| `make app-down` | Остановить контейнеры |
| `make app-restart` | Остановить и снова поднять контейнеры |

---

## Запуск тестов

```bash
make test
```

Проверка типов:

```bash
make typecheck
```

---

## Добавление новой фичи (пример: лимитирование запросов по сессии)

1. **Domain** — добавить value object `RateLimit` или обогатить сущность `Session`, если нужно.
2. **Application port** — объявить `RateLimiter(ABC)` в `application/common/ports/`.
3. **Infrastructure adapter** — реализовать лимитер через Redis (скользящее окно) в `infrastructure/adapters/`.
4. **IoC** — зарегистрировать адаптер в `setup/ioc/infrastructure.py`.
5. **Handler** — внедрить и вызывать его в `SubmitQuestionHandler`.

Другие слои менять не требуется.
