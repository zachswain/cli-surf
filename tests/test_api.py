"""
QA tests for api.py
Make sure pytest is installed: pip install pytest
Run pytest: pytest
"""

from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest
from openmeteo_requests.Client import OpenMeteoRequestsError

from src.api import (
    current_wind_temp,
    default_location,
    forecast,
    gather_data,
    get_coordinates,
    get_hourly_forecast,
    get_rain,
    get_uv,
    get_uv_history,
    ocean_information,
    ocean_information_history,
    seperate_args_and_get_location,
)
from src.helper import arguments_dictionary


@pytest.mark.parametrize(
    ("status_code", "json_data", "expected_result"),
    [
        (
            HTTPStatus.OK,
            {"loc": "43.03,-72.001", "city": "New York"},
            ["43.03", "-72.001", "New York"],
        ),
        (HTTPStatus.BAD_REQUEST, {}, "No data"),
    ],
)
def test_default_location_mocked(
    mocker, status_code, json_data, expected_result
):
    # Arrange: Mock the response from the API
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json = Mock(return_value=json_data)

    # Mock the 'requests.get' method
    mock_requests = mocker.patch("requests.get", return_value=mock_response)

    # Act: Call the function
    result = default_location()

    # Assert: Verify function returns correct location data
    assert result == expected_result

    # Assert: Verify 'requests.get' is called with correct arguments
    mock_requests.assert_called_once_with("https://ipinfo.io/json", timeout=10)


def test_get_coordinates():
    coordinates = get_coordinates(["loc=santa_cruz"])
    lat = coordinates[0]
    long = coordinates[1]
    assert isinstance(lat, (int, float))
    assert isinstance(long, (int, float))


def test_get_uv():
    uv = get_uv(37, 122, 2)
    assert isinstance(uv, (int, float))


def test_ocean_information():
    ocean = ocean_information(37, 122, 2)
    assert isinstance(ocean[0], (int, float))
    assert isinstance(ocean[1], (int, float))
    assert isinstance(ocean[2], (int, float))


def test_forecast():
    """
    Test forecast() at an arbitrary location(palm beach),
    ensures it returns 7 days of heights/directions/periods
    """
    len_of_forecast_list = 7
    fc = forecast(26.705, -80.036, 1, 7)
    heights = fc["wave_height_max"]
    directions = fc["wave_direction_dominant"]
    periods = fc["wave_period_max"]
    assert len(heights) == len_of_forecast_list
    assert len(directions) == len_of_forecast_list
    assert len(periods) == len_of_forecast_list


def test_gather_data():
    """
    Gather data needs the arguments dictionary as input,
    so we will get this by calling arguments_dictionary()
    from helper.py with arbitrary arguments
    """
    lat = 33.37
    long = -117.57
    arguments = arguments_dictionary(lat, long, "San Clemente", [])
    ocean_data_dict = gather_data(lat, long, arguments)
    assert ocean_data_dict["Location"] == "San Clemente"
    assert ocean_data_dict["Lat"] == lat
    assert ocean_data_dict["Long"] == long


def test_seperate_args_and_get_location():
    """
    Test with an abritrary location
    """
    location = ["location=pleasure_point_california"]
    location_data = seperate_args_and_get_location(location)
    lat = location_data["lat"]
    long = location_data["long"]
    city = location_data["city"]
    assert isinstance(lat, (int, float))
    assert isinstance(long, (int, float))
    assert "Pleasure Point" in str(city)


def test_get_uv_history_basic_functionality():
    """
    Test the basic functionality of the get_uv_history function.

    This test verifies that the function returns a string
    when provided with valid latitude and longitude coordinates.
    """
    uv = get_uv_history(31.9505, 115.8605, 2)  # Perth coordinates
    assert isinstance(uv, str)


def test_get_uv_history_invalid_coordinates():
    """
    Test get_uv_history with invalid coordinates.

    This test checks that the function raises an OpenMeteoRequestsError
    when provided with latitude and longitude values that are out of range.
    """
    with pytest.raises(OpenMeteoRequestsError):
        get_uv_history(1000, -2000, 2)


@patch("src.api.testing", new=0)  # Set testing variable to 0
def test_get_uv_history_api_response():
    """
    Test how get_uv_history handles API response.

    This test verifies that the function returns the expected values
    when called with valid coordinates while patching the API call request.
    """
    result = get_uv_history(31.9505, 115.8605, 1)
    expected_result = "0.6"
    assert result == expected_result


def test_ocean_information_history_basic_functionality():
    """
    Test the basic functionality of the ocean_information_history function.

    This test checks that the function returns actual values for
    the wave data points when provided with valid coordinates.
    """
    waves = ocean_information_history(31.9505, 115.8605, 2)
    assert waves[0] is not None
    assert waves[1] is not None
    assert waves[2] is not None


def test_ocean_information_history_invalid_coordinates():
    """
    Test ocean_information_history with invalid coordinates.

    This test ensures that the function raises an OpenMeteoRequestsError
    when provided with latitude and longitude values that are out of range.
    """
    with pytest.raises(OpenMeteoRequestsError):
        ocean_information_history(1000, -2000, 2)


def test_ocean_information_history_response_format():
    """
    Test the response format of ocean_information_history.

    This test verifies that the function returns a list with a
    specific number of elements when called with valid coordinates.
    """
    waves = ocean_information_history(31.9505, 115.8605, 2)
    expected_wave_count = 3
    assert isinstance(waves, list)
    assert len(waves) > 0
    assert len(waves) == expected_wave_count


@patch("src.api.testing", new=0)  # Set testing variable to 0
def test_ocean_information_history():
    """
    Test how ocean_information_history handles API response.

    This test verifies that the function returns the expected values
    when called with valid coordinates while patching the API call request.
    """
    result = ocean_information_history(31.9505, 115.8605, 1)
    expected_result = ["0.6", "0.6", "0.6"]
    assert result == expected_result


# ---- New mocked API tests below ----


def _make_openmeteo_mock(current_values=None, daily_values=None,
                         hourly_values=None):
    """Build a mock openmeteo response object."""
    mock_response = Mock()

    if current_values is not None:
        mock_current = Mock()
        for i, val in enumerate(current_values):
            mock_var = Mock()
            mock_var.Value.return_value = val
            mock_current.Variables.side_effect = (
                lambda idx, vals=current_values: Mock(
                    Value=Mock(return_value=vals[idx])
                )
            )
        mock_response.Current.return_value = mock_current

    if daily_values is not None:
        mock_daily = Mock()
        import numpy as np
        mock_daily.Variables.side_effect = lambda idx: Mock(
            ValuesAsNumpy=Mock(return_value=np.array(daily_values[idx]))
        )
        mock_daily.Time.return_value = 1704067200  # 2024-01-01 UTC
        mock_daily.TimeEnd.return_value = 1704153600  # 2024-01-02 UTC
        mock_daily.Interval.return_value = 86400
        mock_response.Daily.return_value = mock_daily

    if hourly_values is not None:
        mock_hourly = Mock()
        import numpy as np
        mock_hourly.Variables.side_effect = lambda idx: Mock(
            ValuesAsNumpy=Mock(return_value=np.array(hourly_values[idx]))
        )
        mock_hourly.Time.return_value = 1704067200
        mock_hourly.TimeEnd.return_value = 1704153600
        mock_hourly.Interval.return_value = 3600
        mock_response.Hourly.return_value = mock_hourly

    return mock_response


def test_current_wind_temp_mocked(mocker):
    """Mock openmeteo and verify [temp, wind_speed, wind_dir]."""
    mock_resp = _make_openmeteo_mock(current_values=[72.5, 10.3, 180.0])
    mock_client = Mock()
    mock_client.weather_api.return_value = [mock_resp]
    mocker.patch(
        "src.api.openmeteo_requests.Client", return_value=mock_client
    )
    result = current_wind_temp(36.0, -122.0, 1)
    assert len(result) == 3
    assert result[0] == 72.5
    assert result[1] == 10.3
    assert result[2] == 180.0


def test_get_rain_mocked(mocker):
    """Mock openmeteo and verify (rain_sum, precip_prob) tuple."""
    import numpy as np

    mock_resp = Mock()
    mock_daily = Mock()
    mock_daily.Variables.side_effect = lambda idx: Mock(
        ValuesAsNumpy=Mock(
            return_value=np.array([0.5] if idx == 0 else [45.0])
        )
    )
    mock_resp.Daily.return_value = mock_daily
    mock_client = Mock()
    mock_client.weather_api.return_value = [mock_resp]
    mocker.patch(
        "src.api.openmeteo_requests.Client", return_value=mock_client
    )
    rain_sum, precip_prob = get_rain(36.0, -122.0, 1)
    assert rain_sum == 0.5
    assert precip_prob == 45.0


def test_get_hourly_forecast_mocked(mocker):
    """Mock openmeteo + pandas and verify cloud_cover/visibility dict."""
    import numpy as np

    cloud = np.array([50.0] * 24)
    visibility = np.array([10000.0] * 24)
    mock_resp = _make_openmeteo_mock(hourly_values=[cloud, visibility])
    mock_client = Mock()
    mock_client.weather_api.return_value = [mock_resp]
    mocker.patch(
        "src.api.openmeteo_requests.Client", return_value=mock_client
    )
    result = get_hourly_forecast(36.0, -122.0, 1)
    assert "cloud_cover" in result
    assert "visibility" in result
    assert isinstance(result["cloud_cover"], float)
    assert isinstance(result["visibility"], float)


def test_get_coordinates_valid_mocked(mocker):
    """Mock geopy Nominatim with a valid location."""
    mock_location = Mock()
    mock_location.latitude = 36.97
    mock_location.longitude = -122.03
    mock_location.raw = {"name": "Santa Cruz"}

    mock_geocoder = Mock()
    mock_geocoder.geocode.return_value = mock_location
    mocker.patch(
        "src.api.Nominatim", return_value=mock_geocoder
    )
    result = get_coordinates(["loc=santa_cruz"])
    assert result == [36.97, -122.03, "Santa Cruz"]


def test_get_coordinates_invalid_falls_back(mocker):
    """Invalid location falls back to default_location."""
    mock_geocoder = Mock()
    mock_geocoder.geocode.return_value = None
    mocker.patch("src.api.Nominatim", return_value=mock_geocoder)
    mocker.patch(
        "src.api.default_location",
        return_value=["40.0", "-74.0", "Default City"],
    )
    result = get_coordinates(["loc=xyznonexistent"])
    assert result == ["40.0", "-74.0", "Default City"]


def test_get_coordinates_no_location_arg(mocker):
    """No loc= arg calls default_location."""
    mocker.patch(
        "src.api.default_location",
        return_value=["40.0", "-74.0", "Default City"],
    )
    result = get_coordinates(["hide_wave", "json"])
    assert result == ["40.0", "-74.0", "Default City"]


def test_get_uv_value_error_returns_no_data(mocker):
    """get_uv returns 'No data' when ValueError is raised."""
    mock_client = Mock()
    mock_client.weather_api.side_effect = ValueError("bad coords")
    mocker.patch(
        "src.api.openmeteo_requests.Client", return_value=mock_client
    )
    result = get_uv(999, 999, 1)
    assert result == "No data"


def test_ocean_information_value_error_returns_no_data(mocker):
    """ocean_information returns 'No data' when ValueError is raised."""
    mock_client = Mock()
    mock_client.weather_api.side_effect = ValueError("bad coords")
    mocker.patch(
        "src.api.openmeteo_requests.Client", return_value=mock_client
    )
    result = ocean_information(999, 999, 1)
    assert result == "No data"
