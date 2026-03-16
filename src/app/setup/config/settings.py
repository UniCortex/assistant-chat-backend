from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    redis_url: str = Field(..., alias="REDIS_URL")
    nats_url: str = Field(..., alias="NATS_URL")

    nats_subject_questions: str = Field(
        default="assistant.questions",
        alias="NATS_SUBJECT_QUESTIONS",
    )
    nats_subject_answers_prefix: str = Field(
        default="assistant.answers.",
        alias="NATS_SUBJECT_ANSWERS_PREFIX",
    )

    session_ttl: int = Field(default=43200, alias="SESSION_TTL")
    processing_ttl: int = Field(default=300, alias="PROCESSING_TTL")
    result_ttl: int = Field(default=900, alias="RESULT_TTL")

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=4, alias="WORKERS")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
