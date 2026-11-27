"""
tests/conftest.py
Shared test setup: pytest runs this automatically before every test.
"""

import pytest

from modules.csp import reset_reservations


@pytest.fixture(autouse=True)
def fresh_reservations():
    """Start every test with only the sample reservations, so bookings made
    by one test can never change the result of another test."""
    reset_reservations()
    yield
