# SN5 Telemetry Site — Technical Write-Up

## Overview

This project is a web application for Formula Electric at Berkeley. Featuring uploading and analyzing CSV telemetry data logged from the SN5 racecar's CAN bus (signals like `IVTVoltage2`, `bms_state`, `M192_Command_Message`, and `wss_rear_data`). It supports uploading logs, browsing past uploads, charting any signal, and automatically flagging statistically significant data points within a run.

## System Design

The application is split into three independent parts: a frontend, a backend, and a database.

```
Browser
  │
  ▼
SvelteKit application (frontend + backend, but run as two services)
  ├── UI routes (Svelte pages, upload form, charts)
  └── API endpoints (FastAPI, in Python)
         │
         ├──► File storage (raw CSVs on disk)
         └──► Database (SQLite)
```

The frontend and backend are two separate running processes that communicate over HTTP (the frontend calls the backend's API with `fetch`).

## What Frontend Framework Did We Use, and Why?

**SvelteKit**, with TypeScript. This matches the team's existing tooling for other internal tools. Svelte compiles components to lightweight vanilla JavaScript at build time, which keeps chart-heavy pages responsive. SvelteKit adds file-based routing and a dev/build pipeline on top of Svelte itself. TypeScript was enabled to help catch mismatches between what the backend returns and what the frontend expects, since the two are developed as separate codebases.

## What Backend Framework Did We Use, and Why?

**FastAPI**, in Python, run as a separate service from the frontend. The alternative considered was using SvelteKit's own backend capability (`+server.ts` routes), which would have kept everything in one language and avoided needing CORS configuration. Python was chosen instead because automatically identifying significant data points in telemetry depends heavily on pandas and numpy, which is much harder in the JavaScript ecosystem. Since the analytics is the most important part of the assignment, the backend was built where that tooling lives, accepting the added complexity of running two services and configuring CORS as a worthwhile trade-off.

## How Did We Store the Data, and Why?

Two separate stores, each doing a different job:

- **Raw files on disk** (`back_end/uploads/`) — every uploaded CSV is saved unmodified. This keeps a recoverable original in case parsing logic ever needs to be revisited or debugged.
- **SQLite database** (`telemetry.db`) — two tables:
    - `runs`: one row per upload (filename, upload timestamp).
    - `signals`: one row per individual signal reading (run ID, timestamp, CAN bus, CAN ID, signal name, raw value, and decoded label where applicable — e.g. `bms_state` value `1.0` decodes to `"BMS_STATE_LV_POWER"`).

This design (one row per signal reading, rather than one column per signal) was chosen because CAN logs don't have a fixed set of columns and different runs can log different signals. Storing data this way keeps the schema flexible and makes querying by signal name or time range straightforward regardless of what a given upload contains.

SQLite specifically was chosen for zero setup, since the whole application runs on a single machine during development, and it handled a real test upload of ~1.46 million rows.

## What Tools Did We Use to Graph the Data?

**Chart.js**, rendering line charts of a selected signal's value over time. It was chosen over alternatives (D3, uPlot) primarily for development speed given the project timeline. It has a simple, well-documented API that got a working chart on screen quickly. The trade-off is that it involves writing less of the charting logic by hand compared to a lower-level library like D3, which would have taught more about how axes and scales work internally, at the cost of significantly more development time.

## Data Analytics

Two analytics endpoints were built on top of the stored signal data:

- **`/stats`** — returns count, min, max, mean, and standard deviation for a given signal in a given run, computed with pandas.
- **`/anomalies`** — flags individual data points as significant using a z-score: `(value - mean) / std`. Points with an absolute z-score beyond a threshold (default 2.0 standard deviations) are returned as anomalies. This is a standard approach to outlier detection, roughly 95% of normally-distributed data falls within ±2 standard deviations, so points beyond that are statistically unusual for that signal.

## Hypothetical Cloud Deployment

If deployed to the cloud rather than run locally:

- **Frontend and backend** would each run as their own service (e.g. on Fly.io or Render), since they're already built as independent processes.
- **Raw CSV storage** would move from local disk to an object store like Amazon S3, for durability beyond a single machine.
- **SQLite** would either remain as-is for a single-instance deployment, or be upgraded to a managed Postgres database if multiple concurrent users/writers were expected.
- **CI/CD** via GitHub Actions to build and deploy on push.

## Known Limitations / Not Yet Implemented

- `structure.json` (CAN message and signal metadata, including physical units) is not yet integrated — the UI currently shows raw signal values without units.
- No upload de-duplication. Re-uploading the same file creates a new, separate run rather than being detected as a duplicate.
- Minimal UI styling, in line with the project's stated priority on understanding over polish.

## GitHub Link
<https://github.com/jiachengw-sf/feb_fa26_cs.git>

## Demo Video
<https://youtu.be/0UwZOr9SnRk>