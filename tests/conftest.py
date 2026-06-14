from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from fast_madr.app import app
from fast_madr.database import get_session
from fast_madr.models import table_registry
from fast_madr.security import get_password_hash
from tests.factories import AuthorFactory, BookFactory, UserFactory


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
        _engine = create_engine(postgres.get_connection_url())

        with _engine.begin():
            yield _engine


@pytest.fixture
def session(engine):
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
        session.rollback()

    table_registry.metadata.drop_all(engine)


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


@pytest.fixture
def user(session):
    password = 'test'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = 'test'

    return user


@pytest.fixture
def admin_user(session):
    password = 'test'
    admin_user = UserFactory(
        password=get_password_hash(password), is_admin=True
    )

    session.add(admin_user)
    session.commit()
    session.refresh(admin_user)

    admin_user.clean_password = 'test'

    return admin_user


@pytest.fixture
def inactive_user(session):
    password = 'test'
    inactive_user = UserFactory(
        password=get_password_hash(password), is_active=False
    )

    session.add(inactive_user)
    session.commit()
    session.refresh(inactive_user)

    inactive_user.clean_password = 'test'

    return inactive_user


@pytest.fixture
def other_user(session):
    password = 'test'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = 'test'

    return user


@pytest.fixture
def user_with_book(user, book_with_author, session):
    user.books.append(book_with_author)

    session.add(user)
    session.commit()

    return user


@pytest.fixture
def author(session):
    AuthorFactory._meta.sqlalchemy_session = session

    author = AuthorFactory()
    session.refresh(author)

    return author


@pytest.fixture
def book_with_author(session):
    AuthorFactory._meta.sqlalchemy_session = session
    BookFactory._meta.sqlalchemy_session = session

    book = BookFactory()
    session.refresh(book)

    return book


@pytest.fixture
def prepare_factories(session):
    AuthorFactory._meta.sqlalchemy_session = session
    BookFactory._meta.sqlalchemy_session = session


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
