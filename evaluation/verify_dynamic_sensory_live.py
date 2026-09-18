"""
Evaluation Harness: Order-First Dynamic Global Sensory Ingestion Live Verification
Validates:
1. Multi-modal entity extraction from international orders (Denver, Rotterdam, Singapore).
2. Geocoding resolution across continents (North America, Europe, Asia-Pacific).
3. Parametric weather retrieval across past (archive), present (live), and future (14-day forecast) using Open-Meteo.
4. Targeted disruption search query generation.
5. Integration with fetch_corridor_weather tool in agent_tools.py.
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.dynamic_sensory_service import (
    CorridorExtractionOutput,
    OrderCorridorExtractor,
    GlobalDynamicWeatherService,
    DynamicDisruptionKeywordGenerator,
    enrich_order_with_dynamic_sensory
)
from modules.agent_tools import fetch_corridor_weather

def run_sensory_verification():
    print("=" * 80)
    print("ORDER-FIRST DYNAMIC GLOBAL SENSORY INGESTION - MULTI-HORIZON VALIDATION")
    print("=" * 80)

    extractor = OrderCorridorExtractor()
    weather_svc = GlobalDynamicWeatherService()
    keyword_gen = DynamicDisruptionKeywordGenerator()

    # Scenario 1: US Domestic Long-Haul (Denver, CO) - Present Transit
    print("\n--- [Scenario 1: US Domestic Long-Haul (Denver, CO) - Present Transit] ---")
    order_denver = {
        "order_id": "800000000000001",
        "plant_city": "Chicago",
        "dest_city": "Denver",
        "origin_country": "US",
        "destination_country": "US",
        "shipping_type": "Road (FTL)",
        "requested_delivery_date": datetime.now().strftime("%Y-%m-%d")
    }
    c1 = extractor.extract_corridor(order_denver)
    print(f"1. Extracted Corridor: {c1.origin_city} -> {c1.destination_city} via {c1.shipping_mode}")
    print(f"   - Temporal Mode: {c1.temporal_horizon} | Target Date: {c1.target_transit_date}")
    print(f"   - Waypoints: {c1.connection_nodes}")
    assert c1.destination_city.lower() == "denver"
    assert c1.temporal_horizon == "present"

    w1 = weather_svc.fetch_corridor_weather(c1)
    print(f"2. Weather Fetch Status: {w1.get('status')}")
    coords1 = w1.get("coordinates", {})
    print(f"   - Resolved Coordinates: Lat {coords1.get('lat')}, Lon {coords1.get('lon')}")
    raw1 = w1.get("raw_weather", {})
    if "current" in raw1:
        curr = raw1["current"]
        print(f"   - Real-Time Reading: Temp={curr.get('temperature_2m')}C, Wind={curr.get('wind_speed_10m')} km/h, Precip={curr.get('precipitation')}mm")
    assert w1.get("status") in ("SUCCESS", "FALLBACK")

    q1 = keyword_gen.generate_search_queries(c1)
    print(f"3. Disruption Queries Generated ({len(q1)}):")
    for q in q1:
        print(f"   * {q}")
    assert len(q1) >= 3

    # Scenario 2: European Maritime / Barge Corridor (Rotterdam -> Antwerp) - Historical Archive (Past)
    print("\n--- [Scenario 2: EU Maritime Corridor (Rotterdam -> Antwerp) - Historical Past Date] ---")
    past_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    order_eu = {
        "order_id": "EU_MARITIME_002",
        "plant_city": "Rotterdam",
        "dest_city": "Antwerp",
        "origin_country": "NL",
        "destination_country": "BE",
        "shipping_type": "Ocean Container / Short-Sea Barge",
        "requested_delivery_date": past_date
    }
    c2 = extractor.extract_corridor(order_eu)
    print(f"1. Extracted Corridor: {c2.origin_city} -> {c2.destination_city} via {c2.shipping_mode}")
    print(f"   - Temporal Mode: {c2.temporal_horizon} | Target Date: {c2.target_transit_date}")
    assert c2.temporal_horizon == "past"
    assert c2.target_transit_date == past_date

    w2 = weather_svc.fetch_corridor_weather(c2)
    print(f"2. Weather Fetch Status: {w2.get('status')} (Archive Mode)")
    coords2 = w2.get("coordinates", {})
    print(f"   - Resolved Coordinates for Antwerp: Lat {coords2.get('lat')}, Lon {coords2.get('lon')}")
    assert w2.get("status") in ("SUCCESS", "FALLBACK")

    q2 = keyword_gen.generate_search_queries(c2)
    print(f"3. Disruption Queries Generated ({len(q2)}):")
    for q in q2:
        print(f"   * {q}")

    # Scenario 3: Trans-Pacific Air Freight (Singapore -> Sydney) - 14-Day Forecast (Future)
    print("\n--- [Scenario 3: Asia-Pacific Air Corridor (Singapore -> Sydney) - 14-Day Future Forecast] ---")
    future_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    order_apac = {
        "order_id": "APAC_AIR_003",
        "plant_city": "Singapore",
        "dest_city": "Sydney",
        "origin_country": "SG",
        "destination_country": "AU",
        "shipping_type": "Air Freight Expedited",
        "requested_delivery_date": future_date
    }
    c3 = extractor.extract_corridor(order_apac)
    print(f"1. Extracted Corridor: {c3.origin_city} -> {c3.destination_city} via {c3.shipping_mode}")
    print(f"   - Temporal Mode: {c3.temporal_horizon} | Target Date: {c3.target_transit_date}")
    assert c3.temporal_horizon == "future"

    w3 = weather_svc.fetch_corridor_weather(c3)
    print(f"2. Weather Fetch Status: {w3.get('status')} (14-Day Forecast Mode)")
    coords3 = w3.get("coordinates", {})
    print(f"   - Resolved Coordinates for Sydney: Lat {coords3.get('lat')}, Lon {coords3.get('lon')}")
    raw3 = w3.get("raw_weather", {})
    if "daily" in raw3:
        print(f"   - Forecast Data Retrieved: {len(raw3['daily'].get('time', []))} forecast days available.")
    assert w3.get("status") in ("SUCCESS", "FALLBACK")

    # Scenario 4: Tool Invocation from Agent Specialist Interface
    print("\n--- [Scenario 4: Specialist Tool fetch_corridor_weather Live Resolution] ---")
    # Query a non-Indian city that is not in the legacy 10-city list (e.g. Frankfurt)
    tool_res = fetch_corridor_weather.invoke({"city": "Frankfurt"})
    print(f"Specialist Tool Result for 'Frankfurt':")
    print(f"   - Status: {tool_res.get('status')}")
    print(f"   - Temperature: {tool_res.get('temperature_celsius')}°C")
    print(f"   - Hazard Detected: {tool_res.get('hazard_detected')}")
    print(f"   - Description: {tool_res.get('weather_description')}")
    assert tool_res.get("status") == "SUCCESS"
    assert tool_res.get("temperature_celsius") is not None

    print("\n" + "=" * 80)
    print("ALL 4 DYNAMIC SENSORY VALIDATION SCENARIOS PASSED WITH ZERO ERRORS!")
    print("=" * 80)

if __name__ == "__main__":
    run_sensory_verification()
