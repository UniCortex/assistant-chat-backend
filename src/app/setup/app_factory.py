from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.web.tracing import tracing_middleware
from app.presentation.http.controllers.root_router import api_v1_router
from app.presentation.http.errors.handlers import register_error_handlers
from app.setup.config.logging import configure_logging
from app.setup.config.settings import AppSettings
from app.setup.ioc.application import ApplicationProvider
from app.setup.ioc.domain import DomainProvider
from app.setup.ioc.infrastructure import InfrastructureProvider
from app.setup.ioc.settings import SettingsProvider


def create_app() -> FastAPI:
    settings = AppSettings()
    configure_logging(settings)

    container = make_async_container(
        SettingsProvider(),
        InfrastructureProvider(),
        DomainProvider(),
        ApplicationProvider(),
    )

    app = FastAPI(
        title="University AI Assistant",
        version="1.0.0",
        description="Clean-Architecture + DDD backend for question queuing.",
    )

    app.middleware("http")(tracing_middleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router)
    register_error_handlers(app)
    setup_dishka(container, app)

    return app
