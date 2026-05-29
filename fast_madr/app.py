from fastapi import FastAPI

from fast_madr.routers import auth, authors, books, users

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(authors.router)


@app.get('/')
def read_root():
    return {'Olá mundo': 'Hello world'}
