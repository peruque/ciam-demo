from functools import lru_cache
from fastapi import FastAPI, Depends, Request, HTTPException, status
from typing_extensions import Annotated
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from . import config
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from fastapi.security import OAuth2PasswordBearer
import httpx
from jwt import PyJWKClient
import jwt

app = FastAPI()

app.mount(
    "/static", StaticFiles(directory=Path.cwd() / "app" / "static"), name="static"
)

templates = Jinja2Templates(directory=Path.cwd() / "app" / "templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@lru_cache
def get_settings():
    return config.Settings()


async def get_token(request: Request):
    token = request.query_params.get("token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is required"
        )
    return token


async def get_current_user(
    settings: Annotated[config.Settings, Depends(get_settings)],
    token: str = Depends(get_token),
) -> str:
    JWKS_URL = f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/{settings.cognito_user_pool_id}/.well-known/jwks.json"
    client = PyJWKClient(JWKS_URL)

    try:
        header = jwt.get_unverified_header(token)
        key = client.get_signing_key(header["kid"])
        public_key = key.key
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )


@app.get("/info")
async def info(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {"app_name": settings.app_name}


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


@app.get("/", response_class=HTMLResponse)
async def user_login_page(
    request: Request,
    settings: Annotated[config.Settings, Depends(get_settings)],
):
    context = {
        "request": request,
        "auth_url": f"https://{settings.cognito_domain}/oauth2/authorize",
        "client_id": settings.cognito_client_id,
        "redirect_uri": settings.cognito_redirect_uri,
        "scope": "phone openid email",
    }
    return templates.TemplateResponse("login.html", context)


@app.get("/callback")
async def callback(
    code: str,
    settings: Annotated[config.Settings, Depends(get_settings)],
):
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.cognito_client_id,
        "client_secret": settings.cognito_client_secret,
        "code": code,
        "redirect_uri": settings.cognito_redirect_uri,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient() as client:
        TOKEN_URL = f"https://{settings.cognito_domain}/oauth2/token"
        response = await client.post(TOKEN_URL, data=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid code"
        )
    token = response.json()

    return RedirectResponse(url=f"/home?token={token['access_token']}")


@app.get("/logout")
async def logout(
    request: Request,
    settings: Annotated[config.Settings, Depends(get_settings)],
):
    token = request.query_params.get("token")
    LOGOUT_URL = f"https://{settings.cognito_domain}/logout"

    logout_uri = "http%3A%2F%2Flocalhost%3A8000"

    return RedirectResponse(
        url=f"{LOGOUT_URL}?client_id={settings.cognito_client_id}&logout_uri={logout_uri}&token={token}"
    )


@app.get("/home", response_class=HTMLResponse)
async def home_page(
    request: Request,
    settings: Annotated[config.Settings, Depends(get_settings)],
    username: str = Depends(get_current_user),
):
    token = request.query_params.get("token")
    context = {
        "request": request,
        "username": username,
        "logout_url": f"logout?token={token}",
    }
    return templates.TemplateResponse("home.html", context)
