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


def test_add_book_to_user(client, book_with_author, token):
    response = client.post(
        f'/users/me/books/{book_with_author.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book_with_author.id,
        'year': book_with_author.year,
        'title': book_with_author.title,
        'author_id': book_with_author.author_id,
    }


def test_add_book_to_user_should_return_404(client, book_with_author, token):
    response = client.post(
        f'/users/me/books/{book_with_author.id + 1}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found'}


def test_add_book_to_user_should_return_409(client, book_with_author, token):
    client.post(
        f'/users/me/books/{book_with_author.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    response = client.post(
        f'/users/me/books/{book_with_author.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User already has this book saved'}


def test_remove_book_from_user(client, user_with_book, token):
    response = client.delete(
        f'/users/me/books/{user_with_book.books[0].id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Book successfully removed from user collection'
    }


def test_remove_book_from_user_should_return_404(
    client, user_with_book, token
):
    response = client.delete(
        '/users/me/books/300', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User does not have this book saved'}
