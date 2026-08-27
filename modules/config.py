import os
from pathlib import Path

# API Configuration - Reads from environment variable or defaults to empty (triggers Open-Meteo fallback)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Cities to monitor
INDIA_CITIES = {
    "Mumbai":      {"lat": 19.0760, "lon": 72.8777, "state": "Maharashtra",      "tier": "Metro"},
    "Delhi":       {"lat": 28.6139, "lon": 77.2090, "state": "Delhi",            "tier": "Metro"},
    "Bangalore":   {"lat": 12.9716, "lon": 77.5946, "state": "Karnataka",        "tier": "Metro"},
    "Chennai":     {"lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu",       "tier": "Metro"},
    "Kolkata":     {"lat": 22.5726, "lon": 88.3639, "state": "West Bengal",      "tier": "Metro"},
    "Hyderabad":   {"lat": 17.3850, "lon": 78.4867, "state": "Telangana",        "tier": "Metro"},
    "Pune":        {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra",      "tier": "Tier-1"},
    "Ahmedabad":   {"lat": 23.0225, "lon": 72.5714, "state": "Gujarat",          "tier": "Tier-1"},
    "Jaipur":      {"lat": 26.9124, "lon": 75.7873, "state": "Rajasthan",        "tier": "Tier-1"},
    "Lucknow":     {"lat": 26.8467, "lon": 80.9462, "state": "Uttar Pradesh",    "tier": "Tier-1"},
}

# Strike keywords
STRIKE_KEYWORDS = [
    "transport strike", "bus strike", "truck strike",
    "auto strike", "taxi strike", "rail strike",
    "railway strike", "lorry strike", "driver strike",
    "bandh", "hartal", "chakka jam",
    "bharat bandh", "road blockade",
]

# Paths - Supports Databricks Workspace and standalone execution
import os
DATABRICKS_WORKSPACE = Path("/Workspace/Users/ayyash.a@tcs.com/O2C_AI")

if DATABRICKS_WORKSPACE.exists() or "DATABRICKS_RUNTIME_VERSION" in os.environ:
    _project_root = DATABRICKS_WORKSPACE
else:
    try:
        _module_dir = Path(__file__).resolve().parent
        _project_root = _module_dir.parent
    except NameError:
        _project_root = DATABRICKS_WORKSPACE

BASE_DIR = _project_root / "india_monitor_data"
DB_PATH = BASE_DIR / "database" / "india_monitor.db"
RAG_DIR = BASE_DIR / "rag"
DOCS_DIR = RAG_DIR / "documents"
VECTOR_DIR = RAG_DIR / "vector_store"
CHUNKS_DIR = RAG_DIR / "chunks"
LOG_DIR = BASE_DIR / "logs"

# RAG settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5

# Alert thresholds
ALERT_THRESHOLDS = {
    "rain_mm_per_hr": 20,
    "temp_extreme_c": 42,
    "wind_ms": 15,
    "visibility_km": 1,
}

CSV_DIR = BASE_DIR / "csv_exports"
INPUT_FILES_DIR = _project_root / "Input Files"
JSON_DIR = BASE_DIR / "json_exports"
PROCESSED_DIR = RAG_DIR / "processed"

# Create directories
for d in [DB_PATH.parent, RAG_DIR, DOCS_DIR, VECTOR_DIR, CHUNKS_DIR, PROCESSED_DIR, LOG_DIR, CSV_DIR, JSON_DIR]:
    d.mkdir(parents=True, exist_ok=True)