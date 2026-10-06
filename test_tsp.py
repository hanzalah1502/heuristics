"""Offline tests: no geocoding or internet access required."""

import random

import pandas as pd
import pytest
from click.testing import CliRunner

import fetch_cities
import tsp_pandas
from fetch_cities import cities_from_args, create_cities_dataframe
from tsp_pandas import cli, run_simulations, tsp

SMALL_CITIES = [
    ("Boston", 42.3601, -71.0589),
    ("Chicago", 41.8781, -87.6298),
    ("Denver", 39.7392, -104.9903),
    ("Miami", 25.7617, -80.1918),
    ("Seattle", 47.6062, -122.3321),
]


@pytest.fixture(name="small_df")
def small_df_fixture():
    """A small hardcoded cities DataFrame."""
    return pd.DataFrame(SMALL_CITIES, columns=["city", "latitude", "longitude"])


def test_cities_from_args_cleans_input():
    result = cities_from_args(" Boston ", "", "Chicago", "Boston")
    assert result == ["Boston", "Chicago"]


def test_create_cities_dataframe_columns(monkeypatch):
    monkeypatch.setattr(fetch_cities, "get_lat_long", lambda names: SMALL_CITIES)
    df = create_cities_dataframe(["Boston"])
    assert list(df.columns) == ["city", "latitude", "longitude"]
    assert len(df) == len(SMALL_CITIES)


def test_tsp_visits_every_city_once(small_df):
    distance, route = tsp(small_df, random.Random(1))
    assert sorted(route) == sorted(small_df["city"])
    assert distance > 0


def test_run_simulations_returns_best(small_df):
    best_distance, best_route = run_simulations(small_df, 20, seed=7)
    rng = random.Random(7)
    all_distances = [tsp(small_df, rng)[0] for _ in range(20)]
    assert best_distance == pytest.approx(min(all_distances))
    assert len(best_route) == len(small_df)


def test_run_simulations_rejects_zero_count(small_df):
    with pytest.raises(ValueError):
        run_simulations(small_df, 0)


def test_cli_simulate(monkeypatch, small_df):
    monkeypatch.setattr(tsp_pandas, "create_cities_dataframe", lambda *a: small_df)
    result = CliRunner().invoke(cli, ["simulate", "--count", "3", "--seed", "1"])
    assert result.exit_code == 0
    assert "Shortest distance found" in result.output


def test_cli_custom_needs_two_cities(monkeypatch, small_df):
    monkeypatch.setattr(tsp_pandas, "create_cities_dataframe", lambda *a: small_df)
    result = CliRunner().invoke(cli, ["custom", "Boston"])
    assert result.exit_code != 0


def test_cli_custom(monkeypatch, small_df):
    monkeypatch.setattr(tsp_pandas, "create_cities_dataframe", lambda *a: small_df)
    result = CliRunner().invoke(
        cli, ["custom", "Boston", "Chicago", "--count", "2", "--seed", "1"]
    )
    assert result.exit_code == 0
    assert "Route to follow" in result.output
