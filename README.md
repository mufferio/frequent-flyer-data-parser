# Frequent Flyer Data Parser

A Python-based airline simulation and data-processing project that ingests airport, customer, flight-segment, and trip datasets, builds an in-memory domain model, and visualizes booked routes on an interactive world map.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Data Model](#data-model)
- [Input Datasets](#input-datasets)
- [How the Pipeline Works](#how-the-pipeline-works)
- [Filtering and Exploration](#filtering-and-exploration)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [Validation and Quality](#validation-and-quality)
- [Known Limitations](#known-limitations)
- [Potential Improvements](#potential-improvements)

## Overview
This project models a frequent-flyer system for a fictional airline (“Python Air”). It:
- Imports raw CSV datasets
- Constructs typed Python objects (`Airport`, `Customer`, `FlightSegment`, `Trip`)
- Books customer trips onto flight segments
- Tracks status miles and frequent-flyer tiers
- Computes trip and customer costs
- Provides an interactive `pygame` + `tkinter` visualizer for route exploration

The repository appears to be coursework-style code focused on object-oriented modeling and interactive data filtering.

## Key Features
- **CSV ingestion pipeline** for airports, customers, flight segments, and trips
- **Frequent-flyer logic** including:
  - Tier thresholds (`Prestige`, `Elite-Light`, `Elite-Regular`, `Super-Elite`)
  - Cabin multipliers for status miles (`Economy`, `Business`)
  - Fare multipliers and status-based trip discounts
- **Seat booking mechanics** with class capacity constraints
- **Trip analytics** for in-flight and total elapsed time (including layovers)
- **Interactive map visualization** of all loaded flight segments
- **Real-time filtering** by customer, trip ID, date range, duration, and location

## Architecture
Core architecture is organized around domain entities plus orchestration and UI modules.

### Domain Entities
- **`Airport`** (`airport.py`)
  - Stores airport metadata and location coordinates.
- **`FlightSegment`** (`flight.py`)
  - Represents one scheduled flight leg, times, length, route endpoints, manifest, and booking state.
- **`Trip`** (`flight.py`)
  - Represents a customer itinerary composed of one or more `FlightSegment` objects.
- **`Customer`** (`customer.py`)
  - Stores profile information, trip history, total spend, status miles, and frequent-flyer status.

### Processing and Orchestration
- **`application.py`**
  - Imports CSV files, constructs domain objects, loads trips, computes summary stats, and launches visualization.

### Filtering System
- **`filter.py`**
  - Defines abstract `Filter` plus concrete implementations:
    - `ResetFilter`
    - `CustomerFilter`
    - `DurationFilter`
    - `LocationFilter`
    - `DateFilter`
    - `TripFilter`

### Visualization
- **`visualizer.py`**
  - Handles `pygame` map rendering and user interaction.
  - Uses `tkinter` popups for filter inputs and trip summaries.

## Repository Structure
```text
frequent-flyer-data-parser/
├── application.py            # Main entry point and data-loading pipeline
├── airport.py                # Airport entity
├── customer.py               # Customer entity + loyalty logic
├── flight.py                 # FlightSegment and Trip entities
├── filter.py                 # Filter classes used by the UI
├── visualizer.py             # Interactive map UI (pygame + tkinter)
├── data/
│   ├── airports.csv
│   ├── customers.csv
│   ├── segments.csv
│   ├── trips.csv
│   ├── segments_small.csv
│   └── trips_small.csv
└── images/
    └── map.png               # Background map for visualization
```

## Data Model
### Frequent Flyer Status Thresholds
Configured in `customer.py`:
- `Prestige`: 15,000 km (10% discount on future trips)
- `Elite-Light`: 30,000 km (15% discount)
- `Elite-Regular`: 50,000 km (20% discount)
- `Super-Elite`: 100,000 km (25% discount)

### Multipliers
- **Status miles multiplier** (`FREQUENT_FLYER_MULTIPLIER`):
  - Economy: `1x`
  - Business: `5x`
- **Fare multiplier** (`CLASS_MULTIPLIER`):
  - Economy: `1.0x`
  - Business: `2.5x`

### Base Fare
- Global default in `application.py`: `DEFAULT_BASE_COST = 0.1225` (per km)

## Input Datasets
The repository ships with full and reduced datasets:

- `airports.csv` (599 rows)
- `customers.csv` (2,219 rows)
- `segments.csv` (68,780 rows)
- `trips.csv` (42,046 rows)
- `segments_small.csv` (11,780 rows)
- `trips_small.csv` (7,495 rows)

### Expected Record Shapes
- **Airport row**: `IATA, Airport Name, Longitude, Latitude`
- **Customer row**: `CustomerID, Name, Age, Nationality`
- **Segment row**: `FlightID, DepIATA, ArrIATA, Date, DepTime, ArrTime, DistanceKm`
- **Trip row**: `ReservationID, CustomerID, TripDate, ItineraryLiteral...`

> Note: trip itineraries are parsed from serialized tuple-like strings (e.g., airport + cabin class sequence).

## How the Pipeline Works
1. **Import CSV logs** via `import_data(...)`.
2. **Create airports** and populate global airport location mapping.
3. **Create flight segments** indexed by departure date.
4. **Create customers** indexed by customer ID.
5. **Load trips**:
   - Parse itinerary literal
   - Match each leg to available `FlightSegment`
   - Book seats and create `Trip` objects through `Customer.book_trip(...)`
6. **Compute aggregate stats** and launch the visualizer.

## Filtering and Exploration
During visualization, keyboard shortcuts trigger filters:

- `C` → Customer filter (`customer ID`)
- `D` → Duration filter (`L####` or `G####` minutes)
- `L` → Location filter (`DXXX` for departure airport, `AXXX` for arrival airport)
- `Y` → Date filter (`YYYY-MM-DD/YYYY-MM-DD` or comma-separated)
- `T` → Trip filter (reservation ID)
- `R` → Reset all filters
- `S` → Print trip summary by reservation ID
- `Q` → Quit

## Getting Started
### Prerequisites
- Python 3.10+
- `pygame`
- `tkinter` (typically bundled with standard Python installs)

### Install dependency
```bash
pip install pygame
```

## Running the Application
From repository root:

```bash
python application.py
```

By default, `application.py` is configured to load the **small** flight/trip datasets for faster startup.

To run with full datasets, update the `import_data(...)` call in `application.py` to use:
- `data/segments.csv`
- `data/trips.csv`

## Validation and Quality
- No standalone automated test suite is currently included in the repository.
- Source files include optional `python_ta.check_all(...)` blocks under `if __name__ == '__main__':` for static-analysis-style checks when `python_ta` is installed.

## Known Limitations
- No packaged project metadata (`pyproject.toml` / `requirements.txt`) currently provided.
- No CI workflow or test harness included.
- Parsing of trip itinerary strings is custom and sensitive to malformed input.
- UI uses desktop libraries (`pygame`, `tkinter`) and is not web-based.
- Data files are expected at fixed relative paths.

## Potential Improvements
- Add formal packaging (`pyproject.toml`) and pinned dependencies.
- Introduce automated tests (unit + integration) and CI.
- Add robust schema validation for CSV inputs.
- Improve error reporting for invalid itinerary or segment matching.
- Expose a non-UI CLI mode for batch analytics.
- Add performance profiling paths for full dataset runs.

