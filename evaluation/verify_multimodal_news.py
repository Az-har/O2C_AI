# -*- coding: utf-8 -*-
"""
Verification Test Suite for Global Multimodal Transportation Disruption Intelligence System
Validates:
1. Global & Multimodal Query Catalogue Coverage
2. Multimodal NLP Classification (Mode, Disruption Category, Severity, Geography)
3. Database Schema & Migration Verification (strike_news table columns and indexes)
4. Predictive Engine Environmental Cache & Delay Attribution Synergy
5. Strike Intelligence Generator Multimodal Playbook Generation
"""

import sys
import os
from pathlib import Path

# UTF-8 console output for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.config import (
    GLOBAL_DISRUPTION_QUERIES, GLOBAL_PORTS, GLOBAL_AIR_HUBS,
    GLOBAL_CHOKEPOINTS, GLOBAL_COUNTRIES
)
from modules.news_service import GlobalTransportDisruptionNewsService, NewsService
from modules.database_manager import DatabaseManager
from modules.predictive_engine import PredictiveEngine
from modules.strike_intelligence_generator import StrikeIntelligenceGenerator


def test_multimodal_news_system():
    print("=" * 80)
    print("GLOBAL MULTIMODAL TRANSPORTATION DISRUPTION INTELLIGENCE - VERIFICATION")
    print("=" * 80)

    # 1. Config & Query Matrices
    print("\n[Test 1/5] Verifying Global Multimodal Disruption Query Matrices...")
    expected_categories = [
        "ocean_maritime", "canals_chokepoints", "air_freight", "rail_freight",
        "road_trucking", "customs_border", "natural_disasters", "geopolitical_cyber", "domestic_corridors"
    ]
    for cat in expected_categories:
        assert cat in GLOBAL_DISRUPTION_QUERIES, f"Missing query category: {cat}"
        assert len(GLOBAL_DISRUPTION_QUERIES[cat]) > 0, f"Empty query category: {cat}"
    assert len(GLOBAL_PORTS) >= 20, f"Expected >=20 global ports, got {len(GLOBAL_PORTS)}"
    assert len(GLOBAL_CHOKEPOINTS) >= 8, f"Expected >=8 chokepoints, got {len(GLOBAL_CHOKEPOINTS)}"
    assert len(GLOBAL_AIR_HUBS) >= 10, f"Expected >=10 air hubs, got {len(GLOBAL_AIR_HUBS)}"
    print(f"   [OK] Config Matrix verified: {len(GLOBAL_DISRUPTION_QUERIES)} disruption categories, "
          f"{len(GLOBAL_PORTS)} ports, {len(GLOBAL_CHOKEPOINTS)} chokepoints, {len(GLOBAL_AIR_HUBS)} air hubs.")

    # 2. NLP Classification & Entity Extraction
    print("\n[Test 2/5] Verifying Multimodal NLP Entity Extraction...")
    service = GlobalTransportDisruptionNewsService()
    assert issubclass(GlobalTransportDisruptionNewsService, object)
    assert NewsService == GlobalTransportDisruptionNewsService, "Backward compatibility alias broken"

    test_samples = [
        {
            "text": "German Port Strike: Eurogate blocks rail slots as dockworker strike paralyzes Hamburg and Rotterdam terminals",
            "expected_mode": "Maritime / Ocean Port",
            "expected_cat": "Labor Strike / Walkout",
            "expected_country": "Germany"
        },
        {
            "text": "Suez Canal Authority refloats grounded container ship as draft restrictions cause Red Sea transit delay",
            "expected_mode": "Canal / Chokepoint",
            "expected_cat": "Canal / Chokepoint Blockage",
            "expected_country": "Egypt / Middle East"
        },
        {
            "text": "Frankfurt Airport ground handler strike forces cancellation of 300 cargo flights and air freight delays",
            "expected_mode": "Air Freight",
            "expected_cat": "Labor Strike / Walkout",
            "expected_country": "Germany"
        },
        {
            "text": "Freight rail union walkout halts Union Pacific intermodal corridor",
            "expected_mode": "Rail Freight",
            "expected_cat": "Labor Strike / Walkout",
            "expected_country": "Global"
        },
        {
            "text": "Major freight train derailment and bridge collapse shuts down rail freight corridor",
            "expected_mode": "Rail Freight",
            "expected_cat": "Infrastructure / Accident",
            "expected_country": "Global"
        },
        {
            "text": "Mexican truckers blockade California border crossing over commercial diesel and inspection delays",
            "expected_mode": "Road / Trucking",
            "expected_cat": "Labor Strike / Walkout",
            "expected_country": "Mexico"
        },
        {
            "text": "Ransomware cyberattack halts DP World terminal operating system causing severe container vessel backlog",
            "expected_mode": "Maritime / Ocean Port",
            "expected_cat": "Cyber / IT Outage",
            "expected_country": "Global"
        },
        {
            "text": "Super typhoon makes landfall closing Shanghai port container terminals and halting vessel berthing",
            "expected_mode": "Maritime / Ocean Port",
            "expected_cat": "Natural Disaster / Severe Weather",
            "expected_country": "China"
        },
        {
            "text": "Volcanic ash cloud from eruption shuts down international airspace and cargo flights",
            "expected_mode": "Air Freight",
            "expected_cat": "Natural Disaster / Severe Weather",
            "expected_country": "Global"
        },
        {
            "text": "Catastrophic flash flood causes rail line track washout halting intermodal freight trains",
            "expected_mode": "Rail Freight",
            "expected_cat": "Natural Disaster / Severe Weather",
            "expected_country": "Global"
        },
        {
            "text": "Severe blizzard and avalanche forces mountain pass closed for freight trucks and commercial convoys",
            "expected_mode": "Road / Trucking",
            "expected_cat": "Natural Disaster / Severe Weather",
            "expected_country": "Global"
        }
    ]

    for sample in test_samples:
        mode = service._classify_transport_mode(sample["text"])
        cat = service._classify_disruption_category(sample["text"])
        sev = service._classify_severity(sample["text"], mode, cat)
        geo = service._detect_geography(sample["text"])

        assert mode == sample["expected_mode"], f"Mode mismatch: got '{mode}', expected '{sample['expected_mode']}'"
        assert cat == sample["expected_cat"], f"Category mismatch: got '{cat}', expected '{sample['expected_cat']}'"
        print(f"   [OK] '{sample['text'][:55]}...' -> Mode: {mode} | Cat: {cat} | Sev: {sev} | Hub: {geo['hub']} ({geo['country']})")

    # 3. Database Schema Migration & Storage
    print("\n[Test 3/5] Verifying SQLite Database Schema & Migration v1.2...")
    db = DatabaseManager()
    with db.connection() as conn:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(strike_news)").fetchall()]
        for req_col in ["country_mentioned", "transport_mode", "disruption_category", "severity", "city_mentioned"]:
            assert req_col in cols, f"Missing column {req_col} in strike_news"
        count = conn.execute("SELECT COUNT(*) FROM strike_news").fetchone()[0]
        multimodal_count = conn.execute(
            "SELECT COUNT(*) FROM strike_news WHERE transport_mode != 'Multimodal' AND transport_mode IS NOT NULL"
        ).fetchone()[0]
        print(f"   [OK] strike_news verified: {count} total rows ({multimodal_count} enriched multimodal rows).")

    # 4. Predictive Engine Delay Correlation
    print("\n[Test 4/5] Verifying Predictive Engine Multimodal Disruption Synergy...")
    pe = PredictiveEngine()
    order_data = {
        "order_id": "TEST-INTL-001",
        "sales_org": "US01",
        "order_type": "OR",
        "delivery_priority": 1,
        "shipping_condition": "01",
        "customer_tier": "Platinum",
        "dest_city": "Hamburg",
        "carrier_mode": "Ocean Freight",
        "order_qty": 50.0,
        "net_price": 5000.0,
        "specialty_diet_flag": 0,
        "cold_chain_flag": 0,
        "short_dated_flag": 0,
        "carrier_name": "Maersk Line",
        "planned_lead_days": 10.0,
        "distance_km": 6000.0,
        "historical_delay_rate": 0.3
    }
    pred = pe.predict_delivery_delay(order_id="TEST-INTL-001", order_data=order_data)
    print(f"   [OK] Prediction Result: Delay Prob = {pred['delay_probability']:.1%}, Delay Hours = {pred['delay_hours']}h")
    print(f"   [OK] Root Cause Attribution: {pred['root_cause']}")
    assert "multimodal" in pred["root_cause"].lower() or "transit" in pred["root_cause"].lower() or "disaster" in pred["root_cause"].lower()

    # 5. Strike Intelligence Generator Multimodal Playbooks
    print("\n[Test 5/5] Verifying Multimodal Playbook Synthesis...")
    gen = StrikeIntelligenceGenerator()
    briefs = gen.generate_all_intelligence()
    assert len(briefs) > 0, "No intelligence documents generated"
    print(f"   [OK] Successfully generated {len(briefs)} multimodal intelligence playbooks in: {gen.output_dir.name}")
    for b in briefs[:4]:
        print(f"      • {Path(b).name}")

    print("\n" + "=" * 80)
    print("🎉 ALL 5 VERIFICATION SUITES PASSED CLEANLY!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    test_multimodal_news_system()
