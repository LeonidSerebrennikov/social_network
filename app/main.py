from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.redis_client import redis_client
from app.router_registry import ComponentRegistry

from app.cmp.users.routes import router as user_router
from app.cmp.posts.routes import router as posts_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.initialize()
    yield
    await redis_client.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.include_router(router=user_router)
app.include_router(router=posts_router)
# ComponentRegistry.register_all(app)
