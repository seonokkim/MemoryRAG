from fastapi import APIRouter

from app.api import coach, dev, feedback, health, swings, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(swings.router)
api_router.include_router(coach.router)
api_router.include_router(feedback.router)
api_router.include_router(dev.router)
