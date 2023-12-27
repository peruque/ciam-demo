from functools import lru_cache
import json
from fastapi import FastAPI, Depends, Request, HTTPException, status, Cookie
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
import urllib.parse
from pydantic import BaseModel

app = FastAPI()

app.mount(
    "/static", StaticFiles(directory=Path.cwd() / "app" / "static"), name="static"
)

templates = Jinja2Templates(directory=Path.cwd() / "app" / "templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@lru_cache
def get_settings():
    return config.Settings()


class UserInfo(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
    email: str


async def get_verified_access_token(
    settings: Annotated[config.Settings, Depends(get_settings)],
    access_token: Annotated[str | None, Cookie()],
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Access Token is required"
        )

    try:
        verify_access_token(access_token, settings)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except Exception as exp:
        print(exp)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )

    return access_token


def verify_access_token(token: str, settings: config.Settings) -> str:
    JWKS_URL = f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/{settings.cognito_user_pool_id}/.well-known/jwks.json"
    client = PyJWKClient(JWKS_URL)
    header = jwt.get_unverified_header(token)
    key = client.get_signing_key(header["kid"])
    public_key = key.key
    payload = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=["RS256"],
        options={"verify_signature": True},
    )
    return payload["sub"]


async def get_current_user_info(
    settings: Annotated[config.Settings, Depends(get_settings)],
    access_token: str = Depends(get_verified_access_token),
) -> UserInfo:
    headers = {
        "Content-Type": "application/x-amz-json-1.1",
        "Authorization": f"Bearer {access_token}",
    }
    async with httpx.AsyncClient() as client:
        TOKEN_URL = f"https://{settings.cognito_domain}/oauth2/userInfo"
        response = await client.get(TOKEN_URL, headers=headers)

    if response.status_code != 200:
        print("GOT HERE", response.json())
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid code"
        )
    user_info = response.json()

    print("new id_token", json.dumps(user_info, indent=2))

    return UserInfo(
        id=user_info["sub"],
        username=user_info["username"],
        first_name=user_info["given_name"],
        last_name=user_info["family_name"],
        email=user_info["email"],
    )


async def get_id_token(access_token: str, settings: config.Settings) -> str:
    headers = {
        "Content-Type": "application/x-amz-json-1.1",
        "Authorization": f"Bearer {access_token}",
    }
    async with httpx.AsyncClient() as client:
        TOKEN_URL = f"https://{settings.cognito_domain}/oauth2/userInfo"
        response = await client.get(TOKEN_URL, headers=headers)

    if response.status_code != 200:
        print("GOT HERE", response.json())
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid code"
        )
    token = response.json()

    print("new id_token", json.dumps(token, indent=2))

    return ""


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
        "scope": "openid",
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

    response = RedirectResponse(url="/home")

    # Set token cookies as httponly prevents client-side scripts from accessing
    # the cookie. This adds an extra layer of security by reducing the risk of
    # XSS attacks.
    response.set_cookie("access_token", token["access_token"], httponly=True)
    response.set_cookie("refresh_token", token["refresh_token"], httponly=True)

    return response


@app.get("/logout")
async def logout(
    request: Request,
    settings: Annotated[config.Settings, Depends(get_settings)],
):
    token = request.query_params.get("token")
    LOGOUT_URL = f"https://{settings.cognito_domain}/logout"

    redirect_uri = urllib.parse.quote(settings.cognito_logout_redirect_uri, safe="")

    response = RedirectResponse(
        url=f"{LOGOUT_URL}?client_id={settings.cognito_client_id}&logout_uri={redirect_uri}&token={token}"
    )

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return response


@app.get("/home", response_class=HTMLResponse)
async def home_page(
    request: Request,
    user: UserInfo = Depends(get_current_user_info),
):
    context = {
        "request": request,
        "user": user,
    }
    return templates.TemplateResponse("home.html", context)


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    user: UserInfo = Depends(get_current_user_info),
):
    context = {
        "request": request,
        "user": user,
    }
    return templates.TemplateResponse("profile.html", context)
