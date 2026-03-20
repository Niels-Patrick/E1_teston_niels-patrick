# FoxChess Data API

## 📌 Overview
The goal of this project is to collect, transform and store chess related data to prepare the training of an AI model, and exposes a REST/Socket‑based API to access the data. It also includes monitoring configuration for Prometheus/Grafana.

The workspace is split between the supporting scripts such as data collecting and transformation, and a Flask‑based web service.

---

## 🧱 Architecture & Components

### 🎮 Data Collection, Transformation and Loading (`src/data_processing`)
- **`webscraping.py`** – Scrapes the chess openings Wikipedia page.
- **`lichess_api.py`** – Fetches chess games data from the Lichess API.
- **`gm_files.py`** – Converts a downloaded PGN file to a JSON file.
- **`big_data`** – Manages the Cassandra database.
- **`data_from_database`** – Manages the Supabase database.
- **`data_processing_games`** – Cleans, normalizes and aggregates the collected data and stores them in JSON files.

### 🌐 Web API (`src/app/`)
A Flask application exposing endpoints for player management and authentication:
- Config/dataclass definitions (`config.py`).
- Logging infrastructure using `loguru` (`logger_manager.py`).
- Database initialization (`db_manager.py`).
- Blueprints under `src/routes/` for login, token renewal, player CRUD, user operations.
- Models and schemas using SQLAlchemy and Marshmallow (`src/models/`).

### 📊 Monitoring (`monitoring/`)
- Grafana dashboard and datasource configuration.
- Prometheus configuration file for scraping metrics.

### 🛠 Utility & Helpers
- RBAC decorators and route helpers under `src/utils/`.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- `pip` or virtualenv
- PostgreSQL instance for the API (or adjust to another SQL DB)
- A Cassandra database.
- A Supabase database.
- Docker if you plan to launch monitoring stack

### Installation
```bash
cd E1_teston_niels-patrick
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Configuration
Create a `.env` file in the project root with the following variables:
```
DB_USERNAME=...
DB_PASSWORD=...
DB_NAME=...
DB_HOST=...
DB_PORT=5432
JWT_TOKEN_LOCATION=headers
JWT_HEADER_NAME=Authorization
JWT_HEADER_TYPE=Bearer
JWT_SECRET_KEY=your_secret
FERN_KEY=<base64 key from `Fernet.generate_key()`>
HOST=0.0.0.0
PORT=5000
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_CONNECT=...
CHESS_FILE_PATH=...
FERN_KEY=...
```

### Collecting Data
Run the following scripts:
```bash
python big_data.py
python db_loading.py
python gm_files.py
python lichess_api.py
python utils.py
python webscraping.py
```

### Cleaning, Normalizing and Saving Data
Run the following scripts:
```bash
python data_processing_games.py
python db_migration.py
```

### Starting the Web API
```bash
python main.py
```
The API will run on the host/port specified in `.env`. Swagger documentation is available at `http://<host>:<port>/apidocs/`.

### API Endpoints
| Path | Method | Description |
|------|--------|-------------|
| `/api/login/` | POST, DELETE | Authenticate user and receive JWT, or delete a refresh token when logging out |
| `/api/token/refresh` | GET, POST | Check token validity and refresh access token |
| `/api/player/` | GET, POST, PUT, DELETE | List/add/update/delete players (JWT required) |
| `/api/player/<id>` | GET | Retrieve single player (JWT required) |
| `/api/user/<id>` | GET | Retrieve single user (a player is not always a registered user) (JWT required) |
| `/api/event/` | GET | Retrieve the list of events (JWT required) |
| `/api/opening/` | GET | Retrieve the list of openings (JWT required) |
| `/api/game/` | GET, POST, PUT, DELETE | List/add/update/delete games (JWT required) |

The Swagger UI provides interactive docs.

### Monitoring
Launch Prometheus and Grafana (see `monitoring/` subfolders) to visualize metrics. The Grafana Dockerfile builds a custom image with pre‑provisioned dashboards and datasources.

---

## 📂 Repository Structure
```
main.py               # entrypoint for Flask API

src/                  # Python package containing core logic
 ├─ app/              # flask application components
 ├─ data_processing/  # data processing scripts
 ├─ models/           # ORM models and schemas
 ├─ routes/           # HTTP endpoints
 └─ utils/            # helper functions and decorators

monitoring/           # Prometheus/Grafana infrastructure
requirements.txt      # Python dependencies
README.md             # this document
```