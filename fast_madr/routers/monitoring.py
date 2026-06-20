from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from fast_madr.database import get_session

router = APIRouter(tags=['monitoring'])


@router.get('/health', status_code=HTTPStatus.OK)
def health_check(session: Annotated[Session, Depends(get_session)]):
    try:
        session.execute(text('SELECT 1'))

        return {'status': 'online', 'database': 'connected'}

    except Exception:
        raise HTTPException(
            HTTPStatus.SERVICE_UNAVAILABLE,
            detail='Database connection not established',
        )
