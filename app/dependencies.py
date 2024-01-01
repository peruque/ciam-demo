import json
from fastapi import Depends, HTTPException, status, Cookie
from typing_extensions import Annotated
from app.config import AppSettings, get_app_settings, templates
import httpx
from jwt import PyJWKClient
import jwt
from app.models.user import UserInfo, AccessTokenPayload


async def get_verified_access_token_payload(
    settings: Annotated[AppSettings, Depends(get_app_settings)],
    access_token: Annotated[str | None, Cookie()],
) -> AccessTokenPayload:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Access Token is required"
        )

    try:
        access_payload = await verify_access_token(access_token, settings)
        return access_payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except Exception as exp:
        print(exp)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )


async def verify_access_token(token: str, settings: AppSettings) -> AccessTokenPayload:
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

    return AccessTokenPayload(
        token=token,
        sub=payload["sub"],
        groups=payload["cognito:groups"],
        username=payload["username"],
    )


async def get_current_user_info(
    settings: Annotated[AppSettings, Depends(get_app_settings)],
    access_payload: AccessTokenPayload = Depends(get_verified_access_token_payload),
) -> UserInfo:
    headers = {
        "Content-Type": "application/x-amz-json-1.1",
        "Authorization": f"Bearer {access_payload.token}",
    }
    async with httpx.AsyncClient() as client:
        TOKEN_URL = f"https://{settings.cognito_domain}/oauth2/userInfo"
        response = await client.get(TOKEN_URL, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid code"
        )
    user_info = response.json()

    return UserInfo(
        id=user_info["sub"],
        username=user_info["username"],
        first_name=user_info["given_name"],
        last_name=user_info["family_name"],
        email=user_info["email"],
        groups=access_payload.groups,
    )
