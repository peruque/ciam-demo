from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.router import router
import logging.config
from pathlib import Path

app = FastAPI()

log_config_path = Path.cwd() / "app" / "logging.conf"

logging.config.fileConfig(log_config_path, disable_existing_loggers=False)

app.mount(
    "/static", StaticFiles(directory=Path.cwd() / "app" / "static"), name="static"
)
app.include_router(router)
