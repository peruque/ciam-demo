from fastapi import Depends, Request, HTTPException, status, Cookie
from typing_extensions import Annotated
from app.config import AppSettings, get_app_settings, templates
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx
import urllib.parse
from app.models.user import UserInfo
from app.dependencies import get_current_user_info
from fastapi import APIRouter

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def user_login_page(
    request: Request,
    settings: Annotated[AppSettings, Depends(get_app_settings)],
):
    context = {
        "request": request,
        "auth_url": f"https://{settings.cognito_domain}/oauth2/authorize",
        "client_id": settings.cognito_client_id,
        "redirect_uri": settings.cognito_redirect_uri,
        "scope": "openid",
    }
    return templates.TemplateResponse("login.html", context)


@router.get("/callback")
async def callback(
    code: str,
    settings: Annotated[AppSettings, Depends(get_app_settings)],
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


@router.get("/home", response_class=HTMLResponse)
async def home_page(
    request: Request,
    user: UserInfo = Depends(get_current_user_info),
):
    context = {
        "request": request,
        "user": user,
    }
    return templates.TemplateResponse("home.html", context)


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    user: UserInfo = Depends(get_current_user_info),
):
    context = {
        "request": request,
        "user": user,
    }
    return templates.TemplateResponse("profile.html", context)


@router.get("/logout")
async def logout(
    request: Request,
    settings: Annotated[AppSettings, Depends(get_app_settings)],
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
