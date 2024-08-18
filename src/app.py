import os

from brotli_asgi import BrotliMiddleware
from fastapi import FastAPI
from fastapi.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from routes import auth
from config import settings


def make_app():
    os.chdir(settings.project_root)

    middlewares = [
        Middleware(BrotliMiddleware, minimum_size=1000),
        Middleware(SessionMiddleware, secret_key=settings.session_secret),
    ]

    app = FastAPI(
        title="Spotlike",
        description="Enjoy Spotify",
        version=settings.version,
        middleware=middlewares,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": 0,
        },  # collapse the swagger schema
    )

    app.include_router(
        auth.router,
        tags=["auth"],
        prefix="/auth",
    )

    return app