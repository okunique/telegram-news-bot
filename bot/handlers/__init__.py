from aiogram import Dispatcher
from . import status, digest, post

def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    dp.include_router(status.router)
    dp.include_router(digest.router)
    dp.include_router(post.router) 