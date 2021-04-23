from fastapi.testclient import TestClient

import pytest
from app.main import app

client = TestClient(app)


vehicle_info_inputs = [
    (
        "1234",
        {
            "vin": "123123412412",
            "color": "Metallic Silver",
            "doorCount": 4,
            "driveTrain": "v8",
        },
        200,
    ),
    (
        "1235",
        {
            "vin": "1235AZ91XP",
            "color": "Forest Green",
            "doorCount": 2,
            "driveTrain": "electric",
        },
        200,
    ),
    ("INVALID", {}, 404),
]


@pytest.mark.parametrize("vehicle_id, expected, status_code", vehicle_info_inputs)
def test_get_vehicle_info(vehicle_id: str, expected: dict, status_code: int):
    response = client.get(f"/vehicles/{vehicle_id}")
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json() == expected


vehicle_doors_input = [("1234", 4, 200), ("1235", 2, 200), ("INVALID", 0, 404)]


@pytest.mark.parametrize("vehicle_id, door_count, status_code", vehicle_doors_input)
def test_get_vehicle_doors(vehicle_id: str, door_count: int, status_code: int):
    response = client.get(f"/vehicles/{vehicle_id}/doors")

    assert response.status_code == status_code
    if status_code == 200:
        doors = response.json()
        assert len(doors) == door_count

        for door in doors:
            assert door.get("location") and door.get("locked") is not None


@pytest.mark.parametrize(
    "vehicle_id, has_fuel, status_code",
    [("1234", True, 200), ("1235", False, 200), ("INVALID", True, 404)],
)
def test_get_vehicle_fuel_range(vehicle_id: str, has_fuel: bool, status_code: int):
    response = client.get(f"/vehicles/{vehicle_id}/fuel")
    assert response.status_code == status_code
    if status_code == 200:
        if has_fuel:
            assert isinstance(response.json().get("percent"), float)
        else:
            assert response.json().get("percent") is None


@pytest.mark.parametrize(
    "vehicle_id, has_battery, status_code",
    [("1234", False, 200), ("1235", True, 200), ("INVALID", True, 404)],
)
def test_get_vehicle_battery_range(
    vehicle_id: str, has_battery: bool, status_code: int
):
    response = client.get(f"/vehicles/{vehicle_id}/battery")
    assert response.status_code == status_code
    if status_code == 200:
        if has_battery:
            assert isinstance(response.json().get("percent"), float)
        else:
            assert response.json().get("percent") is None


start_stop_inputs = [
    ("1234", "START", 200),
    ("1234", "STOP", 200),
    ("1234", "INVALID", 400),
    ("123", "START", 404),
]


@pytest.mark.parametrize("vehicle_id, action, status_code", start_stop_inputs)
def test_post_vehicle_start_stop_engine(vehicle_id: str, action: str, status_code: int):
    response = client.post(f"/vehicles/{vehicle_id}/engine", json={"action": action})

    assert response.status_code == status_code
    if status_code == 200:
        assert isinstance(response.json().get("status"), str)