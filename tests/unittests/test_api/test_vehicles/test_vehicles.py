from app.api.vehicles import vehicles
import pytest


def test_lookup_vehicle_id():
    assert vehicles.lookup_vehicle_id("1234") == "gm"

    with pytest.raises(KeyError):  # attempts to lookup unknown id
        vehicles.lookup_vehicle_id("INVALID_ID")