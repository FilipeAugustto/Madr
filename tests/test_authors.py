from http import HTTPStatus

from tests.factories import AuthorFactory


def test_create_author(client, token):
    response = client.post(
        '/authors',
        json={'name': 'testname', 'birth_year': 1900},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'id': 1, 'name': 'testname', 'birth_year': 1900}


def test_create_author_should_return_409(client, author, token):
    response = client.post(
        '/authors',
        json={'name': author.name, 'birth_year': author.birth_year},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Author already exists in database'}


def test_create_author_with_impossible_year(client, token):
    response = client.post(
        '/authors',
        json={'name': 'testname', 'birth_year': 3000},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    errors = response.json()['detail']
    assert errors[0]['loc'] == ['body', 'birth_year']
    assert 'The book year cannot be past' in errors[0]['msg']


def test_create_author_with_blank_name(client, token):
    response = client.post(
        '/authors',
        json={'name': ' ', 'birth_year': 1900},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    errors = response.json()['detail']
    assert errors[0]['loc'] == ['body', 'name']
    assert 'Text cannot be empty' in errors[0]['msg']


def test_delete_author(client, author, token_admin):
    response = client.delete(
        f'/authors/{author.id}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Author deleted successfully'}


def test_delete_author_with_common_user(client, author, token):
    response = client.delete(
        f'/authors/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Action restricted to administrators'}


def test_delete_author_should_return_404(client, author, token_admin):
    response = client.delete(
        f'/authors/{author.id + 1}',
        headers={'Authorization': f'Bearer {token_admin}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author not found'}


def test_patch_author(client, author, token):
    response = client.patch(
        f'/authors/{author.id}',
        json={'name': 'new name', 'birth_year': 1901},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': author.id,
        'name': 'new name',
        'birth_year': 1901,
    }


def test_patch_author_should_return_404(client, author, token):
    response = client.patch(
        f'/authors/{author.id + 1}',
        json={'name': 'new name', 'birth_year': 1901},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author not found'}


def test_list_authors_should_return_20_authors(
    client, prepare_factories, token
):
    AuthorFactory.create_batch(20)
    expected_authors = 20
    response = client.get(
        '/authors', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['authors']) == expected_authors


def test_list_authors_filter_pagination_should_return_5_authors(
    client, prepare_factories, token
):
    AuthorFactory.create_batch(20)
    expected_authors = 5
    response = client.get(
        '/authors?limit=5&offset=3',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['authors']) == expected_authors


def test_list_authors_filter_name_should_return_2_authors(
    client, prepare_factories, token
):
    AuthorFactory.create_batch(3)
    AuthorFactory.create_batch(2, name='test name')
    expected_authors = 2
    response = client.get(
        '/authors?name=test name', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['authors']) == expected_authors


def test_list_authors_filter_birth_year_should_return_5_authors(
    client, prepare_factories, token
):
    AuthorFactory.create_batch(5, birth_year=1900)
    expected_authors = 5
    response = client.get(
        '/authors?birth_year=1900',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['authors']) == expected_authors


def test_list_authors_should_return_correct_fields(client, author, token):
    response = client.get(
        '/authors', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json()['authors'] == [
        {'id': author.id, 'name': author.name, 'birth_year': author.birth_year}
    ]
