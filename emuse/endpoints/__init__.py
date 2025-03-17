from .index import router as index_router
from .login import router as login_router
from .logout import router as logout_router

__all__ = ['index_router', 'login_router', 'logout_router']
