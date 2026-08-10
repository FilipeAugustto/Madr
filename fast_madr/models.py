from datetime import datetime

from sqlalchemy import Column, ForeignKey, Table, func
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    registry,
    relationship,
)

table_registry = registry()
user_book_association = Table(
    'user_book',
    table_registry.metadata,
    Column(
        'user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True
    ),
    Column(
        'book_id', ForeignKey('books.id', ondelete='CASCADE'), primary_key=True
    ),
)


@mapped_as_dataclass(table_registry)
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    books: Mapped[list['Book']] = relationship(
        secondary=user_book_association,
        init=False,
        back_populates='users',
        passive_deletes=True,
        lazy='selectin',
    )


@mapped_as_dataclass(table_registry)
class Book:
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    year: Mapped[int]
    title: Mapped[str] = mapped_column(unique=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'))
    author: Mapped['Author'] = relationship(
        init=False, back_populates='books', lazy='selectin'
    )
    users: Mapped[list[User]] = relationship(
        secondary=user_book_association,
        init=False,
        back_populates='books',
        passive_deletes=True,
        lazy='selectin',
    )


@mapped_as_dataclass(table_registry)
class Author:
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    birth_year: Mapped[int]
    books: Mapped[list['Book']] = relationship(
        init=False,
        back_populates='author',
        cascade='all, delete-orphan',
        lazy='selectin',
    )
