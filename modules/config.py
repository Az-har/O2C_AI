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

# Strike & Transport Disruption Keywords (Legacy domestic baseline)
STRIKE_KEYWORDS = [
    "transport strike", "bus strike", "truck strike",
    "auto strike", "taxi strike", "rail strike",
    "railway strike", "lorry strike", "driver strike",
    "bandh", "hartal", "chakka jam",
    "bharat bandh", "road blockade",
]

# Global Multimodal Disruption Search Matrix (Across All Transport Modes)
GLOBAL_DISRUPTION_QUERIES = {
    "ocean_maritime": [
        "port strike OR dockworker strike OR longshoremen strike",
        "container terminal congestion OR port vessel backlog OR berth delay",
        "container port shutdown OR shipping container terminal walkout",
    ],
    "canals_chokepoints": [
        "Suez Canal blockage OR Suez transit disruption OR Suez vessel grounding",
        "Panama Canal drought restriction OR Panama transit draft",
        "Red Sea shipping vessel attack OR Bab el Mandeb cargo ship",
        "Strait of Malacca shipping OR Rhine river low water barge halt",
    ],
    "air_freight": [
        "air cargo disruption OR cargo flight cancellation freight",
        "airport ground handler strike OR cargo handlers walkout",
        "air traffic control strike OR FAA ground delay cargo",
    ],
    "rail_freight": [
        "freight rail strike OR locomotive engineers walkout",
        "rail freight embargo OR cargo train derailment corridor",
        "intermodal rail terminal congestion OR rail cargo delay",
    ],
    "road_trucking": [
        "truckers strike OR lorry drivers strike OR owner operator protest",
        "highway blockade freight OR truck convoy border blockade",
        "diesel shortage freight OR fuel tanker drivers strike",
    ],
    "customs_border": [
        "customs officers strike OR border freight inspection delay",
        "customs IT system outage freight OR border crossing closed trucks",
    ],
    "natural_disasters": [
        "typhoon port closure OR hurricane shipping disruption OR cyclone port shutdown",
        "major flood highway closed freight OR flash flood rail line washout OR cargo terminal flooded",
        "earthquake port damage OR tsunami shipping warning OR earthquake highway bridge collapsed",
        "volcanic ash flight disruption OR volcanic ash airspace closed cargo",
        "blizzard highway closed trucks OR winter storm freight rail disruption OR mountain pass closed snow",
        "wildfire highway closure freight OR forest fire rail line halted",
        "Panama Canal drought restriction OR Rhine river low water barge halt OR Mississippi river low water shipping",
        "landslide freight highway blocked OR rockfall rail line closed corridor",
    ],
    "geopolitical_cyber": [
        "port cyberattack OR logistics ransomware terminal operating system",
        "customs IT system outage freight OR cyber attack shipping line",
        "Red Sea shipping vessel missile attack OR Bab el Mandeb drone attack cargo",
        "airspace closure war zone cargo OR naval blockade shipping lane",
    ],
    "domestic_corridors": [
        "transport strike India OR truckers strike India",
        "chakka jam highway OR road blockade freight India",
        "JNPT port strike OR Chennai port congestion OR Mundra port delay",
    ]
}

# Major Global Maritime Ports
GLOBAL_PORTS = {
    "Rotterdam": {"country": "Netherlands", "region": "Europe", "type": "Sea Port"},
    "Antwerp": {"country": "Belgium", "region": "Europe", "type": "Sea Port"},
    "Hamburg": {"country": "Germany", "region": "Europe", "type": "Sea Port"},
    "Felixstowe": {"country": "United Kingdom", "region": "Europe", "type": "Sea Port"},
    "Singapore": {"country": "Singapore", "region": "Asia", "type": "Sea Port / Transshipment Hub"},
    "Shanghai": {"country": "China", "region": "Asia", "type": "Sea Port"},
    "Ningbo": {"country": "China", "region": "Asia", "type": "Sea Port"},
    "Busan": {"country": "South Korea", "region": "Asia", "type": "Sea Port"},
    "Shenzhen": {"country": "China", "region": "Asia", "type": "Sea Port"},
    "Guangzhou": {"country": "China", "region": "Asia", "type": "Sea Port"},
    "Hong Kong": {"country": "China", "region": "Asia", "type": "Sea Port / Air Hub"},
    "Los Angeles": {"country": "United States", "region": "North America", "type": "Sea Port"},
    "Long Beach": {"country": "United States", "region": "North America", "type": "Sea Port"},
    "New York": {"country": "United States", "region": "North America", "type": "Sea Port / Air Hub"},
    "Savannah": {"country": "United States", "region": "North America", "type": "Sea Port"},
    "Dubai": {"country": "United Arab Emirates", "region": "Middle East", "type": "Sea Port / Air Hub"},
    "Jebel Ali": {"country": "United Arab Emirates", "region": "Middle East", "type": "Sea Port"},
    "JNPT": {"country": "India", "region": "South Asia", "type": "Sea Port"},
    "Mundra": {"country": "India", "region": "South Asia", "type": "Sea Port"},
    "Chennai Port": {"country": "India", "region": "South Asia", "type": "Sea Port"},
    "Pipavav": {"country": "India", "region": "South Asia", "type": "Sea Port"},
    "Colombo": {"country": "Sri Lanka", "region": "South Asia", "type": "Transshipment Hub"},
    "Tanjung Pelepas": {"country": "Malaysia", "region": "Asia", "type": "Transshipment Hub"},
    "Santos": {"country": "Brazil", "region": "South America", "type": "Sea Port"},
}

# Major Global Air Freight Hubs
GLOBAL_AIR_HUBS = {
    "Memphis": {"country": "United States", "code": "MEM", "type": "Air Cargo Hub"},
    "Anchorage": {"country": "United States", "code": "ANC", "type": "Air Cargo Transshipment"},
    "Louisville": {"country": "United States", "code": "SDF", "type": "Air Cargo Hub"},
    "Incheon": {"country": "South Korea", "code": "ICN", "type": "Air Cargo Hub"},
    "Frankfurt": {"country": "Germany", "code": "FRA", "type": "Air Cargo Hub"},
    "Paris CDG": {"country": "France", "code": "CDG", "type": "Air Cargo Hub"},
    "Amsterdam Schiphol": {"country": "Netherlands", "code": "AMS", "type": "Air Cargo Hub"},
    "London Heathrow": {"country": "United Kingdom", "code": "LHR", "type": "Air Cargo Hub"},
    "Doha": {"country": "Qatar", "code": "DOH", "type": "Air Cargo Hub"},
    "Chicago O'Hare": {"country": "United States", "code": "ORD", "type": "Air Cargo Hub"},
    "Tokyo Narita": {"country": "Japan", "code": "NRT", "type": "Air Cargo Hub"},
    "Delhi IGI": {"country": "India", "code": "DEL", "type": "Air Cargo Hub"},
    "Mumbai CSIA": {"country": "India", "code": "BOM", "type": "Air Cargo Hub"},
}

# Critical Global Maritime Canals & Chokepoints
GLOBAL_CHOKEPOINTS = {
    "Suez Canal": {"region": "Egypt / Middle East", "impact": "Asia-Europe Maritime Trade"},
    "Panama Canal": {"region": "Central America", "impact": "Pacific-Atlantic Maritime Trade"},
    "Red Sea": {"region": "Middle East / East Africa", "impact": "Suez Route Maritime Security"},
    "Bab-el-Mandeb": {"region": "Horn of Africa / Yemen", "impact": "Red Sea Entry Chokepoint"},
    "Strait of Hormuz": {"region": "Persian Gulf", "impact": "Global Energy & Chemical Transport"},
    "Strait of Malacca": {"region": "Southeast Asia", "impact": "East Asia-Europe Maritime Corridor"},
    "English Channel": {"region": "UK / France", "impact": "North Sea Maritime & Ferry Freight"},
    "Dover": {"region": "UK / France", "impact": "Cross-Channel Truck & Ro-Ro Freight"},
    "Bosphorus": {"region": "Turkey", "impact": "Black Sea Maritime Corridor"},
    "Rhine River": {"region": "Germany / Netherlands", "impact": "Inland European Chemical & Coal Barge Freight"},
    "Mississippi River": {"region": "United States", "impact": "Inland US Grain & Bulk Barge Freight"},
}

# Recognized Countries in Global Freight
GLOBAL_COUNTRIES = {
    "United States": ["US", "USA", "America"],
    "China": ["PRC", "Chinese"],
    "Germany": ["Deutschland", "German"],
    "Netherlands": ["Holland", "Dutch"],
    "United Kingdom": ["UK", "Britain", "British"],
    "Japan": ["Japanese"],
    "South Korea": ["Korea", "Korean"],
    "Singapore": ["Singaporean"],
    "United Arab Emirates": ["UAE", "Dubai"],
    "France": ["French"],
    "Canada": ["Canadian"],
    "Mexico": ["Mexican"],
    "India": ["Indian"],
    "Australia": ["Australian"],
    "Brazil": ["Brazilian"],
    "Vietnam": ["Vietnamese"],
    "Taiwan": ["Taiwanese"],
    "Belgium": ["Belgian"],
    "Italy": ["Italian"],
    "Spain": ["Spanish"],
}


# Paths - Dynamic resolution for Databricks, Linux, and Windows
def _resolve_project_root() -> Path:
    if "O2C_PROJECT_ROOT" in os.environ:
        p = Path(os.environ["O2C_PROJECT_ROOT"])
        if p.exists():
            return p

    try:
        p = Path(__file__).resolve().parent.parent
        if (p / "modules").exists() or (p / "Input Files").exists():
            return p
    except Exception:
        pass

    cwd = Path.cwd()
    if (cwd / "modules").exists() or (cwd / "Input Files").exists():
        return cwd
    if (cwd.parent / "modules").exists() or (cwd.parent / "Input Files").exists():
        return cwd.parent

    # Databricks workspace resolution
    if "DATABRICKS_RUNTIME_VERSION" in os.environ:
        for base in [Path("/Workspace/Users"), Path("/Workspace/Repos")]:
            if base.exists():
                try:
                    for sub in base.glob("*/O2C_AI"):
                        if sub.exists():
                            return sub
                except Exception:
                    pass
        tmp_p = Path("/tmp/O2C_AI")
        tmp_p.mkdir(parents=True, exist_ok=True)
        return tmp_p

    return cwd

_project_root = _resolve_project_root()

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

# Create directories
for d in [DB_PATH.parent, RAG_DIR, DOCS_DIR, VECTOR_DIR, CHUNKS_DIR, LOG_DIR, CSV_DIR, JSON_DIR]:
    d.mkdir(parents=True, exist_ok=True)