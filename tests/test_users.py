from http import HTTPStatus

from tests.factories import BookFactory


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


def test_get_current_user_info(client, user, token):
    response = client.get(
        '/users/me', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


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


def test_list_book_from_users_should_return_20_books(
    client, user, prepare_factories, token, session
):
    books = BookFactory.create_batch(21)

    user.books.extend(books)
    session.add(user)
    session.commit()

    expected_books = 20
    response = client.get(
        '/users/me/books', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['books']) == expected_books


def test_list_book_from_users_filter_pagination_should_return_10_books(
    client, user, prepare_factories, token, session
):
    books = BookFactory.create_batch(20)

    user.books.extend(books)
    session.add(user)
    session.commit()

    expected_books = 10
    response = client.get(
        '/users/me/books?limit=10&offset=5',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['books']) == expected_books


def test_list_book_from_users_filter_year_should_return_5_books(
    client, user, prepare_factories, token, session
):
    books_to_return = BookFactory.create_batch(5, year=1900)
    books_to_ignore = BookFactory.create_batch(2, year=2000)

    user.books.extend(books_to_ignore)
    user.books.extend(books_to_return)

    session.add(user)
    session.commit()

    expected_books = 5
    response = client.get(
        '/users/me/books?year=1900',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['books']) == expected_books


def test_list_book_from_users_filter_min_year_should_return_5_books(
    client, user, prepare_factories, token, session
):
    books_to_return = BookFactory.create_batch(5, year=1800)
    books_to_ignore = BookFactory.create_batch(2, year=1700)

    user.books.extend(books_to_ignore)
    user.books.extend(books_to_return)

    session.add(user)
    session.commit()

    expected_books = 5
    response = client.get(
        '/users/me/books?min_year=1800',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['books']) == expected_books


def test_list_book_from_users_filter_max_year_should_return_5_books(
    client, user, prepare_factories, token, session
):
    books_to_return = BookFactory.create_batch(5, year=1800)
    books_to_ignore = BookFactory.create_batch(2, year=2000)

    user.books.extend(books_to_ignore)
    user.books.extend(books_to_return)

    session.add(user)
    session.commit()

    expected_books = 5
    response = client.get(
        '/users/me/books?max_year=1900',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['books']) == expected_books


def test_list_book_from_users_filter_title_should_return_1_book(
    client, user, prepare_factories, token, session
):
    books_to_ignore = BookFactory.create_batch(5)
    book_to_return = BookFactory.create(title='best test title')

    user.books.extend(books_to_ignore)
    user.books.append(book_to_return)

    session.add(user)
    session.commit()

    expected_books = 1
    response = client.get(
        '/users/me/books?title=best test title',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['books']) == expected_books


def test_list_books_return_expected_fields(client, user_with_book, token):
    response = client.get(
        '/users/me/books', headers={'Authorization': f'Bearer {token}'}
    )

    book_from_user = user_with_book.books[0]

    assert response.json()['books'] == [
        {
            'id': book_from_user.id,
            'year': book_from_user.year,
            'title': book_from_user.title,
            'author_id': book_from_user.author_id,
        }
    ]
