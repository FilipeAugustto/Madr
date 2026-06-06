from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_madr.database import get_session
from fast_madr.models import User
from fast_madr.schemas import Message, UserPublic, UserSchema
from fast_madr.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])
O_Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('', response_model=UserPublic, status_code=HTTPStatus.CREATED)
def create_user(user: UserSchema, session: O_Session):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        raise HTTPException(
            HTTPStatus.CONFLICT, detail='Username or email already exists'
        )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.put('/{user_id}', response_model=UserPublic, status_code=HTTPStatus.OK)
def update_user(
    user_id: int,
    user: UserSchema,
    current_user: CurrentUser,
    session: O_Session,
):
    if user_id != current_user.id:
        raise HTTPException(HTTPStatus.FORBIDDEN, detail='Unauthorized user')

    current_user.username = user.username
    current_user.email = user.email
    current_user.password = get_password_hash(user.password)

    try:
        session.add(current_user)
        session.commit()

    except IntegrityError:
        raise HTTPException(
            HTTPStatus.CONFLICT, detail='Username or email already exists'
        )

    return current_user


@router.delete('/{user_id}', response_model=Message, status_code=HTTPStatus.OK)
def delete_user(user_id: int, current_user: CurrentUser, session: O_Session):
    if user_id != current_user.id:
        raise HTTPException(HTTPStatus.FORBIDDEN, detail='Unauthorized user')

    user = session.scalar(select(User).where(User.id == current_user.id))

    user.is_active = False

    session.add(user)
    session.commit()

    return {'message': 'User deleted successfully'}
