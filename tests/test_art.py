"""
QA tests for art.py
Make sure pytest is installed: pip install pytest
Run pytest: pytest
"""

import io
import sys

import pytest

from src import art


def test_print_wave():
    """
    Testing the print_wave() function
    Uses sys & io to capture printed output
    """
    # Capture the output
    captured_output = io.StringIO()  # Create StringIO object
    sys.stdout = captured_output  # Redirect stdout.

    # Call the function
    # Color is invalid, should default to blue
    art.print_wave(1, 0, "sdfsd")

    # Reset redirect.
    sys.stdout = sys.__stdout__

    # Now captured_output.getvalue() contains the printed content
    output = captured_output.getvalue()

    # Perform assertions based on expected output
    assert "[0;34m" in output, "Blue color code not found in output"
    assert output, "print_wave() did not print anything"


def test_print_wave_valid_color():
    """Valid color produces output with the correct ANSI code."""
    captured = io.StringIO()
    sys.stdout = captured
    art.print_wave(1, 0, "red")
    sys.stdout = sys.__stdout__
    output = captured.getvalue()
    assert art.colors["red"] in output
    assert art.colors["end"] in output


def test_print_large_wave():
    """show_large_wave=1 prints the braille art."""
    captured = io.StringIO()
    sys.stdout = captured
    art.print_wave(0, 1, "blue")
    sys.stdout = sys.__stdout__
    output = captured.getvalue()
    assert len(output) > 100, "Large wave art should be substantial"
    assert art.colors["blue"] in output


def test_print_wave_hidden():
    """show_wave=0 and show_large_wave=0 prints nothing."""
    captured = io.StringIO()
    sys.stdout = captured
    art.print_wave(0, 0, "blue")
    sys.stdout = sys.__stdout__
    output = captured.getvalue()
    assert output == ""


@pytest.mark.parametrize(
    "color_name",
    [
        "red",
        "green",
        "yellow",
        "blue",
        "purple",
        "teal",
        "white",
        "bold_red",
    ],
)
def test_print_wave_all_colors(color_name):
    """All valid color names produce output."""
    captured = io.StringIO()
    sys.stdout = captured
    art.print_wave(1, 0, color_name)
    sys.stdout = sys.__stdout__
    output = captured.getvalue()
    assert len(output) > 0
    assert art.colors[color_name] in output
