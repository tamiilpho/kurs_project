__all__ = ["router"]

from aiogram import Router
from .user_messages_answer import router as user_messages_answer_router
from .admin_messages_answer import router as admin_messages_answer_router

router = Router(name=__name__)
router.include_routers(user_messages_answer_router, admin_messages_answer_router,)
