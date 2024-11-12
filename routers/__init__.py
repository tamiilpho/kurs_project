__all__ = ["router"]

from aiogram import Router
from .commands import router as commands_router
from .user_navigation import router as navigation_router
from .callbacks import router as callbacks_router

router = Router(name=__name__)
router.include_routers(commands_router, navigation_router, callbacks_router)
