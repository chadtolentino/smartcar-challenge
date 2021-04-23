import logging
from pathlib import Path

from fastapi import FastAPI

from .api.vehicles import router as vehicle_router
from .custom_logging import CustomizeLogger

logger = logging.getLogger(__name__)


config_path = Path(__file__).with_name("logging_config.json")
print(config_path)


def create_app() -> FastAPI:
    app = FastAPI()
    logger = CustomizeLogger.make_logger(config_path)
    app.logger = logger

    app.include_router(vehicle_router, prefix="/vehicles")

    return app


app = create_app()
