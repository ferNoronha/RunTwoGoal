from fastapi import APIRouter

from .endpoints import users, wallet

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])