from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fast_madr.database import get_session
from fast_madr.models import Book, User
from fast_madr.schemas import (
    BookPublic,
    FilterBook,
    ListBooks,
    Message,
    UserPublic,
    UserSchema,
)
from fast_madr.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])
O_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('', response_model=UserPublic, status_code=HTTPStatus.CREATED)
async def create_user(user: UserSchema, session: O_Session):
    db_user = await session.scalar(
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
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.put('/{user_id}', response_model=UserPublic, status_code=HTTPStatus.OK)
async def update_user(
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
        await session.commit()

    except IntegrityError:
        raise HTTPException(
            HTTPStatus.CONFLICT, detail='Username or email already exists'
        )

    return current_user


@router.delete('/{user_id}', response_model=Message, status_code=HTTPStatus.OK)
async def delete_user(
    user_id: int, current_user: CurrentUser, session: O_Session
):
    if user_id != current_user.id:
        raise HTTPException(HTTPStatus.FORBIDDEN, detail='Unauthorized user')

    user = await session.scalar(select(User).where(User.id == current_user.id))

    user.is_active = False

    session.add(user)
    await session.commit()

    return {'message': 'User deleted successfully'}


@router.get('/me', response_model=UserPublic, status_code=HTTPStatus.OK)
async def get_current_user_info(current_user: CurrentUser):

    return current_user


@router.post(
    '/me/books/{book_id}', response_model=BookPublic, status_code=HTTPStatus.OK
)
async def add_book_to_user(
    book_id: int, current_user: CurrentUser, session: O_Session
):
    db_book = await session.scalar(select(Book).where(Book.id == book_id))

    if not db_book:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='Book not found')

    if db_book in current_user.books:
        raise HTTPException(
            HTTPStatus.CONFLICT, detail='User already has this book saved'
        )

    current_user.books.append(db_book)

    session.add(current_user)
    await session.commit()

    return db_book


@router.delete(
    '/me/books/{book_id}', response_model=Message, status_code=HTTPStatus.OK
)
async def remove_book_from_user(
    book_id: int, current_user: CurrentUser, session: O_Session
):
    user_saved_book = await session.scalar(
        select(Book)
        .join(Book.users)
        .where((User.id == current_user.id) & (Book.id == book_id))
    )

    if not user_saved_book:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, detail='User does not have this book saved'
        )

    current_user.books.remove(user_saved_book)
    await session.commit()

    return {'message': 'Book successfully removed from user collection'}


@router.get('/me/books', response_model=ListBooks, status_code=HTTPStatus.OK)
async def list_books_from_user(
    book_filter: Annotated[FilterBook, Query()],
    current_user: CurrentUser,
    session: O_Session,
):
    query = select(Book).join(Book.users).where(User.id == current_user.id)

    if book_filter.year:
        query = query.filter(Book.year == book_filter.year)

    if book_filter.min_year:
        query = query.filter(Book.year >= book_filter.min_year)

    if book_filter.max_year:
        query = query.filter(Book.year <= book_filter.max_year)

    if book_filter.title:
        query = query.filter(Book.title.contains(book_filter.title))

    books_from_user = await session.scalars(
        query.offset(book_filter.offset).limit(book_filter.limit)
    )

    return {'books': books_from_user.all()}
