from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_madr.database import get_session
from fast_madr.models import User
from fast_madr.schemas import Token
from fast_madr.security import (
    create_access_token,
    get_current_user,
    verify_password_hash,
)

router = APIRouter(prefix='/auth', tags=['auth'])

Formdata = Annotated[OAuth2PasswordRequestForm, Depends()]
O_Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/token', response_model=Token, status_code=HTTPStatus.OK)
def login_for_access_token(session: O_Session, form_data: Formdata):
    user = session.scalar(select(User).where(
            (User.email == form_data.username) & (User.is_active)
        )
    )

    if not user or not verify_password_hash(form_data.password, user.password):
        raise HTTPException(
            HTTPStatus.BAD_REQUEST, detail='Incorrect email or password!'
        )

    data = {'sub': user.email}
    access_token = create_access_token(data)

    return Token(access_token=access_token, token_type='Bearer')


@router.post('/token-refresh', response_model=Token, status_code=HTTPStatus.OK)
def refresh_token(current_user: CurrentUser):
    new_access_token = create_access_token({'sub': current_user.email})

    return Token(access_token=new_access_token, token_type='Bearer')
