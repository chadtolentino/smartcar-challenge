import pytest
from fastapi import HTTPException
from app.thirdparty_translators.gm import vehicles

test_inputs = [
    (ValueError, "getVehicleInfoService", ""),  # tests with missing id
    (ValueError, "", "1234"),  # tests with missing url
    (HTTPException, "dummy", "1234"),  # tests bad url
]


@pytest.mark.parametrize("exc, url, vid", test_inputs)
def test_post_vehicle_request_exceptions(exc, url: str, vid: str):
    with pytest.raises(exc):
        vehicles.post_vehicle_request(url, vid)


def test_post_vehicle_request():
    # asserts normal request works
    assert vehicles.post_vehicle_request("getVehicleInfoService", "1234")

    # tests to see if raw response works
    assert "status" in vehicles.post_vehicle_request(
        "getVehicleInfoService", "1234", raw=True
    )


def test_translator_wrapper():
    with pytest.raises(HTTPException):
        vehicles.translate_vehicle_info({})
        vehicles.translate_security_status({})
        vehicles.translate_battery_level({})
        vehicles.translate_fuel_level({})


def test_translate_vehicle_info():
    input_data = {
        "vin": {"type": "String", "value": "1213231"},
        "color": {"type": "String", "value": "Metallic Silver"},
        "fourDoorSedan": {"type": "Boolean", "value": "True"},
        "twoDoorCoupe": {"type": "Boolean", "value": "False"},
        "driveTrain": {"type": "String", "value": "v8"},
    }
    expected_output = {
        "vin": "1213231",
        "color": "Metallic Silver",
        "doorCount": 4,
        "driveTrain": "v8",
    }

    test_output = vehicles.translate_vehicle_info(input_data)

    assert test_output
    assert test_output.dict() == expected_output

    # changes the door count
    input_data["fourDoorSedan"]["value"] = "False"
    input_data["twoDoorCoupe"]["value"] = "True"
    expected_output["doorCount"] = 2

    test_output2 = vehicles.translate_vehicle_info(input_data)

    assert test_output2
    assert test_output2.dict() == expected_output


def test_security_status():
    input_data = {
        "doors": {
            "type": "Array",
            "values": [
                {
                    "location": {"type": "String", "value": "frontLeft"},
                    "locked": {"type": "Boolean", "value": "True"},
                },
                {
                    "location": {"type": "String", "value": "frontRight"},
                    "locked": {"type": "Boolean", "value": "True"},
                },
                {
                    "location": {"type": "String", "value": "backLeft"},
                    "locked": {"type": "Boolean", "value": "False"},
                },
                {
                    "location": {"type": "String", "value": "backRight"},
                    "locked": {"type": "Boolean", "value": "True"},
                },
            ],
        }
    }
    expected_output = [
        {"location": "frontLeft", "locked": True},
        {"location": "frontRight", "locked": True},
        {"location": "backLeft", "locked": False},
        {"location": "backRight", "locked": True},
    ]

    test_output = [d.dict() for d in vehicles.translate_security_status(input_data)]
    assert test_output
    assert test_output == expected_output


def test_translate_fuel_level():
    input_data = {
        "tankLevel": {"type": "Number", "value": "30.2"},
        "batteryLevel": {"type": "Null", "value": "null"},
    }
    expected_output = {"percent": 30.2}

    test_output = vehicles.translate_fuel_level(input_data)
    assert test_output
    assert test_output.dict() == expected_output

    # tests null value
    input_data["tankLevel"]["value"] = "null"
    expected_output["percent"] = None

    test_output = vehicles.translate_fuel_level(input_data)
    assert test_output
    assert test_output.dict() == expected_output

    # tests invalid fuel level
    input_data["tankLevel"]["value"] = "invalid"
    with pytest.raises(ValueError):
        vehicles.translate_fuel_level(input_data)


def test_translate_battery_level():
    input_data = {
        "batteryLevel": {"type": "Number", "value": "30.2"},
        "tankLevel": {"type": "Null", "value": "null"},
    }
    expected_output = {"percent": 30.2}

    test_output = vehicles.translate_battery_level(input_data)

    assert test_output
    assert test_output.dict() == expected_output

    # tests null value
    input_data["batteryLevel"]["value"] = "null"
    expected_output["percent"] = None

    test_output = vehicles.translate_fuel_level(input_data)
    assert test_output
    assert test_output.dict() == expected_output

    # tests invalid battery level
    input_data["batteryLevel"]["value"] = "invalid"
    with pytest.raises(ValueError):
        vehicles.translate_battery_level(input_data)


def test_translate_engine_command():
    assert vehicles.translate_engine_command("START") == "START_VEHICLE"
    assert vehicles.translate_engine_command("STOP") == "STOP_VEHICLE"
    with pytest.raises(HTTPException):
        vehicles.translate_engine_command("INVALID")


def test_translate_start_stop_engine():
    input_data = {"status": "EXECUTED"}
    expected_output = {"status": "success"}

    test_output = vehicles.translate_start_stop_engine(input_data)
    assert test_output == expected_output

    # tests different message
    input_data = {"status": "FAILED"}
    expected_output = {"status": "error"}

    test_output = vehicles.translate_start_stop_engine(input_data)
    assert test_output == expected_output

    # tests invalid
    input_data = {"status": "INVALID"}
    with pytest.raises(HTTPException):
        vehicles.translate_start_stop_engine(input_data)
