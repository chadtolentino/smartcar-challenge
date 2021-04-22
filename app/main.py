from fastapi import FastAPI

from .api.vehicles import router as vehicle_router

app = FastAPI()
app.include_router(vehicle_router, prefix="/vehicle")
