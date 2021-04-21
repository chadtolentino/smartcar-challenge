from typing import List
from fastapi import APIRouter
from . import models

router = APIRouter()


@router.get("/{vid}", response_model=models.VehicleInfo)
async def get_vehicle_info(vid: int):
    pass


@router.get("/{vid}/doors", response_model=List[models.Door])
async def get_doors(vid: int):
    pass


@router.get("/{vid}/fuel", response_model=models.Fuel)
async def get_fuel_range(vid: int):
    pass


@router.get("/{vid}/battery", response_model=models.Battery)
async def get_battery_range(vid: int):
    pass


@router.post("/{vid}/engine", response_model=models.StartStopEngineResponse)
async def start_stop_engine(vid: int, body: models.StartStopEngineRequest):
    pass