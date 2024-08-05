from fastapi import FastAPI

from .routers import init_router
from .models import init_db


def create_app():
    app = FastAPI()

    init_db()

    init_router(app)

    return app
