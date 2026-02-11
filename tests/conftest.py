"""
Shared pytest fixtures for cli-surf tests.
"""

import pytest

from src.server import create_app
from src.settings import ServerSettings


@pytest.fixture()
def flask_test_client():
    """Flask test client backed by ServerSettings defaults."""
    env = ServerSettings()
    app = create_app(env)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture()
def sample_ocean_data_dict():
    """Fully populated ocean data dict matching api.gather_data() shape."""
    return {
        "Lat": 36.95,
        "Long": -121.97,
        "Location": "Santa Cruz",
        "Height": 4.5,
        "Height one year ago": "3.2",
        "Swell Direction": 210.0,
        "Swell Direction one year ago": "195.0",
        "Period": 12.0,
        "Period one year ago": "11.0",
        "UV Index": 5.3,
        "UV Index one year ago": "4.1",
        "Air Temperature": 65.0,
        "Wind Speed": 8.5,
        "Wind Direction": 270.0,
        "Forecast": [
            {
                "date": "2025-01-01",
                "surf height": 4.5,
                "swell direction": 210.0,
                "swell period": 12.0,
                "uv index": 5.3,
                "temperature_2m_max": 68.0,
                "temperature_2m_min": 55.0,
                "rain_sum": 0.0,
                "daily_precipitation_probability": 10.0,
                "wind_speed_max": 12.0,
                "wind_direction_10m_dominant": 270.0,
            }
        ],
        "Unit": "imperial",
        "Rain Sum": 0.0,
        "Precipitation Probability Max": 10.0,
        "Cloud Cover": 25.0,
        "Visibility": 10000.0,
    }


@pytest.fixture()
def sample_arguments():
    """Fully populated arguments dict matching helper.arguments_dictionary()."""
    return {
        "lat": 36.95,
        "long": -121.97,
        "city": "Santa Cruz",
        "show_wave": 1,
        "show_large_wave": 0,
        "show_uv": 1,
        "show_past_uv": 0,
        "show_height": 1,
        "show_direction": 1,
        "show_period": 1,
        "show_height_history": 0,
        "show_direction_history": 0,
        "show_period_history": 0,
        "show_city": 1,
        "show_date": 1,
        "show_air_temp": 0,
        "show_wind_speed": 0,
        "show_wind_direction": 0,
        "json_output": 0,
        "show_rain_sum": 0,
        "show_precipitation_prob": 0,
        "unit": "imperial",
        "gpt": 0,
        "show_cloud_cover": 0,
        "show_visibility": 0,
        "decimal": 1,
        "forecast_days": 0,
        "color": "blue",
    }
