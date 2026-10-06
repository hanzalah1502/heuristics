#!/usr/bin/env python
"""Command-line tool that finds a short route visiting all cities in a list.

Heuristic: pick a random starting city, then always travel to the nearest
unvisited city (greedy). Repeat many times and keep the shortest route.
"""

import random
from functools import lru_cache

import click
from geopy.distance import geodesic

from fetch_cities import cities_from_args, create_cities_dataframe


@lru_cache(maxsize=None)
def distance_between(point_a, point_b):
    """Return the geodesic distance in miles between two (lat, long) tuples."""
    return geodesic(point_a, point_b).miles


def tsp(df, rng=None):
    """Run one random-start greedy simulation.

    Returns (total_distance_in_miles, route) where route is the ordered list
    of city names. The total includes the trip back to the starting city.
    """
    rng = rng or random.Random()
    cities = [
        (row.city, (row.latitude, row.longitude)) for row in df.itertuples(index=False)
    ]
    rng.shuffle(cities)

    current = cities[0]
    unvisited = cities[1:]
    route = [current[0]]
    total = 0.0

    while unvisited:
        nearest = min(unvisited, key=lambda c: distance_between(current[1], c[1]))
        total += distance_between(current[1], nearest[1])
        unvisited.remove(nearest)
        route.append(nearest[0])
        current = nearest

    # Return leg to the starting city.
    start_point = cities[0][1]
    total += distance_between(current[1], start_point)
    return total, route


def run_simulations(df, count, seed=None):
    """Run the simulation `count` times and return the shortest result."""
    if count < 1:
        raise ValueError("count must be at least 1")
    rng = random.Random(seed)
    best_distance = None
    best_route = None
    for run in range(1, count + 1):
        distance, route = tsp(df, rng)
        click.echo(f"Simulation {run}: {distance:,.0f} miles starting in {route[0]}")
        if best_distance is None or distance < best_distance:
            best_distance, best_route = distance, route
    return best_distance, best_route


def report(best_distance, best_route):
    """Print the best route found."""
    click.echo(f"\nShortest distance found: {best_distance:,.0f} miles")
    click.echo("Route to follow:")
    for step, city in enumerate(best_route, start=1):
        click.echo(f"  {step}. {city}")
    click.echo(f"  back to {best_route[0]}")


@click.group()
def cli():
    """Find the shortest route through cities using a random-start greedy TSP."""


@cli.command()
@click.option(
    "--count", default=10, show_default=True, type=int, help="Number of simulations."
)
@click.option("--seed", default=None, type=int, help="Seed for repeatable results.")
def simulate(count, seed):
    """Run the simulation on the default list of 20 US cities."""
    df = create_cities_dataframe()
    report(*run_simulations(df, count, seed))


@cli.command()
@click.argument("cities", nargs=-1, required=True)
@click.option(
    "--count", default=10, show_default=True, type=int, help="Number of simulations."
)
@click.option("--seed", default=None, type=int, help="Seed for repeatable results.")
def custom(cities, count, seed):
    """Run the simulation on your own cities.

    Example: ./tsp_pandas.py custom "Boston, MA" "Chicago, IL" --count 10
    """
    names = cities_from_args(*cities)
    if len(names) < 2:
        raise click.UsageError("Provide at least two different cities.")
    df = create_cities_dataframe(names)
    report(*run_simulations(df, count, seed))


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
