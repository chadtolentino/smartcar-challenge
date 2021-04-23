import logging
from typing import List

from fastapi import APIRouter, HTTPException

from app.thirdparty_translators import translator_selectors as tpt

from . import models

logger = logging.getLogger(__name__)
router = APIRouter()


def lookup_vehicle_id(vehicle_id: str) -> str:
    """Performs a lookup of the vehicle id to determine which external api to hit
    (currently lookup data is represented in a dictionary, but could be a DB or other media)

    Args:
        vehicle_id (str): id of vehicle to lookup

    Raises:
        ValueError: raises value error if vehicle_id is not in brand_dict

    Returns:
        str: brand name as string
    """
    brand_dict = {
        "1234": "gm",
        "1235": "gm",
        "FORD": "ford",
    }  # could be a query to a database
    brand = brand_dict.get(vehicle_id, "UNKN")
    logger.info(f"selected brand {brand}")
    if brand == "UNKN":
        raise KeyError(f"unable to find brand for vehicle_id {vehicle_id}")

    return brand


@router.get("/{vehicle_id}", response_model=models.VehicleInfo)
def get_vehicle_info(vehicle_id: str):
    """Fetches vehicle information by vehicle_id"""
    try:
        brand = lookup_vehicle_id(vehicle_id)
    except KeyError as e:
        logger.error(e)
        raise HTTPException(404, detail=str(e))

    return tpt.select_vehicle_info(brand, vehicle_id)


@router.get("/{vehicle_id}/doors", response_model=List[models.Door])
def get_doors(vehicle_id: str):
    """Fetches door security information by vehicle_id"""
    try:
        brand = lookup_vehicle_id(vehicle_id)
    except KeyError as e:
        logger.error(e)
        raise HTTPException(404, detail=str(e))

    return tpt.select_security_status(brand, vehicle_id)


@router.get("/{vehicle_id}/fuel", response_model=models.Fuel)
def get_fuel_range(vehicle_id: str):
    """Fetches fuel range by vehicle_id. Returns null if vehicle does not use fuel"""
    try:
        brand = lookup_vehicle_id(vehicle_id)
    except KeyError as e:
        logger.error(e)
        raise HTTPException(404, detail=str(e))

    return tpt.select_fuel_level(brand, vehicle_id)


@router.get("/{vehicle_id}/battery", response_model=models.Battery)
def get_battery_range(vehicle_id: str):
    """Fetches battery range by vehicle_id. Returns null if vehicle is not electric"""
    try:
        brand = lookup_vehicle_id(vehicle_id)
    except KeyError as e:
        logger.error(e)
        raise HTTPException(404, detail=str(e))

    return tpt.select_battery_level(brand, vehicle_id)


@router.post("/{vehicle_id}/engine", response_model=models.StartStopEngineResponse)
def start_stop_engine(vehicle_id: str, body: models.StartStopEngineRequest):
    """
    Sends a request to start/stop vehicle. Proper commands are START|STOP
    Returns "success" upon success, "error" upon error.
    """
    try:
        brand = lookup_vehicle_id(vehicle_id)
    except KeyError as e:
        logger.error(e)
        raise HTTPException(404, detail=str(e))

    return tpt.select_start_stop_engine(brand, vehicle_id, body.dict())