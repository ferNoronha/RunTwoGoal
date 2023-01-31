from fastapi import FastAPI
from api.api import api_router
from config import settings


app = FastAPI(
    title=settings.PROJECT_NAME
)

app.include_router(api_router)


