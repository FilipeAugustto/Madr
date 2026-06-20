from http import HTTPStatus

from fast_madr.app import app


def test_health_check(client):
    response = client.get('/health')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'status': 'online', 'database': 'connected'}


def test_health_check_should_return_503(client, mock_session_with_error):
    response = client.get('/health')

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json() == {'detail': 'Database connection not established'}

    app.dependency_overrides.clear()
