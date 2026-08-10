import factory
from faker import Faker

from fast_madr.models import Author, Book, User
from fast_madr.utils import sanitize_text

fake = Faker()


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    is_active = True
    is_admin = False


class AuthorFactory(factory.Factory):
    class Meta:
        model = Author

    name = factory.LazyAttribute(lambda x: sanitize_text(fake.name()))
    birth_year = factory.Faker('random_int', min=1800, max=2005)


class BookFactory(factory.Factory):
    class Meta:
        model = Book

    year = factory.Faker('random_int', min=1800, max=2026)
    title = factory.Sequence(lambda y: f'title{y}')
