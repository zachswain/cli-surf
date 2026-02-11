"""
QA tests for helper.py
Make sure pytest is installed: pip install pytest
Run pytest: pytest
"""

import io
from datetime import datetime
from unittest.mock import patch

from src import cli, helper
from src.helper import set_output_values


def test_invalid_input():
    """
    Test if decimal input prints proper invalid input message
    """
    with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
        helper.extract_decimal(["decimal=NotADecimal"])
        printed_output = fake_stdout.getvalue().strip()
        expected = "Invalid value for decimal. Please provide an integer."
        assert printed_output == expected


def test_default_input():
    """
    Test that when no decimal= in args, 1 is the default
    """
    decimal = helper.extract_decimal([])
    assert 1 == decimal


def test_json_output():
    """
    Passing "JSON" as an argument to cli.run,
    we check if a JSON object returns.
    We also check for expected outputs,
    like a lat that is a float/int
    """
    # Hardcode lat and long for location.
    # If not, when test are ran in Github Actions
    # We get an error(because server probably isn't near ocean)
    json_output = cli.run(36.95, -121.97, ["", "json"])
    assert type(json_output["Lat"]) in {int, float}
    assert isinstance(json_output["Location"], str)


def test_print_gpt():
    """
    Tests the simple_gpt()
    """
    surf_data = {
        "Location": "test",
        "Height": "test",
        "Swell Direction": "test",
        "Period": "test",
        "Unit": "test",
    }
    gpt_prompt = "Please output 'gpt works'"
    gpt_info = [None, ""]
    gpt_response = helper.print_gpt(surf_data, gpt_prompt, gpt_info)
    assert "gpt works" in gpt_response


def test_set_output_values_show_past_uv():
    args = ["show_past_uv"]
    arguments_dictionary = {}
    expected = {"show_past_uv": 1}
    result = set_output_values(args, arguments_dictionary)
    assert result == expected


def test_set_output_values_hide_past_uv():
    args = ["hide_past_uv"]
    arguments_dictionary = {}
    expected = {"show_past_uv": 0}
    result = set_output_values(args, arguments_dictionary)
    assert result == expected


def test_set_output_values_show_height_history():
    args = ["show_height_history"]
    arguments_dictionary = {}
    expected = {"show_height_history": 1}
    result = set_output_values(args, arguments_dictionary)
    assert result == expected


def test_set_output_values_hide_height_history():
    args = ["hide_height_history"]
    arguments_dictionary = {}
    expected = {"show_height_history": 0}
    result = set_output_values(args, arguments_dictionary)
    assert result == expected


def test_set_output_values_show_direction_history():
    args = ["show_direction_history"]
    arguments_dictionary = {}
    expected = {"show_direction_history": 1}
    result = set_output_values(args, arguments_dictionary)
    assert result == expected


def test_set_output_values_hide_direction_history():
    args = ["hide_direction_history"]
    arguments_dictionary = {}
    expected = {"show_direction_history": 0}
    result = set_output_values(args, arguments_dictionary)
    assert result == expected


def test_set_output_values_show_period_history():
    args = ["show_period_history"]
    arguments_dictionary = {}
    expected = {"show_period_history": 1}
    result = set_output_values(args, arguments_dictionary)
    assert result == expected


def test_set_output_values_hide_period_history():
    args = ["hide_period_history"]
    arguments_dictionary = {}
    expected = {"show_period_history": 0}
    result = set_output_values(args, arguments_dictionary)
    assert result == expected


def test_set_output_values_combined_arguments():
    args = [
        "show_past_uv",
        "show_height_history",
        "show_direction_history",
        "show_period_history",
    ]
    arguments_dictionary = {}
    expected = {
        "show_past_uv": 1,
        "show_height_history": 1,
        "show_direction_history": 1,
        "show_period_history": 1,
    }
    result = set_output_values(args, arguments_dictionary)
    assert result == expected


def test_round_decimal():
    # Standard rounding
    rounded = helper.round_decimal([2.4345, 30.2789], 2)
    assert rounded == [2.43, 30.28]

    # Empty input
    assert helper.round_decimal([], 2) == []

    # Rounding to zero decimals
    assert helper.round_decimal([2.5, 3.7, -1.2], 0) == [2.0, 4.0, -1.0]

    # Midpoint values
    # Depending on rounding method
    assert helper.round_decimal([2.5], 0) in ([2.0], [3.0])
    # Depending on rounding method
    assert helper.round_decimal([2.45], 1) in ([2.4], [2.5])

    # Negative numbers
    assert helper.round_decimal([-2.555, -3.444], 2) == [-2.56, -3.44]

    # Integer inputs
    assert helper.round_decimal([1, 2, 3], 2) == [1.0, 2.0, 3.0]


def test_print_location_show_city_false():
    with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
        helper.print_location("Not a City", 0)
        output = fake_stdout.getvalue()
        assert not output.strip()


def test_get_forecast_days_valid():
    FORECAST_DAYS = 3
    args = ["forecast=3"]
    assert helper.get_forecast_days(args) == FORECAST_DAYS


def test_get_forecast_days_default():
    assert helper.get_forecast_days([]) == 0


# ---- New tests below ----


def test_seperate_args_multiple():
    """Multiple comma-separated args are split correctly."""
    result = helper.seperate_args(["script", "loc=sc,hide_wave,json"])
    assert result == ["loc=sc", "hide_wave", "json"]


def test_seperate_args_single():
    """Single arg without commas returns a one-element list."""
    result = helper.seperate_args(["script", "json"])
    assert result == ["json"]


def test_seperate_args_empty():
    """No args returns empty list."""
    result = helper.seperate_args(["script"])
    assert result == []


def test_set_location():
    """Returns (city, lat, long) tuple."""
    location = {"city": "Santa Cruz", "lat": 36.97, "long": -122.03}
    city, lat, long = helper.set_location(location)
    assert city == "Santa Cruz"
    assert lat == 36.97
    assert long == -122.03


def test_arguments_dictionary_defaults():
    """Default arguments are set when no CLI args provided."""
    args = []
    result = helper.arguments_dictionary(36.0, -122.0, "TestCity", args)
    assert result["lat"] == 36.0
    assert result["long"] == -122.0
    assert result["city"] == "TestCity"
    assert result["show_wave"] == 1
    assert result["unit"] == "imperial"
    assert result["decimal"] == 1
    assert result["forecast_days"] == 0
    assert result["color"] == "blue"


def test_arguments_dictionary_with_overrides():
    """CLI args override defaults."""
    args = ["hide_wave", "metric", "forecast=3", "color=red", "decimal=2"]
    result = helper.arguments_dictionary(36.0, -122.0, "TestCity", args)
    assert result["show_wave"] == 0
    assert result["unit"] == "metric"
    assert result["forecast_days"] == 3
    assert result["color"] == "red"
    assert result["decimal"] == 2


def test_get_color_default():
    """Default color is blue."""
    assert helper.get_color([]) == "blue"


def test_get_color_with_color_arg():
    """color= arg returns specified color."""
    assert helper.get_color(["color=red"]) == "red"


def test_get_color_with_c_shorthand():
    """c= shorthand returns specified color."""
    assert helper.get_color(["c=green"]) == "green"


def test_get_forecast_days_fc_shorthand():
    """fc= shorthand is recognized."""
    assert helper.get_forecast_days(["fc=5"]) == 5


def test_get_forecast_days_out_of_range():
    """Out-of-range value (>7) returns 0."""
    with patch("sys.stdout", new=io.StringIO()):
        result = helper.get_forecast_days(["forecast=10"])
    assert result == 0


def test_get_forecast_days_negative():
    """Negative value returns 0."""
    with patch("sys.stdout", new=io.StringIO()):
        result = helper.get_forecast_days(["forecast=-1"])
    assert result == 0


def test_print_location_show_city_true():
    """show_city=1 prints the location."""
    with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
        helper.print_location("Santa Cruz", 1)
        output = fake_stdout.getvalue()
        assert "Santa Cruz" in output


def test_print_ocean_data_all_shown(sample_ocean_data_dict):
    """When all show flags are 1, all data lines print."""
    args = {
        "show_uv": 1,
        "show_past_uv": 1,
        "show_height": 1,
        "show_direction": 1,
        "show_period": 1,
        "show_height_history": 1,
        "show_direction_history": 1,
        "show_period_history": 1,
        "show_air_temp": 1,
        "show_wind_speed": 1,
        "show_wind_direction": 1,
        "show_rain_sum": 1,
        "show_precipitation_prob": 1,
        "show_cloud_cover": 1,
        "show_visibility": 1,
    }
    with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
        helper.print_ocean_data(args, sample_ocean_data_dict)
        output = fake_stdout.getvalue()
    assert "UV index:" in output
    assert "Wave Height:" in output
    assert "Wave Direction:" in output
    assert "Wave Period:" in output
    assert "Wind Speed:" in output


def test_print_ocean_data_all_hidden(sample_ocean_data_dict):
    """When all show flags are 0, nothing prints."""
    args = {
        "show_uv": 0,
        "show_past_uv": 0,
        "show_height": 0,
        "show_direction": 0,
        "show_period": 0,
        "show_height_history": 0,
        "show_direction_history": 0,
        "show_period_history": 0,
        "show_air_temp": 0,
        "show_wind_speed": 0,
        "show_wind_direction": 0,
        "show_rain_sum": 0,
        "show_precipitation_prob": 0,
        "show_cloud_cover": 0,
        "show_visibility": 0,
    }
    with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
        helper.print_ocean_data(args, sample_ocean_data_dict)
        output = fake_stdout.getvalue()
    assert output == ""


def test_print_forecast_one_day():
    """Prints one day of forecast data."""
    ocean = {
        "forecast_days": 1,
        "show_date": 1,
        "show_uv": 0,
        "show_height": 1,
        "show_direction": 0,
        "show_period": 0,
        "show_air_temp": 0,
        "show_rain_sum": 0,
        "show_precipitation_prob": 0,
        "show_wind_speed": 0,
        "show_wind_direction": 0,
        "decimal": 1,
    }
    forecast = {
        "date": [datetime(2025, 1, 1)],
        "wave_height_max": [4.56],
        "wave_direction_dominant": [210.0],
        "wave_period_max": [12.0],
        "uv_index_max": [5.3],
        "temperature_2m_max": [68.0],
        "temperature_2m_min": [55.0],
        "rain_sum": [0.0],
        "precipitation_probability_max": [10.0],
        "wind_speed_10m_max": [12.0],
        "wind_direction_10m_dominant": [270.0],
    }
    with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
        helper.print_forecast(ocean, forecast)
        output = fake_stdout.getvalue()
    assert "Wave Height:" in output
    assert "4.6" in output  # rounded to 1 decimal


def test_forecast_to_json():
    """Returns list of dicts with correct keys and rounding."""
    forecast_data = {
        "date": [datetime(2025, 1, 1)],
        "wave_height_max": [4.567],
        "wave_direction_dominant": [210.123],
        "wave_period_max": [12.456],
        "uv_index_max": [5.789],
        "temperature_2m_max": [68.123],
        "temperature_2m_min": [55.456],
        "rain_sum": [0.123],
        "precipitation_probability_max": [10.789],
        "wind_speed_10m_max": [12.345],
        "wind_direction_10m_dominant": [270.678],
    }
    result = helper.forecast_to_json(forecast_data, 1)
    assert isinstance(result, list)
    assert len(result) == 1
    day = result[0]
    assert "surf height" in day
    assert "swell direction" in day
    assert "swell period" in day
    assert day["surf height"] == 4.6
    assert day["swell direction"] == 210.1


def test_surf_summary():
    """Returned string contains location, height, direction, period."""
    surf_data = {
        "Location": "Santa Cruz",
        "Height": 4.5,
        "Swell Direction": 210,
        "Period": 12,
        "Unit": "imperial",
    }
    result = helper.surf_summary(surf_data)
    assert "Santa Cruz" in result
    assert "4.5" in result
    assert "210" in result
    assert "12" in result
