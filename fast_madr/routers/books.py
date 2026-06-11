from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_madr.database import get_session
from fast_madr.models import Book, User
from fast_madr.schemas import (
    BookPublic,
    BookSchema,
    BookUpdate,
    FilterBook,
    ListBooks,
    Message,
)
from fast_madr.security import get_admin_user, get_current_user

router = APIRouter(prefix='/books', tags=['books'])
CurrentUser = Annotated[User, Depends(get_current_user)]
O_Session = Annotated[Session, Depends(get_session)]
AdminUser = Annotated[User, Depends(get_admin_user)]


@router.post('', status_code=HTTPStatus.CREATED, response_model=BookPublic)
def create_book(
    book: BookSchema, current_user: CurrentUser, session: O_Session
):
    db_book = session.scalar(select(Book).where(Book.title == book.title))
    if db_book:
        raise HTTPException(
            HTTPStatus.CONFLICT, detail='Book already exists in the database'
        )

    try:
        db_book = Book(
            year=book.year, title=book.title, author_id=book.author_id
        )

        session.add(db_book)
        session.commit()
        session.refresh(db_book)

    except IntegrityError:
        raise HTTPException(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Author does not exists in the database',
        )

    return db_book


@router.delete('/{book_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_book(book_id: int, admin_user: AdminUser, session: O_Session):
    db_book = session.scalar(select(Book).where(Book.id == book_id))

    if not db_book:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='Book not found')

    session.delete(db_book)
    session.commit()

    return {'message': 'Book deleted'}


@router.patch(
    '/{book_id}', status_code=HTTPStatus.OK, response_model=BookPublic
)
def patch_book(
    book_id: int, book: BookUpdate, admin_user: AdminUser, session: O_Session
):
    db_book = session.scalar(select(Book).where(Book.id == book_id))

    if not db_book:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='Book not found')

    for key, value in book.model_dump(exclude_unset=True).items():
        setattr(db_book, key, value)

    session.add(db_book)
    session.commit()
    session.refresh(db_book)

    return db_book


@router.get('', status_code=HTTPStatus.OK, response_model=ListBooks)
def list_books(
    book_filter: Annotated[FilterBook, Query()],
    current_user: CurrentUser,
    session: O_Session,
):
    query = select(Book)

    if book_filter.title:
        query.filter(Book.year >= book_filter.year)

    if book_filter.title:
        query.filter(Book.title.contains(book_filter.title))

    books = session.scalars(query.limit(book_filter.limit))

    return books
