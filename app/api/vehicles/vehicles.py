from typing import List

from fastapi import APIRouter, HTTPException

from app.thirdparty_translators import translator_selectors as tpt

from . import models

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
    brand_dict = {"1234": "gm", "1235": "gm"}  # could be a query to a database
    brand = brand_dict.get(vehicle_id, "UNKN")
    if brand == "UNKN":
        raise KeyError(f"unable to find brand for vehicle_id {vehicle_id}")

    return brand


@router.get("/{vid}", response_model=models.VehicleInfo)
def get_vehicle_info(vid: str):
    try:
        brand = lookup_vehicle_id(vid)
    except KeyError as e:
        return HTTPException(404, detail=str(e))

    return tpt.select_vehicle_info(brand, vid)


@router.get("/{vid}/doors", response_model=List[models.Door])
def get_doors(vid: str):
    try:
        brand = lookup_vehicle_id(vid)
    except KeyError as e:
        return HTTPException(404, detail=str(e))

    return tpt.select_security_status(brand, vid)


@router.get("/{vid}/fuel", response_model=models.Fuel)
def get_fuel_range(vid: str):
    try:
        brand = lookup_vehicle_id(vid)
    except KeyError as e:
        return HTTPException(404, detail=str(e))

    return tpt.select_fuel_level(brand, vid)


@router.get("/{vid}/battery", response_model=models.Battery)
def get_battery_range(vid: str):
    try:
        brand = lookup_vehicle_id(vid)
    except KeyError as e:
        return HTTPException(404, detail=str(e))

    return tpt.select_battery_level(brand, vid)


@router.post("/{vid}/engine", response_model=models.StartStopEngineResponse)
def start_stop_engine(vid: str, body: models.StartStopEngineRequest):
    try:
        brand = lookup_vehicle_id(vid)
    except KeyError as e:
        return HTTPException(404, detail=str(e))
    # TODO: add this