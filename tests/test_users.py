from http import HTTPStatus


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'usertest',
            'email': 'usertest@example.com',
            'password': 'test',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'usertest',
        'email': 'usertest@example.com',
    }


def test_create_user_should_return_409(client, user):
    user_schema = {
        'username': user.username,
        'email': user.email,
        'password': user.clean_password,
    }
    response = client.post('/users', json=user_schema)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_update_user(client, user, token):
    user_request = {
        'username': 'usertest200',
        'email': user.email,
        'password': user.clean_password,
    }
    response = client.put(
        f'/users/{user.id}',
        json=user_request,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': user_request['username'],
        'email': user_request['email'],
    }


def test_update_user_should_return_403(client, user, token):
    user_request = {
        'username': 'usertest200',
        'email': user.email,
        'password': user.clean_password,
    }
    response = client.put(
        f'/users/{user.id + 1}',
        json=user_request,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Unauthorized user'}


def test_update_user_should_return_409(client, user, other_user, token):
    user_request = {
        'username': other_user.username,
        'email': other_user.email,
        'password': user.clean_password,
    }
    response = client.put(
        f'/users/{user.id}',
        json=user_request,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_delete_user_should_return_403(client, user, token):
    response = client.delete(
        f'/users/{user.id + 1}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Unauthorized user'}
