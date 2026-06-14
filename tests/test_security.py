from http import HTTPStatus

from jwt import decode

from fast_madr.security import create_access_token
from fast_madr.settings import get_settings

settings = get_settings()


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded['test'] == 'test'
    assert 'exp' in decoded


def test_wrong_token(client):
    response = client.put(
        '/users/1', headers={'Authorization': 'Bearer wrong_token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_not_found(client):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.put(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_dont_exists(client):
    data = {'sub': 'test@example.com'}
    token = create_access_token(data)

    response = client.put(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_admin_user(client, token_admin, book_with_author):
    response = client.delete(
        f'/books/{book_with_author.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Book deleted successfully'}


def test_get_admin_user_with_common_user(client, token, book_with_author):
    response = client.delete(
        f'/books/{book_with_author.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Action restricted to administrators'}
