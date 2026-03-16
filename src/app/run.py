import uvicorn

from app.setup.app_factory import create_app
from app.setup.config.logging import configure_logging
from app.setup.config.settings import AppSettings

app = create_app()


if __name__ == "__main__":
    settings = AppSettings()
    log_config = configure_logging(settings)
    uvicorn.run(
        "app.run:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        loop="uvloop",
        reload=False,
        log_config=log_config,
    )
