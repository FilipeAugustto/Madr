from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_madr.database import get_session
from fast_madr.models import User
from fast_madr.schemas import TokenData
from fast_madr.settings import get_settings

settings = get_settings()
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='auth/token', refreshUrl='/auth/refresh-token'
)


def get_password_hash(plain_password: str):
    return password_hash.hash(plain_password)


def verify_password_hash(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject_email = payload.get('sub')
        if subject_email is None:
            raise credentials_exception

        token_data = TokenData(username=subject_email)

    except InvalidTokenError:
        raise credentials_exception

    user = await session.scalar(
        select(User).where(
            (User.email == token_data.username) & (User.is_active)
        )
    )

    if not user:
        raise credentials_exception

    return user


def get_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_admin:
        raise HTTPException(
            HTTPStatus.FORBIDDEN, detail='Action restricted to administrators'
        )

    return current_user
