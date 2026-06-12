from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr, Field

from fast_madr.models import Author
from fast_madr.utils import check_future_year, sanitize_text


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class BookSchema(BaseModel):
    year: Annotated[int, Field(ge=0), AfterValidator(check_future_year)]
    title: Annotated[str, AfterValidator(sanitize_text)]
    author_id: int


class BookPublic(BookSchema):
    id: int


class BookUpdate(BaseModel):
    year: (
        Annotated[int, Field(ge=0), AfterValidator(check_future_year)] | None
    ) = None
    title: Annotated[str, AfterValidator(sanitize_text)] | None = None
    author_id: int | None = None


class FilterPage(BaseModel):
    limit: int = Field(ge=1, default=20)
    offset: int = Field(ge=0, default=0)


class FilterBook(FilterPage):
    year: (
        Annotated[int, Field(ge=0), AfterValidator(check_future_year)] | None
    ) = None
    min_year: (
        Annotated[int, Field(ge=0), AfterValidator(check_future_year)] | None
    ) = None
    max_year: (
        Annotated[int, Field(ge=0), AfterValidator(check_future_year)] | None
    ) = None
    title: (
        Annotated[str, Field(min_length=3), AfterValidator(sanitize_text)]
        | None
    ) = None


class ListBooks(BaseModel):
    books: list[BookPublic] = []


class AuthorSchema(BaseModel):
    name: Annotated[str, AfterValidator(sanitize_text)]
    birth_year: Annotated[int, Field(ge=0), AfterValidator(check_future_year)]


class AuthorPublic(AuthorSchema):
    id: int


class FilterAuthor(FilterPage):
    name: Annotated[str, AfterValidator(sanitize_text)] | None = None
    birth_year: (
        Annotated[int, Field(ge=0), AfterValidator(check_future_year)] | None
    ) = None
