from typing import List


from app.api.vehicles import models as vehicle_models

from .gm import vehicles as gm_vehicles


# following functions select which translators to use based on brand
def select_vehicle_info(brand: str, vehicle_id: str) -> vehicle_models.VehicleInfo:
    if brand == "gm":
        data = gm_vehicles.post_vehicle_request("getVehicleInfoService", vehicle_id)
        return gm_vehicles.translate_vehicle_info(data)
    else:
        raise ValueError(f"brand {brand} not found!")


def select_security_status(brand: str, vehicle_id: str) -> List[vehicle_models.Door]:
    if brand == "gm":
        data = gm_vehicles.post_vehicle_request("getSecurityStatusService", vehicle_id)
        return gm_vehicles.translate_security_status(data)
    else:
        raise ValueError(f"brand {brand} not found!")


def select_fuel_level(brand: str, vehicle_id: str) -> vehicle_models.Fuel:
    if brand == "gm":
        data = gm_vehicles.post_vehicle_request("getEnergyService", vehicle_id)
        return gm_vehicles.translate_fuel_level(data)
    else:
        raise ValueError(f"brand {brand} not found!")


def select_battery_level(brand: str, vehicle_id: str) -> vehicle_models.Battery:
    if brand == "gm":
        data = gm_vehicles.post_vehicle_request("getEnergyService", vehicle_id)
        return gm_vehicles.translate_battery_level(data)
    else:
        raise ValueError(f"brand {brand} not found!")


def select_start_stop_engine(
    brand: str, vehicle_id: str, post_data: dict
) -> vehicle_models.StartStopEngineResponse:
    if brand == "gm":
        return gm_vehicles.start_stop_engine(vehicle_id, post_data)
    else:
        raise ValueError(f"brand {brand} not found!")