import asyncio
import sys
from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from fast_madr.app import app
from fast_madr.database import get_session
from fast_madr.models import table_registry
from fast_madr.security import get_password_hash
from tests.factories import AuthorFactory, BookFactory, UserFactory

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:17-alpine', driver='psycopg') as postgres:
        yield create_async_engine(postgres.get_connection_url())


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def mock_session_with_error():
    class FakeSession:
        @staticmethod
        def execute():
            raise Exception('error with connection')

    def override():
        return FakeSession()

    app.dependency_overrides[get_session] = override

    yield

    app.dependency_overrides.clear()


@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 6, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session):
    password = 'test'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = 'test'

    return user


@pytest_asyncio.fixture
async def admin_user(session):
    password = 'test'
    admin_user = UserFactory(
        password=get_password_hash(password), is_admin=True
    )

    session.add(admin_user)
    await session.commit()
    await session.refresh(admin_user)

    admin_user.clean_password = 'test'

    return admin_user


@pytest_asyncio.fixture
async def inactive_user(session):
    password = 'test'
    inactive_user = UserFactory(
        password=get_password_hash(password), is_active=False
    )

    session.add(inactive_user)
    await session.commit()
    await session.refresh(inactive_user)

    inactive_user.clean_password = 'test'

    return inactive_user


@pytest_asyncio.fixture
async def other_user(session):
    password = 'test'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = 'test'

    return user


@pytest_asyncio.fixture
async def user_with_book(user, book_with_author, session):
    user.books.append(book_with_author)

    session.add(user)
    await session.commit()

    return user


@pytest_asyncio.fixture
async def author(session):
    author = AuthorFactory.build()
    session.add(author)
    await session.commit()
    await session.refresh(author)

    return author


@pytest_asyncio.fixture
async def book_with_author(session, author):
    book = BookFactory.build(author_id=author.id)
    session.add(book)
    await session.commit()
    await session.refresh(book)

    return book


async def create_book_batch(session, size: int = 1, **kwargs):
    books = []

    for _ in range(size):
        author = AuthorFactory.build()
        session.add(author)
        await session.flush()

        book = BookFactory.build(author_id=author.id, **kwargs)
        session.add(book)
        books.append(book)

    await session.commit()

    for book in books:
        await session.refresh(book)

    return books


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def token_admin(client, admin_user):
    response = client.post(
        '/auth/token',
        data={
            'username': admin_user.email,
            'password': admin_user.clean_password,
        },
    )

    return response.json()['access_token']
