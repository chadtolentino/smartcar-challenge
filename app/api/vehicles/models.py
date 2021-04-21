from typing import List

from fastapi import FastAPI
from pydantic import BaseModel


class VehicleInfo(BaseModel):
    vin: str
    color: str
    door_count: int
    drive_train: str


class Door(BaseModel):
    location: str
    locked: bool


class Fuel(BaseModel):
    percent: float


class Battery(BaseModel):
    percent: float


class StartStopEngineRequest(BaseModel):
    action: str


class StartStopEngineResponse(BaseModel):
    status: str