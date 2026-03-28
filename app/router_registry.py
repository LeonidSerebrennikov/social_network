from fastapi import FastAPI, APIRouter
from typing import List

class ComponentRegistry:
    _routers = []
    
    @classmethod
    def register(cls, router):
        cls._routers.append(router)
        return router
    
    @classmethod
    def register_all(cls, app: FastAPI):
        for router in cls._routers:
            app.include_router(router)

def register_component(router: APIRouter, prefix: str = "", tags: List[str] = None):
    if prefix:
        router.prefix = prefix
    if tags:
        router.tags = tags
    ComponentRegistry.register(router)
    return router