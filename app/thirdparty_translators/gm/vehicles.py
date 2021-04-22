from typing import List, Optional, Type

import requests
from fastapi import HTTPException

from app.api.vehicles import models

BASE_URL = "http://gmapi.azurewebsites.net"  # hardcoded for now, but could be pulled from config file in future


def post_vehicle_request(
    url: str, vehicle_id: str, response_type="JSON", extra_data: Optional[dict] = None
) -> dict:
    f"""makes a POST request to {BASE_URL} and returns the result as a dict

    Args:
        url (str): route to service
        vehicle_id (str): vehicle id
        response_type (str, optional): response type from service. Defaults to "JSON".
        extra_data(dict, optional): any extra values that need to be passed in POST body

    Raises:
        ValueError: raises if vehicle_id is empty or None
        ValueError: raises if url is empty or None
        HTTPException: raises if status code is not 200
        ValueError: raises if data json is None

    Returns:
        dict: json data from response as dict
    """
    # TODO: log request
    if not vehicle_id:
        raise ValueError("missing vehicle id")
    if not url:
        raise ValueError("missing URL")

    if url[0] != "/":  # makes sure to add a slash if missing
        url = "/" + url

    post_data = {"id": vehicle_id, "responseType": response_type}
    if extra_data:  # adds extra key/values if provided
        post_data.update(extra_data)

    res = requests.post(f"{BASE_URL}{url}", json=post_data)
    res_json = res.json()
    data = res_json.get("data")

    status = res_json.get("status", str(res.status_code))

    if status != "200":
        raise HTTPException(int(status), detail=res_json.get("reason"))

    if data is None:  # very rare case
        raise ValueError("received empty response with no data")

    return data


def translate_vehicle_info(data: dict) -> models.VehicleInfo:
    """Translates vehicle info from GM API format to Smartcar format

    Args:
        data (dict): data from GM API response

    Returns:
        models.VehicleInfo: Smartcar formatted data
    """
    # data = post_vehicle_request("getVehicleInfoService", vehicle_id)

    new_data: dict = {}
    if "vin" in data:
        new_data["vin"] = data["vin"].get("value")

    if "color" in data:
        new_data["color"] = data["color"].get("value")

    if "driveTrain" in data:
        new_data["driveTrain"] = data["driveTrain"].get("value")

    door_count = 0  # gets door count
    if data.get("twoDoorCoupe") and data["twoDoorCoupe"].get("value") == "True":
        door_count = 2
    elif data.get("fourDoorSedan") and data["fourDoorSedan"].get("value") == "True":
        door_count = 4

    new_data["doorCount"] = door_count

    return models.VehicleInfo.parse_obj(new_data)


def translate_security_status(data: dict) -> List[models.Door]:
    """Translates security status info from GM API format to Smartcar format

    Args:
        data (dict): data from GM API response

    Raises:
        TypeError: raises typerror if door.values is not a list

    Returns:
        List[models.Door]: list of door objects
    """
    # data = post_vehicle_request("getSecurityStatusService", vehicle_id)
    new_data_list = []
    if data.get("doors"):
        door_list = data["doors"].get("values")
        if not isinstance(door_list, list):  # rare edge case
            raise TypeError(f"was expecting list of doors, instead got {door_list}")

        for door in door_list:
            new_door = {}
            new_door["location"] = door["location"].get("value")
            new_door["locked"] = (
                True if door["locked"].get("value") == "True" else False
            )
            new_data_list.append(models.Door.parse_obj(new_door))

    return new_data_list


def translate_fuel_level(data: dict) -> models.Fuel:
    """[summary]

    Args:
        data (dict): [description]

    Returns:
        models.Fuel: [description]
    """
    # data = post_vehicle_request("getEnergyService", vehicle_id)
    if "tankLevel" in data:
        fuel_value_str = data["tankLevel"].get("value")
    else:
        fuel_value_str = None

    if fuel_value_str is None or fuel_value_str.lower() == "null":
        fuel_value = None
    else:
        try:
            fuel_value = float(fuel_value_str)
        except ValueError as e:
            raise (e)

    return models.Fuel(percent=fuel_value)


def translate_battery_level(data: dict) -> models.Battery:
    # data = post_vehicle_request("getEnergyService", vehicle_id)
    if "batteryLevel" in data:
        battery_value_str = data["batteryLevel"].get("value")
    else:
        battery_value_str = None

    if battery_value_str is None or battery_value_str.lower() == "null":
        battery_value = None
    else:
        try:
            battery_value = float(battery_value_str)
        except ValueError as e:
            raise (e)

    return models.Battery(percent=battery_value)


def translate_start_stop_engine(data: dict) -> models.StartStopEngineResponse:
    # translated_command = ""
    # data = post_vehicle_request(
    #     "actionEngineService", vehicle_id, extra_data={"command": translated_command}
    # )
    pass
