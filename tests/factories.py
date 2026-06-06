import factory

from fast_madr.models import Author, Book, User


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

    name = factory.Faker('name')


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
