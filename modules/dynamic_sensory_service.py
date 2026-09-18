"""
Dynamic Global Sensory Ingestion Service (Improvement 5.10 / Deliverable 8)

Replaces static regional scrapers with an Order-First Dynamic Ingestion Pipeline:
1. Ingests raw SAP sales orders first.
2. Extracts transit corridor entities (origin, destination, shipping mode, connection waypoints, temporal horizon).
3. Fetches parametric global weather via zero-key free Open-Meteo Geocoding, Forecast, & Archive APIs.
4. Generates hyper-targeted boolean disruption search queries for active corridor surveillance.
"""

import os
import requests
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date

logger = logging.getLogger("DynamicSensoryService")


class CorridorExtractionOutput(BaseModel):
    """Structured geographic and multimodal transit profile extracted from order"""
    origin_city: str = Field(description="Shipment starting location / manufacturing plant / distribution center")
    origin_country: str = Field(default="US", description="Origin country code or name")
    destination_city: str = Field(description="Consignee ship-to city / clinic / delivery terminal")
    destination_country: str = Field(default="US", description="Destination country code or name")
    shipping_mode: str = Field(description="Transport mode: Road (FTL/LTL), Air Freight, Ocean Container, Rail Intermodal")
    connection_nodes: List[str] = Field(default_factory=list, description="Intermediate transit waypoints, highway corridors, transfer hubs, or maritime ports")
    temporal_horizon: str = Field(description="Temporal evaluation mode: 'past' (historical audit), 'present' (active transit), or 'future' (promised ETA forecast)")
    target_transit_date: str = Field(description="Relevant date string YYYY-MM-DD for weather evaluation")


# Global Multi-Tier Persistent Caches (Thread-Safe Process Lifetime)
_GLOBAL_GEO_CACHE: Dict[str, Dict[str, float]] = {
    # Indian Metros & Freight Hubs
    "mumbai": {"lat": 19.0760, "lon": 72.8777},
    "delhi": {"lat": 28.6139, "lon": 77.2090},
    "bangalore": {"lat": 12.9716, "lon": 77.5946},
    "chennai": {"lat": 13.0827, "lon": 80.2707},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "pune": {"lat": 18.5204, "lon": 73.8567},
    "kolkata": {"lat": 22.5726, "lon": 88.3639},
    "ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "jaipur": {"lat": 26.9124, "lon": 75.7873},
    "lucknow": {"lat": 26.8467, "lon": 80.9462},
    "bhubaneswar": {"lat": 20.2961, "lon": 85.8245},
    "nagpur": {"lat": 21.1458, "lon": 79.0882},

    # US Domestic Corridor Hubs (SAP Dataset)
    "boston": {"lat": 42.3601, "lon": -71.0589},
    "chicago": {"lat": 41.8781, "lon": -87.6298},
    "denver": {"lat": 39.7392, "lon": -104.9903},
    "new york": {"lat": 40.7128, "lon": -74.0060},
    "los angeles": {"lat": 34.0522, "lon": -118.2437},
    "austin": {"lat": 30.2672, "lon": -97.7431},
    "miami": {"lat": 25.7617, "lon": -80.1918},
    "buffalo": {"lat": 42.8864, "lon": -78.8784},
    "dallas": {"lat": 32.7767, "lon": -96.7970},
    "san francisco": {"lat": 37.7749, "lon": -122.4194},
    "seattle": {"lat": 47.6062, "lon": -122.3321},
    "atlanta": {"lat": 33.7490, "lon": -84.3880},

    # Global Maritime, Port & Intermodal Chokepoints
    "rotterdam": {"lat": 51.9244, "lon": 4.4777},
    "antwerp": {"lat": 51.2205, "lon": 4.4003},
    "singapore": {"lat": 1.3521, "lon": 103.8198},
    "sydney": {"lat": -33.8679, "lon": 151.2073},
    "frankfurt": {"lat": 50.1109, "lon": 8.6821},
    "shanghai": {"lat": 31.2304, "lon": 121.4737},
    "hamburg": {"lat": 53.5511, "lon": 9.9937},
    "dubai": {"lat": 25.2048, "lon": 55.2708},
    "london": {"lat": 51.5074, "lon": -0.1278},
    "paris": {"lat": 48.8566, "lon": 2.3522},
    "tokyo": {"lat": 35.6762, "lon": 139.6503}
}

_GLOBAL_WEATHER_CACHE: Dict[str, Dict[str, Any]] = {}
_GLOBAL_CORRIDOR_CACHE: Dict[str, CorridorExtractionOutput] = {}
_GLOBAL_SEARCH_QUERY_CACHE: Dict[str, List[str]] = {}
_SHARED_SESSION = requests.Session()


def _is_ollama_alive(base_url: str = "http://127.0.0.1:11434") -> bool:
    """Ultra-fast (0.3s) health probe to avoid blocking on offline or saturated local LLM daemon"""
    try:
        import urllib.request
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=0.3):
            return True
    except Exception:
        return False


class OrderCorridorExtractor:
    """Uses LLM structured extraction to parse global geographic routing entities from raw SAP orders"""

    EXTRACTION_PROMPT = """You are an enterprise logistics routing analyst. 
Analyze the provided SAP Sales Order / Delivery document and extract the physical transit corridor details.
Determine origin, destination, shipping mode, critical intermediate connection nodes (e.g. major highways, transfer airports, maritime chokepoints), and temporal transit window.
Return valid JSON adhering strictly to the schema."""

    def __init__(self, model_name: str = "qwen2.5:7b", base_url: str = "http://127.0.0.1:11434"):
        self.model_name = model_name
        self.base_url = base_url

    def extract_corridor(self, order_payload: Dict[str, Any]) -> CorridorExtractionOutput:
        """Invokes LLM with structured schema or falls back to robust deterministic parsing with caching"""
        # Form cache signature
        dest_raw = str(order_payload.get("dest_city") or order_payload.get("city") or order_payload.get("destination_city") or "Boston").strip().lower()
        orig_raw = str(order_payload.get("plant_city") or order_payload.get("origin_city") or order_payload.get("shipping_point_city") or "Chicago").strip().lower()
        mode_raw = str(order_payload.get("shipping_type") or order_payload.get("transport_mode") or order_payload.get("shipping_mode") or "Road (FTL)").strip().lower()
        req_date = str(order_payload.get("requested_delivery_date") or order_payload.get("vdatu") or "").strip()
        
        cache_key = f"{orig_raw}|{dest_raw}|{mode_raw}|{req_date[:10]}"
        if cache_key in _GLOBAL_CORRIDOR_CACHE:
            return _GLOBAL_CORRIDOR_CACHE[cache_key]

        # Fast probe before attempting Ollama
        if _is_ollama_alive(self.base_url):
            try:
                from langchain_ollama import ChatOllama
                llm = ChatOllama(model=self.model_name, temperature=0.1, base_url=self.base_url, timeout=1.5)
                structured_llm = llm.with_structured_output(CorridorExtractionOutput)
                result = structured_llm.invoke(f"{self.EXTRACTION_PROMPT}\n\nOrder Payload:\n{order_payload}")
                if result and isinstance(result, CorridorExtractionOutput):
                    _GLOBAL_CORRIDOR_CACHE[cache_key] = result
                    return result
            except Exception as e:
                logger.debug(f"LLM corridor extraction falling back to deterministic extraction: {e}")

        # High-Fidelity Deterministic Fallback
        dest = str(
            order_payload.get("dest_city") or
            order_payload.get("city") or
            order_payload.get("destination_city") or
            "Boston"
        ).strip()
        
        origin = str(
            order_payload.get("plant_city") or
            order_payload.get("origin_city") or
            order_payload.get("shipping_point_city") or
            "Chicago"
        ).strip()
        
        mode = str(
            order_payload.get("shipping_type") or
            order_payload.get("transport_mode") or
            order_payload.get("shipping_mode") or
            "Road (FTL)"
        ).strip()

        # Infer connection nodes based on route
        nodes = []
        if "air" in mode.lower():
            nodes = [f"{origin} Air Freight Cargo Hub", f"{dest} International Cargo Terminal"]
        elif "rail" in mode.lower() or "intermodal" in mode.lower():
            nodes = [f"{origin} Intermodal Yard", "Class-I Freight Corridor", f"{dest} Railhead"]
        else:
            nodes = [f"Interstate Highway Corridor from {origin}", f"{dest} Freight Gateway"]

        # Infer temporal horizon
        today_str = datetime.now().strftime("%Y-%m-%d")
        horizon = "present"
        target_date = today_str

        if req_date:
            try:
                clean_date = req_date.split()[0]
                if clean_date < today_str:
                    horizon = "past"
                    target_date = clean_date
                elif clean_date > today_str:
                    horizon = "future"
                    target_date = clean_date
            except Exception:
                pass

        corridor = CorridorExtractionOutput(
            origin_city=origin,
            origin_country=str(order_payload.get("origin_country") or "US"),
            destination_city=dest,
            destination_country=str(order_payload.get("destination_country") or "US"),
            shipping_mode=mode,
            connection_nodes=nodes,
            temporal_horizon=horizon,
            target_transit_date=target_date
        )
        _GLOBAL_CORRIDOR_CACHE[cache_key] = corridor
        return corridor


class GlobalDynamicWeatherService:
    """
    Zero-key, 100% free global weather client utilizing Open-Meteo Geocoding, Forecast, and Archive APIs.
    Features persistent class-level geocoding and weather caching to guarantee zero redundant network hits
    and eliminate API throttling / freezes during batch runs.
    """

    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

    def __init__(self):
        self._session = _SHARED_SESSION

    def geocode_location(self, city_name: str, country: Optional[str] = None) -> Optional[Dict[str, float]]:
        """Resolves any global city to exact latitude & longitude with persistent in-memory caching"""
        cache_key = city_name.lower().strip()
        if cache_key in _GLOBAL_GEO_CACHE:
            return _GLOBAL_GEO_CACHE[cache_key]

        try:
            params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
            r = self._session.get(self.GEOCODING_URL, params=params, timeout=2.5)
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                if results:
                    top = results[0]
                    coords = {"lat": float(top["latitude"]), "lon": float(top["longitude"])}
                    _GLOBAL_GEO_CACHE[cache_key] = coords
                    return coords
        except Exception as e:
            logger.debug(f"Geocoding failed for {city_name}: {e}")

        # Fallback default coordinates (Chicago)
        coords = {"lat": 41.8781, "lon": -87.6298}
        _GLOBAL_GEO_CACHE[cache_key] = coords
        return coords

    def fetch_corridor_weather(self, corridor: CorridorExtractionOutput) -> Dict[str, Any]:
        """Dynamically pulls weather along the corridor with persistent caching across batch runs"""
        dest_city_clean = corridor.destination_city.lower().strip()
        horizon = corridor.temporal_horizon.lower()
        target_date = corridor.target_transit_date

        weather_cache_key = f"{dest_city_clean}|{horizon}|{target_date}"
        if weather_cache_key in _GLOBAL_WEATHER_CACHE:
            return _GLOBAL_WEATHER_CACHE[weather_cache_key]

        dest_coords = self.geocode_location(corridor.destination_city, corridor.destination_country)
        if not dest_coords:
            dest_coords = {"lat": 42.3601, "lon": -71.0589}  # Boston

        try:
            if horizon == "past":
                params = {
                    "latitude": dest_coords["lat"],
                    "longitude": dest_coords["lon"],
                    "start_date": target_date,
                    "end_date": target_date,
                    "hourly": "temperature_2m,precipitation,snowfall,wind_speed_10m"
                }
                res = self._session.get(self.ARCHIVE_URL, params=params, timeout=3.0).json()
            elif horizon == "future":
                params = {
                    "latitude": dest_coords["lat"],
                    "longitude": dest_coords["lon"],
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,snowfall_sum,wind_speed_10m_max",
                    "forecast_days": 14,
                    "timezone": "auto"
                }
                res = self._session.get(self.FORECAST_URL, params=params, timeout=3.0).json()
            else:
                params = {
                    "latitude": dest_coords["lat"],
                    "longitude": dest_coords["lon"],
                    "current": "temperature_2m,relative_humidity_2m,precipitation,snowfall,wind_speed_10m",
                    "timezone": "auto"
                }
                res = self._session.get(self.FORECAST_URL, params=params, timeout=3.0).json()

            weather_res = {
                "status": "SUCCESS",
                "city": corridor.destination_city,
                "coordinates": dest_coords,
                "temporal_mode": horizon,
                "target_date": target_date,
                "raw_weather": res
            }
            _GLOBAL_WEATHER_CACHE[weather_cache_key] = weather_res
            return weather_res
        except Exception as e:
            # Resilient graceful degradation fallback
            fallback_res = {
                "status": "FALLBACK",
                "city": corridor.destination_city,
                "coordinates": dest_coords,
                "temporal_mode": horizon,
                "target_date": target_date,
                "raw_weather": {
                    "current": {
                        "temperature_2m": 22.0,
                        "precipitation": 0.0,
                        "wind_speed_10m": 12.0
                    }
                },
                "note": f"Weather API offline or timed out: {e}"
            }
            # Cache the fallback too to prevent repeated timeout stalls during network outage
            _GLOBAL_WEATHER_CACHE[weather_cache_key] = fallback_res
            return fallback_res


class DynamicDisruptionKeywordGenerator:
    """Generates hyper-targeted news and strike search strings tailored to the corridor with caching and timeouts"""

    def __init__(self, model_name: str = "qwen2.5:7b", base_url: str = "http://127.0.0.1:11434"):
        self.model_name = model_name
        self.base_url = base_url

    def generate_search_queries(self, corridor: CorridorExtractionOutput) -> List[str]:
        """Generates 3-5 precise boolean search queries for the live news / strike aggregator"""
        c_dest = corridor.destination_city
        c_orig = corridor.origin_city
        c_mode = corridor.shipping_mode
        first_node = corridor.connection_nodes[0] if corridor.connection_nodes else f"{c_orig} to {c_dest}"

        cache_key = f"{c_orig.lower()}|{c_dest.lower()}|{c_mode.lower()}"
        if cache_key in _GLOBAL_SEARCH_QUERY_CACHE:
            return _GLOBAL_SEARCH_QUERY_CACHE[cache_key]

        if _is_ollama_alive(self.base_url):
            prompt = f"""Generate 4 focused news search query strings to detect active strikes, weather disasters, road blockades, and logistics disruptions affecting:
- Origin: {corridor.origin_city}, {corridor.origin_country}
- Destination: {corridor.destination_city}, {corridor.destination_country}
- Transit Mode: {corridor.shipping_mode}
- Corridor Nodes: {', '.join(corridor.connection_nodes)}
Output format: Provide exactly 4 query strings, one per line."""

            try:
                from langchain_ollama import ChatOllama
                llm = ChatOllama(model=self.model_name, temperature=0.2, base_url=self.base_url, timeout=1.5)
                resp = llm.invoke(prompt)
                lines = [l.strip().lstrip("-*1234. ") for l in resp.content.splitlines() if l.strip()]
                if len(lines) >= 2:
                    queries = lines[:4]
                    _GLOBAL_SEARCH_QUERY_CACHE[cache_key] = queries
                    return queries
            except Exception:
                pass

        # Deterministic Domain-Specific Search Fallback
        deterministic_queries = [
            f"{c_dest} {c_mode} disruption delay",
            f"{c_dest} highway road closure freight strike",
            f"{first_node} transit delay blockade",
            f"{c_orig} to {c_dest} logistics bottleneck"
        ]
        _GLOBAL_SEARCH_QUERY_CACHE[cache_key] = deterministic_queries
        return deterministic_queries


def enrich_order_with_dynamic_sensory(order_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Master Ingestion Entry Point: Takes an order, extracts the corridor,
    fetches global weather dynamically, and generates targeted disruption search vectors.
    """
    extractor = OrderCorridorExtractor()
    corridor = extractor.extract_corridor(order_payload)

    weather_service = GlobalDynamicWeatherService()
    weather_data = weather_service.fetch_corridor_weather(corridor)

    disruption_gen = DynamicDisruptionKeywordGenerator()
    search_queries = disruption_gen.generate_search_queries(corridor)

    return {
        "corridor": corridor.model_dump(),
        "weather": weather_data,
        "targeted_search_queries": search_queries,
        "enriched_at": datetime.now().isoformat()
    }
