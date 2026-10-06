#!/usr/bin/env python
"""Fetch latitude and longitude for real cities using geopy."""

import time

import pandas as pd
from geopy.geocoders import Nominatim

DEFAULT_CITIES = [
    "New York, NY",
    "Knoxville, TN",
    "Birmingham, AL",
    "Baltimore, MD",
    "Bangor, ME",
    "Cleveland, OH",
    "Chicago, IL",
    "Denver, CO",
    "Los Angeles, CA",
    "San Francisco, CA",
    "Raleigh, NC",
    "Seattle, WA",
    "Boston, MA",
    "Houston, TX",
    "Dallas, TX",
    "Miami, FL",
    "Atlanta, GA",
    "Fort Worth, TX",
    "Phoenix, AZ",
    "San Diego, CA",
]

# In-memory cache so repeated runs in one process do not re-query the service.
_CACHE = {}


def get_lat_long(city_names):
    """Return a list of (city, latitude, longitude) tuples using Nominatim.

    Nominatim allows roughly one request per second, so we pause between
    real queries. Cached cities are returned instantly.
    """
    geolocator = Nominatim(user_agent="heuristics-tsp")
    rows = []
    for name in city_names:
        if name not in _CACHE:
            location = geolocator.geocode(name)
            if location is None:
                raise ValueError(f"Could not find a location for city: {name}")
            _CACHE[name] = (location.latitude, location.longitude)
            time.sleep(1)
        latitude, longitude = _CACHE[name]
        rows.append((name, latitude, longitude))
    return rows


def create_cities_dataframe(city_names=None):
    """Create a pandas DataFrame with columns city, latitude, longitude.

    Uses DEFAULT_CITIES when no list is given.
    """
    if city_names is None:
        city_names = DEFAULT_CITIES
    rows = get_lat_long(city_names)
    return pd.DataFrame(rows, columns=["city", "latitude", "longitude"])


def cities_from_args(*names):
    """Return a clean list of city names from variable-length arguments.

    Strips whitespace, drops empty strings, and removes duplicates while
    keeping the original order.
    """
    cleaned = []
    for name in names:
        name = name.strip()
        if name and name not in cleaned:
            cleaned.append(name)
    return cleaned
