from fastapi import Request, Depends, HTTPException
from sqlmodel import Session
from starlette import status

from db.auth import User
from db.main import get_session


def current_user(
    request: Request,
    db_session: Session = Depends(get_session),
) -> User:
    if "uid" in request.session:
        user = db_session.get(User, request.session["uid"])
    else:
        user = None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
