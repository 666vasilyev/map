# uvicorn main:app --host 0.0.0.0 --port 8000 --reload

from fastapi import FastAPI

from app.api.routes.chains import router as chain_router
from app.api.routes.categories import router as category_router
from app.api.routes.trees import router as tree_router
from app.api.routes.objects import router as object_router
from app.api.routes.products import router as product_router
from app.api.routes.projects import router as project_router



def get_app() -> FastAPI:
    app = FastAPI(title="Logistics App", description="An app to manage objects, chains, categories, and products.")

    # Include routers
    app.include_router(chain_router, prefix="/chains", tags=["Chains"])
    app.include_router(category_router, prefix="/categories", tags=["Categories"])
    app.include_router(tree_router, prefix="/tree", tags=["Trees"])

    app.include_router(object_router, prefix="/objects", tags=["Objects"])
    app.include_router(product_router, prefix="/products", tags=["Products"])
    app.include_router(project_router, prefix="/projects", tags=["Projects"])

    return app
