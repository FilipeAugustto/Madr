from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_madr.database import get_session
from fast_madr.models import User
from fast_madr.schemas import Message, UserPublic, UserSchema
from fast_madr.security import get_password_hash

router = APIRouter(prefix='/users', tags=['users'])
a_session = Annotated[Session, Depends(get_session)]


@router.post('/', response_model=UserPublic, status_code=HTTPStatus.CREATED)
def create_user(user: UserSchema, session: a_session):
    db_user = session.scalar(select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        raise HTTPException(
            HTTPStatus.CONFLICT,
            detail=('Username or email already exists!')
        )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password)
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get('/{user_id}', response_model=UserPublic, status_code=HTTPStatus.OK)
def get_user(user_id: int):
    ...


@router.put('/{user_id}', response_model=UserPublic, status_code=HTTPStatus.OK)
def update_user(user_id: int):
    ...


@router.delete('/{user_id}', response_model=Message, status_code=HTTPStatus.OK)
def delete_user(user_id: int):
    ...
