# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hydrodynamic flood simulation of the Sullivans Creek catchment (ACT, Australia) using [ANUGA](https://github.com/anuga-community/anuga_core) — a shallow water equation solver. Models rainfall-runoff under various storm events (1%, 2%, 5%, 10%, 20%, 50% AEP and 500-year return periods).

## Running Simulations

Single-process (development/testing):
```bash
python run_sullivans_test.py
python run_sullivans.py
```

Parallel MPI execution (production):
```bash
mpirun -np 12 python run_PAR_Sullivans_Test.py
```

There is no formal test suite or build system. Simulation output is written as SWW (Shallow Water Wave) and NetCDF files.

## Script Inventory

| Script | Purpose |
|--------|---------|
| `run_sullivans.py` | Primary production simulation |
| `run_PAR_Sullivans_Test.py` | Parallel MPI variant |
| `run_sullivans_with_rain.py` | Rainfall-driven variant |
| `run_sullivans_construction.py` | Variant with construction site modifications |
| `run_sullivans_test.py` | Lightweight test run |
| `sullivans.py` | Polygon/shapefile configuration (shared across all run scripts) |
| `model_build_tools_04.py` | Utility functions for mesh, roughness, and structure setup |
| `bom_file_utils.py` | Reader for BOM radar rainfall NetCDF files |
| `diagnostic.py` | Post-processing utilities |

## Architecture

All `run_*.py` scripts follow the same structure:

1. **Mesh generation** — triangular mesh from DEM (`01_DEM/`) and polygon refinement zones (`02_POLYS/`); ~618,822 triangles at ~75–2000 m² resolution.
2. **Domain setup** — elevation, stage (initial water level 558.0 m), Manning's roughness (0.0452 base).
3. **Boundary conditions** — reflective walls and Dirichlet inflow/outflow.
4. **Operators** — `Rate_operator` for rainfall, `Inlet_operator` for drainage structures, `Boyd_box_culvert_operator` for culverts/bridges.
5. **Riverwalls** — Barry Embankment and Gods Embankment modelled as elevated barriers.
6. **Evolution** — 8-hour simulation (28,800 s) with 5-minute yield steps; outputs SWW file.

Shared configuration lives in `sullivans.py` (17+ named polygons for water bodies, structures, banks) and `model_build_tools_04.py` (friction tables, building footprint integration).

## Key Data Directories

| Directory | Contents |
|-----------|----------|
| `01_DEM/` | Digital Elevation Model rasters |
| `02_POLYS/` | Mesh refinement polygons and interior holes |
| `03_FORCEFUNC/` | Rainfall forcing functions (CSV/NetCDF) |
| `04_RAINFALL/` | BOM radar rainfall fields (2010–2012, `rainfields_rudy.vandrie_ndrp_act_20130909/`) plus sample `.pts`/`.asc` outputs |
| `05_SHAPEFILES/` | Creek centrelines, bridge outlines, bank polygons |
| `07_CSVFILES/` | Polygon/feature CSVs (creek, bridge, bank outlines) exported from the shapefiles |
| `culverts-bridges/` | Culvert geometry and reference data (MapInfo `.mid`/`.mif`, survey TIFs under `sullivans_data/`) |
| `2018-Flood/` | Reference imagery and BOM rainfall IFD data for the Feb 2018 flood event |

## Spatial Reference

UTM Zone 55 South:
- Easting: 689,801 – 700,200 m
- Northing: 6,091,501 – 6,104,600 m
