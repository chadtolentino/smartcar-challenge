from typing import Optional

from pydantic import BaseModel


class VehicleInfo(BaseModel):
    vin: str
    color: str
    doorCount: int
    driveTrain: str


class Door(BaseModel):
    location: str
    locked: bool


class Fuel(BaseModel):
    percent: Optional[float]


class Battery(BaseModel):
    percent: Optional[float]


class StartStopEngineRequest(BaseModel):
    action: str


class StartStopEngineResponse(BaseModel):
    status: str