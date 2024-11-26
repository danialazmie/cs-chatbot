from fastapi import APIRouter
from chatbot.webhook import main

api_router = APIRouter()

api_router.include_router(main.router, prefix='/v1/webhook', tags=['webhook'])