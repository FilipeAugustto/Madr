from http import HTTPStatus

from tests.factories import BookFactory


def test_create_book(client, author, token):
    book_request = {'year': 1990, 'title': 'testbook', 'author_id': author.id}

    response = client.post(
        '/books',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'year': 1990,
        'title': 'testbook',
        'author_id': author.id,
    }


def test_create_book_should_return_409(client, book_with_author, token):
    book_request = {
        'year': 1990,
        'title': book_with_author.title,
        'author_id': book_with_author.author_id,
    }

    response = client.post(
        '/books',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Book already exists in the database'}


def test_create_book_with_inexistent_author(client, token):
    book_request = {'year': 1990, 'title': 'testbook', 'author_id': 1}

    response = client.post(
        '/books',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': 'Author does not exists in the database'
    }


def test_create_book_with_impossible_year(client, author, token):
    book_request = {'year': 3000, 'title': 'testbook', 'author_id': author.id}

    response = client.post(
        '/books',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    errors = response.json()['detail']
    assert errors[0]['loc'] == ['body', 'year']
    assert 'The book year cannot be past' in errors[0]['msg']


def test_create_book_with_blank_title(client, author, token):
    book_request = {'year': 1990, 'title': ' ', 'author_id': author.id}

    response = client.post(
        '/books',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    errors = response.json()['detail']
    assert errors[0]['loc'] == ['body', 'title']
    assert 'Text cannot be empty' in errors[0]['msg']


def test_delete_book(client, book_with_author, token_admin):
    response = client.delete(
        f'/books/{book_with_author.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Book deleted successfully'}


def test_delete_book_should_return_404(client, token_admin):
    response = client.delete(
        '/books/1', headers={'Authorization': f'Bearer {token_admin}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found'}


def test_delete_book_with_common_user(client, book_with_author, token):
    response = client.delete(
        f'/books/{book_with_author.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Action restricted to administrators'}


def test_patch_book(client, book_with_author, token):
    book_request = {
        'year': 2000,
        'title': 'new title',
        'author_id': book_with_author.author_id,
    }
    response = client.patch(
        f'/books/{book_with_author.id}',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book_with_author.id,
        'year': book_request['year'],
        'title': book_request['title'],
        'author_id': book_request['author_id'],
    }


def test_patch_book_should_return_404(client, author, token):
    book_request = {'year': 2000, 'title': 'new title', 'author_id': author.id}
    response = client.patch(
        '/books/1',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book not found'}


def test_patch_book_with_inexistent_author(client, book_with_author, token):
    book_request = {'year': 2000, 'title': 'new title', 'author_id': 300}
    response = client.patch(
        f'/books/{book_with_author.id}',
        json=book_request,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': 'Author does not exists in the database'
    }


def test_list_books_should_return_20_books(client, token):
    BookFactory.create_batch(20)
    expected_books = 20
    response = client.get(
        '/books', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['books']) == expected_books


def test_list_books_filter_pagination_should_return_5_books(
    client, token, prepare_factories
):
    BookFactory.create_batch(20)
    expected_books = 5
    response = client.get(
        '/books?limit=5&offset=10',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['books']) == expected_books


def test_list_books_filter_year_should_return_5_books(
    client, token, prepare_factories
):
    BookFactory.create_batch(5, year=1900)
    expected_books = 5
    response = client.get(
        '/books?year=1900', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['books']) == expected_books


def test_list_books_filter_min_year_should_return_5_books(
    client, token, prepare_factories
):
    BookFactory.create_batch(5, year=1900)
    expected_books = 5
    response = client.get(
        '/books?min_year=1800', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['books']) == expected_books


def test_list_books_filter_max_year_should_return_5_books(
    client, token, prepare_factories
):
    BookFactory.create_batch(5, year=1900)
    expected_books = 5
    response = client.get(
        '/books?max_year=2026', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['books']) == expected_books


def test_list_books_filter_title_should_return_1_book(
    client, token, prepare_factories
):
    BookFactory.create_batch(5)
    BookFactory.create(title='mega test title')
    expected_books = 1
    response = client.get(
        '/books?title=test', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['books']) == expected_books


def test_list_books_return_expected_fields(client, book_with_author, token):
    response = client.get(
        '/books', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json()['books'] == [
        {
            'id': book_with_author.id,
            'year': book_with_author.year,
            'title': book_with_author.title,
            'author_id': book_with_author.author_id,
        }
    ]
