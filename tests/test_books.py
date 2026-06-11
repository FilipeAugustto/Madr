from http import HTTPStatus


def test_create_book(client, author, token):
    book_request = {
        'year': 1990,
        'title': 'testbook',
        'author_id': author.id
    }

    response = client.post(
        '/books',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'year': 1990,
        'title': 'testbook',
        'author_id': author.id
    }


def test_create_book_should_return_409(client, book_with_author, token):
    book_request = {
        'year': 1990,
        'title': book_with_author.title,
        'author_id': book_with_author.author_id
    }

    response = client.post(
        '/books',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Book already exists in the database'}


def test_create_book_with_inexistent_author(client, token):
    book_request = {
        'year': 1990,
        'title': 'testbook',
        'author_id': 1
    }

    response = client.post(
        '/books',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': 'Author does not exists in the database'
    }


def test_create_book_with_impossible_year(client, author, token):
    book_request = {
        'year': 3000,
        'title': 'testbook',
        'author_id': author.id
    }

    response = client.post(
        '/books',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    errors = response.json()['detail']
    assert errors[0]['loc'] == ['body', 'year']
    assert 'The book year cannot be past' in errors[0]['msg']


def test_create_book_with_blank_title(client, author, token):
    book_request = {
        'year': 1990,
        'title': ' ',
        'author_id': author.id
    }

    response = client.post(
        '/books',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    errors = response.json()['detail']
    assert errors[0]['loc'] == ['body', 'title']
    assert 'Text cannot be empty' in errors[0]['msg']
