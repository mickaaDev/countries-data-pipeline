# Countries Data Pipeline

ETL pipeline to load countries data from REST API to PostgreSQL with interactive dashboard.

## Setup

1. Configure environment variables in `.env` file (see sample variables in `.env.example`)
2. Run `docker-compose up -d` to start PostgreSQL
3. Install dependencies: `pip install -r requirements.txt`
4. Run pipeline: `python src/load_countries.py`

## Usage

```bash
# Start database
docker-compose up -d

# Run ETL pipeline
python src/load_countries.py

# Query data
docker-compose exec postgres psql -U myuser -d mydatabase -c "SELECT * FROM countries LIMIT 5;"

# Start the dashboard (runs on http://localhost:8050)
python src/app.py