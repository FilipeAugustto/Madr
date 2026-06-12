import pytest

from fast_madr.utils import check_future_year, sanitize_text


def test_sanitize_text():
    title_request = 'MEga   MeSS title '

    expected_title = 'mega mess title'
    response = sanitize_text(title_request)

    assert response == expected_title


def test_sanitize_text_with_blank_text():

    with pytest.raises(ValueError, match='Text cannot be empty'):
        sanitize_text('  ')


def test_check_future_year():

    with pytest.raises(ValueError, match='The book year cannot be past'):
        check_future_year(3000)
