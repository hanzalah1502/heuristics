# Traveling Salesman Heuristic (random start + greedy)

A command-line tool that finds a short route through real US cities.
City coordinates come from `geopy`, distances are geodesic miles, and each
simulation picks a random starting city, then always moves to the nearest
unvisited city (greedy). Running many simulations and keeping the shortest
route gives a good heuristic answer.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
make install
```

## Usage

Run on the 20 default cities, 10 simulations:

```bash
python tsp_pandas.py simulate --count 10
```

Run on your own cities:

```bash
python tsp_pandas.py custom "Boston, MA" "Chicago, IL" "Port Aransas, TX" --count 10
```

Add `--seed 42` to either command for repeatable results.
Geocoding needs internet access and takes about one second per city.

## Development

```bash
make format   # black
make lint     # pylint
make test     # pytest (offline, no geocoding)
make all      # install + lint + test
```

## Files

- `fetch_cities.py` - geopy geocoding and the cities DataFrame
- `tsp_pandas.py` - greedy TSP simulation and click CLI
- `test_tsp.py` - pytest tests