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


class AuthorFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Author
        sqlalchemy_session = None
        sqlalchemy_session_persistence = 'commit'

    name = factory.LazyAttribute(lambda x: sanitize_text(fake.name()))
    birth_year = factory.Faker('random_int', min=1800, max=2005)


class BookFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Book
        sqlalchemy_session = None
        sqlalchemy_session_persistence = 'commit'
        exclude = 'author'

    year = factory.Faker('random_int', min=1800, max=2026)
    title = factory.Sequence(lambda y: f'title{y}')
    author = factory.SubFactory(AuthorFactory)
    author_id = factory.SelfAttribute('author.id')
