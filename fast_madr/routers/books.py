from typing import Annotated

from fastapi import APIRouter, Depends
from fast_madr.database import get_session
from fast_madr.models import User, Book
from fast_madr.schemas import BookSchema
from fast_madr.security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix='/books', tags=['books'])
CurrentUser = Annotated[User, Depends(get_current_user)]
O_Session = Annotated[Session, Depends(get_session)]
