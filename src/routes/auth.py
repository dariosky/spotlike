import logging
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from spotipy import SpotifyOauthError

from auth import logged_user
from config import settings
from db.auth import User
from multispot import get_auth_manager, SpotUserActions

router = APIRouter()

logger = logging.getLogger(__file__)


@router.post("/logout")
def logout(request: Request, user: User = Depends(logged_user)):
    del request.session["uid"]
    return {"detail": "Logged out successfully"}


@router.get("/user", response_model=User)
def current_user(user: User = Depends(logged_user)):
    return user


@router.get("/connect")
def connect(code: str, request: Request):
    redirect_uri = f"{settings.hostname}/connect"
    try:
        auth_manager = get_auth_manager(None, redirect_uri=redirect_uri)
        auth_manager.get_access_token(code, check_cache=False)
        act = SpotUserActions(user=None, auth_manager=auth_manager)
        request.session["uid"] = act.user.id
        return RedirectResponse("/")
    except SpotifyOauthError as e:
        return {"message": str(e)}, 400


@router.get("/redirect")
def redirect():
    return RedirectResponse("/")
