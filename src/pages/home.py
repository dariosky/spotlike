from fastapi import FastAPI

from nicegui import app, ui

from config import settings


def get_spotify_auth_url():
    return "https://spotify.com"


def run_gui(fastapi_app: FastAPI) -> None:
    @ui.page("/")
    async def home():
        ui.label("Hello, FastAPI!")

        with ui.row():
            ui.label("Welcome to the Spotify Authentication Page")

            ui.button("Login with Spotify", on_click=lambda: ui.open())

        # NOTE dark mode will be persistent for each user across tabs and server restarts
        ui.dark_mode().bind_value(app.storage.user, "dark_mode")
        ui.checkbox("dark mode").bind_value(app.storage.user, "dark_mode")

    ui.run_with(fastapi_app, storage_secret=settings.session_secret)
