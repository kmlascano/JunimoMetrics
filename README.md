# JunimoMetrics

A cute, cosy analytics engineering MVP for Nexus Mods-style behavioural, creator, lifecycle, and download analytics.

JunimoMetrics is a one-day analytics engineering showcase that turns synthetic product event data into governed metrics, lifecycle audiences, and stakeholder-ready dashboards.

## What it demonstrates

- Synthetic product event generation
- dbt staging, intermediate, and mart models
- Data quality tests
- Metric catalogue / semantic layer
- Lifecycle audience segmentation
- Streamlit dashboard for stakeholder analytics
- Local DuckDB warehouse, designed to mirror ClickHouse-style analytical modelling

## Architecture

Synthetic CSV data → DuckDB warehouse → dbt models/tests/docs → Streamlit dashboard

## Business questions answered

1. Which games drive the most download activity?
2. Which games have the strongest download completion rate?
3. Which users fall into lifecycle audiences?
4. Which metrics are governed in the metric catalogue?

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install dbt-duckdb duckdb pandas faker streamlit plotly

python scripts/generate_data.py
cd mods_analytics
dbt seed
dbt run
dbt test
dbt docs generate

cd ../dashboard
streamlit run app.py