from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_madr.database import get_session
from fast_madr.models import Author, User
from fast_madr.schemas import (
    AuthorPublic,
    AuthorSchema,
    AuthorUpdate,
    FilterAuthor,
    ListAuthors,
    Message,
)
from fast_madr.security import get_admin_user, get_current_user

router = APIRouter(prefix='/authors', tags=['authors'])
O_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(get_admin_user)]


@router.post('', response_model=AuthorPublic, status_code=HTTPStatus.CREATED)
async def create_author(
    author: AuthorSchema, current_user: CurrentUser, session: O_Session
):
    db_author = await session.scalar(
        select(Author).where(
            (Author.name == author.name)
            & (Author.birth_year == author.birth_year)
        )
    )

    if db_author:
        raise HTTPException(
            HTTPStatus.CONFLICT, detail='Author already exists in database'
        )

    db_author = Author(name=author.name, birth_year=author.birth_year)

    session.add(db_author)
    await session.commit()
    await session.refresh(db_author)

    return db_author


@router.delete(
    '/{author_id}', response_model=Message, status_code=HTTPStatus.OK
)
async def delete_author(
    author_id: int, admin_user: AdminUser, session: O_Session
):
    db_author = await session.scalar(
        select(Author).where(Author.id == author_id)
    )

    if not db_author:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='Author not found')

    await session.delete(db_author)
    await session.commit()

    return {'message': 'Author deleted successfully'}


@router.patch(
    '/{author_id}', response_model=AuthorPublic, status_code=HTTPStatus.OK
)
async def patch_author(
    author_id: int,
    author: AuthorUpdate,
    current_user: CurrentUser,
    session: O_Session,
):
    db_author = await session.scalar(
        select(Author).where(Author.id == author_id)
    )

    if not db_author:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail='Author not found')

    for key, value in author.model_dump(exclude_unset=True).items():
        setattr(db_author, key, value)

    session.add(db_author)
    await session.commit()
    await session.refresh(db_author)

    return db_author


@router.get('', response_model=ListAuthors, status_code=HTTPStatus.OK)
async def list_authors(
    author_filter: Annotated[FilterAuthor, Query()],
    current_user: CurrentUser,
    session: O_Session,
):
    query = select(Author)

    if author_filter.name:
        query = query.filter(Author.name.contains(author_filter.name))

    if author_filter.birth_year:
        query = query.filter(Author.birth_year == author_filter.birth_year)

    authors = await session.scalars(
        query.offset(author_filter.offset).limit(author_filter.limit)
    )

    return {'authors': authors.all()}


@router.get(
    '/{author_id}', response_model=AuthorPublic, status_code=HTTPStatus.OK
)
async def get_author_by_id(
    author_id: int, current_user: CurrentUser, session: O_Session
):
    db_author = await session.scalar(
        select(Author).where(Author.id == author_id)
    )

    if not db_author:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail=('Author not found'))

    return db_author
