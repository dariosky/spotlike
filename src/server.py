import logging

import uvicorn

from app import make_app

app = make_app()

if __name__ == "__main__":  # pragma: no cover
    logging.info("Listening on http://localhost:8090")
    uvicorn.run(
        "server:app",
        host="localhost",
        port=8000,
        reload=True,
        reload_excludes=["*/tests/*", ".idea/*"],
    )
