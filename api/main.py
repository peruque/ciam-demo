from functools import lru_cache
from fastapi import Depends, FastAPI, Request
from typing_extensions import Annotated
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from . import config
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()

app.mount(
    "/static", StaticFiles(directory=Path.cwd() / "api" / "static"), name="static"
)

templates = Jinja2Templates(directory=Path.cwd() / "api" / "templates")


@lru_cache
def get_settings():
    return config.Settings()


@app.get("/")
async def info(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {
        "app_name": settings.app_name,
    }


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


@app.get("/home", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": {}})
