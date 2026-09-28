import pytest

from app.services.geo import haversine_distance_m

BRANCH = {"lat": 47.9188, "lon": 106.9176}

# (name, lat, lon, expected_m, tolerance_m)
CASES = [
    ("same_point", 47.9188, 106.9176, 0, 1),
    ("about_150m_north", 47.92015, 106.91760, 150, 5),
    ("about_5km", 47.9638, 106.9176, 5000, 100),
]


@pytest.mark.parametrize("name,lat,lon,expected_m,tolerance_m", CASES)
def test_haversine_known_distances(name, lat, lon, expected_m, tolerance_m):
    distance = haversine_distance_m(BRANCH["lat"], BRANCH["lon"], lat, lon)
    assert abs(distance - expected_m) <= tolerance_m, f"{name}: got {distance}, expected ~{expected_m}"


def test_haversine_is_symmetric():
    a = haversine_distance_m(47.9188, 106.9176, 47.9300, 106.9300)
    b = haversine_distance_m(47.9300, 106.9300, 47.9188, 106.9176)
    assert a == pytest.approx(b)
