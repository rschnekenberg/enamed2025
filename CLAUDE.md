# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Streamlit dashboard for exploring ENADE Medicina 2025 data (Brazilian national higher education exam results for Medicine courses). Features:
- Interactive scatter plot (participants vs proficiency) with filters for UF, administrative category, and participant count
- Interactive map of Brazil showing institution locations colored by proficiency percentage

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application locally
streamlit run app.py

# Generate coordinates (if coordinates.json is missing)
# Run the geocoding script manually - takes ~4 minutes due to API rate limits
```

## Architecture

Single-file Streamlit application (`app.py`) with:
- Data loading from `conceito-enade-2025-medicina.xlsx`
- Pre-computed geocoding coordinates in `coordinates.json`
- Section 1: Scatter plot with multi-select filters and color-by options
- Section 2: Mapbox scatter map with color scale controls

## Key Files

- `app.py` - Main Streamlit application
- `conceito-enade-2025-medicina.xlsx` - Source ENADE data
- `coordinates.json` - Pre-computed lat/lon for each municipality
- `requirements.txt` - Python dependencies

## Data Columns (renamed internally)

- `nome_ies` - Institution name
- `municipio` / `uf` - Location
- `categoria` - Administrative category (public/private)
- `n_participantes` - Number of participating graduates
- `pct_proficiencia` - Proficiency percentage (0-1 scale)
- `conceito_enade` - ENADE score band

## Deployment

Deploy to Streamlit Community Cloud:
1. Push to GitHub
2. Go to share.streamlit.io
3. Connect repo and select `app.py`
