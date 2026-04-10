from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from happiness_backend.database import initialize_database
from happiness_backend.routers.admin import router as admin_router
from happiness_backend.routers.public import router as public_router
from happiness_backend.settings import get_settings


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database(settings)
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="0.1.0",
    description="Bilingual web menu and lightweight staff panel for Happiness Cafe.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public_router)
app.include_router(admin_router)

