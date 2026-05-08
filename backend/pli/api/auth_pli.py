"""Routes /auth/* pour l'authentification PLI (Cloud).

(Distinct de `auth.py` qui gère l'OAuth des providers Gmail/Microsoft.)
"""

from __future__ import annotations

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, Field

from ..auth.login import (
    EmailNotVerified,
    InvalidCredentials,
    LoginResult,
    rotate_refresh,
)
from ..auth.login import (
    login as do_login,
)
from ..auth.login import (
    logout as do_logout,
)
from ..auth.password_reset import confirm_reset, request_reset
from ..auth.passwords import PasswordPolicyError
from ..auth.signup import EmailAlreadyExists, create_user
from ..auth.tokens import consume_verification_token

router = APIRouter()

REFRESH_COOKIE = "pli_refresh"
COOKIE_KW = {"httponly": True, "samesite": "lax", "secure": True, "path": "/auth"}


# ------------ Schemas ------------


class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=200)
    accept_terms: bool


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class VerifyIn(BaseModel):
    token: str


class ResetRequestIn(BaseModel):
    email: EmailStr


class ResetConfirmIn(BaseModel):
    token: str
    new_password: str = Field(min_length=12, max_length=200)


class LoginOut(BaseModel):
    access_token: str
    user_id: str
    email: str
    plan: str


# ------------ Helpers ------------


def _set_refresh_cookie(response: Response, refresh: str) -> None:
    response.set_cookie(REFRESH_COOKIE, refresh, max_age=30 * 24 * 3600, **COOKIE_KW)


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE, path="/auth")


def _login_response(response: Response, r: LoginResult) -> LoginOut:
    _set_refresh_cookie(response, r.refresh_token)
    return LoginOut(
        access_token=r.access_token,
        user_id=r.user_id,
        email=r.email,
        plan=r.plan,
    )


# ------------ Routes ------------


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(body: SignupIn) -> dict:
    if not body.accept_terms:
        raise HTTPException(400, "terms_not_accepted")
    try:
        user = await create_user(str(body.email), body.password)
    except EmailAlreadyExists:
        raise HTTPException(409, "email_already_exists")
    except PasswordPolicyError as e:
        raise HTTPException(422, str(e))
    return {"user_id": user.id, "email": user.email, "verification_sent": True}


@router.post("/verify")
async def verify(body: VerifyIn) -> dict:
    user_id = await consume_verification_token(body.token)
    if not user_id:
        raise HTTPException(400, "invalid_or_expired_token")
    return {"verified": True, "user_id": user_id}


@router.post("/login")
async def login(body: LoginIn, request: Request, response: Response) -> LoginOut:
    ua = request.headers.get("user-agent")
    ip = request.client.host if request.client else None
    try:
        r = await do_login(str(body.email), body.password, user_agent=ua, ip=ip)
    except InvalidCredentials:
        raise HTTPException(401, "invalid_credentials")
    except EmailNotVerified:
        raise HTTPException(403, "email_not_verified")
    return _login_response(response, r)


@router.post("/refresh")
async def refresh(response: Response, pli_refresh: str | None = Cookie(default=None)) -> LoginOut:
    if not pli_refresh:
        raise HTTPException(401, "no_refresh_cookie")
    try:
        r = await rotate_refresh(pli_refresh)
    except InvalidCredentials:
        _clear_refresh_cookie(response)
        raise HTTPException(401, "invalid_or_reused_refresh")
    return _login_response(response, r)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    pli_refresh: str | None = Cookie(default=None),
) -> dict:
    if pli_refresh:
        access_jti = None
        access_exp = None
        principal = getattr(request.state, "principal", None)
        if principal:
            # on pourrait extraire jti/exp du header Authorization si besoin
            pass
        await do_logout(pli_refresh)
    _clear_refresh_cookie(response)
    return {"logged_out": True}


@router.post("/password-reset/request")
async def password_reset_request(body: ResetRequestIn) -> dict:
    await request_reset(str(body.email))
    return {"sent": True}  # réponse identique même si email inconnu


@router.post("/password-reset/confirm")
async def password_reset_confirm(body: ResetConfirmIn) -> dict:
    try:
        ok = await confirm_reset(body.token, body.new_password)
    except PasswordPolicyError as e:
        raise HTTPException(422, str(e))
    if not ok:
        raise HTTPException(400, "invalid_or_expired_token")
    return {"reset": True}
