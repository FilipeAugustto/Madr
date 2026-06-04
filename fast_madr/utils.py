import re
from datetime import datetime


def sanitize_text(text: str) -> str:
    if not text.strip():
        raise ValueError('Text cannot be empty')

    return re.sub(r'\s+', ' ', text).strip().lower()


def check_future_year(year: int) -> int:
    current_year = datetime.today().year
    if year > current_year:
        raise ValueError(f'The book year cannot be past {current_year}')

    return year
