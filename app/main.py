from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.router import router

app = FastAPI()

app.mount(
    "/static", StaticFiles(directory=Path.cwd() / "app" / "static"), name="static"
)
app.include_router(router)
