from fastapi import FastAPI
from api.database import get_db
from api.routers import auth_router, item_router

app = FastAPI(
    title="Imputation Platform API",
    version="1.0.0",
    description="API para análisis y imputación de datos multivariados"
)

app.include_router(auth_router.router)
app.include_router(item_router.router)

@app.get("/")
async def root():
    return {"message": "API de Imputación activa"}