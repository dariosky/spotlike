import logging


from app import make_app
from pages.home import run_gui

app = make_app()

if __name__ == "__main__":  # pragma: no cover
    logging.info("Listening on http://localhost:8090")
    run_gui(app)
    # uvicorn.run(
    #     "server:app",
    #     host="localhost",
    #     port=8000,
    #     reload=True,
    #     reload_excludes=["*/tests/*", ".idea/*"],
    # )
