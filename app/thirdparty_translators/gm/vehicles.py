import logging
from typing import List, Optional

import requests
from fastapi import HTTPException
from pydantic.error_wrappers import ValidationError

from app.api.vehicles import models

logger = logging.getLogger(__name__)

BASE_URL = "http://gmapid.azurewebsites.net"  # hardcoded for now, but could be pulled from config file in future


def post_vehicle_request(
    url: str,
    vehicle_id: str,
    raw=False,
    response_type="JSON",
    extra_data: Optional[dict] = None,
) -> dict:
    f"""Makes a POST request to {BASE_URL} and returns the result as a dict

    Args:
        url (str): route to service
        vehicle_id (str): vehicle id
        raw: if True, return the entire response, not just the data dict
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
    if not vehicle_id:
        raise ValueError("missing vehicle id")
    if not url:
        raise ValueError("missing URL")

    if url[0] != "/":  # makes sure to add a slash if missing
        url = "/" + url

    post_data = {"id": vehicle_id, "responseType": response_type}
    if extra_data:  # adds extra key/values if provided
        post_data.update(extra_data)
        logger.debug(f"post_data: {post_data}")

    res = requests.post(f"{BASE_URL}{url}", json=post_data)
    res_json = res.json()

    if not raw:  # grabs only the data portion if not raw
        data = res_json.get("data")
    else:
        data = res_json

    logger.debug(f"data from POST request: {data}")

    status = res_json.get("status", str(res.status_code))

    if status != "200":
        err_message = res_json.get("reason")
        logger.error(err_message)
        raise HTTPException(int(status), detail=err_message)

    if data is None:  # very rare case
        err_message = "received empty response from GM API with no data"
        logger.error(err_message)
        raise HTTPException(status_code=500, detail=err_message)

    return data


def translator(func):
    """Decorator to wrap validation and keyerrors into one error

    Raises:
        ValueError: raises value error when unable to translate data

    Args:
        func ([type]): translate function
    """

    def inner(data: dict):
        try:
            translated_data = func(data)
            logger.debug(f"translated data: {translated_data}")
            return translated_data
        except (ValidationError, KeyError) as e:
            logger.error(e)
            raise HTTPException(
                status_code=500,
                detail="translation failed because of incorrectly formed data from external API",
            )

    return inner


@translator
def translate_vehicle_info(data: dict) -> models.VehicleInfo:
    """Translates vehicle info from GM API format to Smartcar format

    Args:
        data (dict): data from GM API response

    Returns:
        models.VehicleInfo: Smartcar formatted data
    """

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


@translator
def translate_security_status(data: dict) -> List[models.Door]:
    """Translates security status info from GM API format to Smartcar format

    Args:
        data (dict): data from GM API response

    Raises:
        TypeError: raises type error if door.values is not a list

    Returns:
        List[models.Door]: list of door objects
    """
    new_data_list = []
    if data.get("doors"):
        door_list = data["doors"].get("values")
        if not isinstance(door_list, list):  # rare edge case
            err_message = f"was expecting list of doors, instead got {door_list}"
            logger.error(err_message)
            raise TypeError(err_message)

        for door in door_list:
            new_door = {}
            new_door["location"] = door["location"].get("value")
            new_door["locked"] = (
                True if door["locked"].get("value") == "True" else False
            )
            new_data_list.append(models.Door.parse_obj(new_door))

    return new_data_list


@translator
def translate_fuel_level(data: dict) -> models.Fuel:
    """Translates fuel information from GM API to Smartcar format

    Args:
        data (dict): energy data retrieved from GM

    Raises:
        ValueError: raises value error if fuel_value_str cannot be converted to float

    Returns:
        models.Fuel: [description]
    """
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
            raise ValueError(f"{fuel_value_str} is not a correct percentage")

    return models.Fuel(percent=fuel_value)


@translator
def translate_battery_level(data: dict) -> models.Battery:
    """Translates battery information from GM API to Smartcar format

    Args:
        data (dict): energy data retrieved from GM

    Raises:
        ValueError: raises value error if battery_value_str cannot be converted to float

    Returns:
        models.Battery: [description]
    """
    if "batteryLevel" in data:
        battery_value_str = data["batteryLevel"].get("value")
    else:
        battery_value_str = None

    if battery_value_str is None or battery_value_str.lower() == "null":
        battery_value = None
    else:
        try:
            battery_value = float(battery_value_str)  # could possibly throw error?
        except ValueError as e:
            raise ValueError(f"{battery_value_str} is not a correct percentage")

    return models.Battery(percent=battery_value)


def translate_engine_command(command: str) -> str:
    """Translates engine start/stop command to GM equivalent

    Args:
        command (str): START|STOP

    Raises:
        HTTPException: raises 400 error if command is not in command_dict

    Returns:
        str: GM START|STOP command
    """

    # {SMARTCAR_KEY: GM_VALUE}
    command_dict = {"START": "START_VEHICLE", "STOP": "STOP_VEHICLE"}

    if command in command_dict:
        return command_dict[command]
    else:
        err_message = f"command {command} not recognized/missing"
        logger.error(err_message)
        raise HTTPException(status_code=400, detail=err_message)


@translator
def translate_start_stop_engine(data: dict) -> models.StartStopEngineResponse:
    """Translates response from GM start/stop engine into Smartcar response

    Args:
        data (dict): dict containing status key

    Raises:
        HTTPException: raises 500 error if status is not in status_dict

    Returns:
        models.StartStopEngineResponse: Smartcar StartStopEngine response
    """
    # {GM Status: Smartcar Status}
    status_dict = {"EXECUTED": "success", "FAILED": "error"}
    status = data["status"]
    if status in status_dict:
        translated_status = status_dict[status]
    else:
        err_message = f"status {status} not in status_dict!"
        logger.error(err_message)
        raise HTTPException(status_code=500, detail=err_message)

    return models.StartStopEngineResponse(status=translated_status)


def start_stop_engine(
    vehicle_id: str, post_data: dict
) -> models.StartStopEngineResponse:
    """Wraps translate_engine_command and translate_start_stop_engine
    Makes a post request to get data and then returns Smartcar StartStopEngine response

    Args:
        vehicle_id (str): vehicle id
        post_data (dict): dict containing command to send to GM API

    Returns:
        models.StartStopEngineResponse: Smartcar StartStopEngine response
    """
    command = post_data.get("action", "")
    translated_command = translate_engine_command(command)
    data = post_vehicle_request(
        "actionEngineService",
        vehicle_id,
        raw=True,
        extra_data={"command": translated_command},
    )
    return translate_start_stop_engine(data.get("actionResult", {}))
