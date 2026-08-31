"""Weather Policy Generator - Converts weather data into RAG-ready policy documents"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from .config import DB_PATH, DOCS_DIR
except ImportError:
    from config import DB_PATH, DOCS_DIR


class WeatherPolicyGenerator:
    """
    Converts weather alerts from database into policy documents for RAG.
    
    Purpose:
    - Weather data is NOT for validating RAG
    - Weather policies are RAG knowledge sources
    - Used by Copilot to apply Force Majeure, route changes, etc.
    """
    
    def __init__(self, db_path=str(DB_PATH), output_dir=None):
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx not installed. Run: pip install python-docx")
        
        self.db_path = db_path
        self.output_dir = output_dir or (DOCS_DIR / "Weather_Policies")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all_policies(self) -> List[str]:
        """Generate weather policy documents from all weather alerts"""
        print("\n" + "="*80)
        print("🌤️  WEATHER POLICY GENERATOR")
        print("="*80)
        
        # Get weather alerts from database
        alerts = self._fetch_weather_alerts()
        print(f"\n📊 Found {len(alerts)} weather alerts in database")
        
        if not alerts:
            print("⚠️  No weather alerts found. Run the main pipeline first.")
            return []
        
        # Group by city and severity
        policies_by_city = self._group_alerts_by_city(alerts)
        
        # Generate policy documents
        generated_files = []
        print(f"\n📝 Generating policy documents...")
        
        for city, city_alerts in policies_by_city.items():
            doc_path = self._create_city_weather_policy(city, city_alerts)
            generated_files.append(doc_path)
            print(f"   ✅ {doc_path.name}")
        
        # Create master weather protocol document
        master_doc = self._create_master_weather_protocol(alerts)
        generated_files.append(master_doc)
        print(f"   ✅ {master_doc.name}")
        
        print(f"\n✅ Generated {len(generated_files)} weather policy documents")
        print(f"📁 Saved to: {self.output_dir}")
        print("="*80 + "\n")
        
        return [str(f) for f in generated_files]
    
    def _fetch_weather_alerts(self) -> List[Dict]:
        """Fetch all weather alerts from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT city_name as city, temperature as temp_c, weather_description as description, 
                   wind_speed as wind_ms, rain_1h as rain_mm, visibility_km, 
                   recorded_at as timestamp, 0 as latitude, 0 as longitude
            FROM weather_readings
            WHERE temperature > 40 OR wind_speed > 15 OR rain_1h > 20 OR visibility_km < 1
            ORDER BY city_name, recorded_at DESC
        """
        
        cursor.execute(query)
        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return alerts
    
    def _group_alerts_by_city(self, alerts: List[Dict]) -> Dict[str, List[Dict]]:
        """Group alerts by city"""
        by_city = {}
        for alert in alerts:
            city = alert['city']
            if city not in by_city:
                by_city[city] = []
            by_city[city].append(alert)
        return by_city
    
    def _create_city_weather_policy(self, city: str, alerts: List[Dict]) -> Path:
        """Create a weather policy document for a specific city"""
        doc = Document()
        
        # Title
        title = doc.add_heading(f'{city} Severe Weather Protocol', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Metadata
        doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.add_paragraph(f"Total Alerts Analyzed: {len(alerts)}")
        doc.add_paragraph()
        
        # Executive Summary
        doc.add_heading('Executive Summary', 1)
        summary = doc.add_paragraph(
            f"This document outlines severe weather protocols for {city} based on "
            f"historical weather alert patterns. It provides guidance for the O2C Delivery "
            f"Risk Copilot on when to apply Force Majeure clauses, reroute shipments, "
            f"and notify stakeholders."
        )
        
        # Weather Thresholds
        doc.add_heading('Severe Weather Thresholds', 1)
        doc.add_paragraph("The following conditions trigger automatic Copilot alerts:")
        
        thresholds = doc.add_paragraph()
        thresholds.add_run("🌡️  Extreme Heat: ").bold = True
        thresholds.add_run("Temperature > 40°C\n")
        
        thresholds.add_run("💨 High Wind: ").bold = True
        thresholds.add_run("Wind Speed > 15 m/s\n")
        
        thresholds.add_run("🌧️  Heavy Rain: ").bold = True
        thresholds.add_run("Rainfall > 20mm/hr\n")
        
        thresholds.add_run("🌫️  Low Visibility: ").bold = True
        thresholds.add_run("Visibility < 1km")
        
        # Alert History
        doc.add_heading(f'Recent {city} Weather Alerts', 1)
        
        # Categorize alerts
        heat_alerts = [a for a in alerts if a['temp_c'] > 40]
        wind_alerts = [a for a in alerts if a['wind_ms'] > 15]
        rain_alerts = [a for a in alerts if a['rain_mm'] > 20]
        visibility_alerts = [a for a in alerts if a['visibility_km'] < 1]
        
        if heat_alerts:
            doc.add_heading('Extreme Heat Events & Cold-Chain Protocol', 2)
            doc.add_paragraph(
                f"🌡️  {len(heat_alerts)} extreme heat events recorded. "
                f"Peak: {max(a['temp_c'] for a in heat_alerts):.1f}°C in {city}."
            )
            doc.add_paragraph(
                "• Product Impact: Ambient temperature exceeding 40.0°C degrades lipid stability in premium therapeutic wet pet food and denatures active enzymes in veterinary probiotics.\n"
                "• Mandatory Quality Action: Any shipment in transit through this zone exceeding 4.0 hours without active reefer logging must undergo HPLC stability testing and human organoleptic evaluation upon arrival. Reduce nominal shelf-life by 20% per QA Policy 2024-03.\n"
                "• Cold-Chain Expedited Transit: Automatically prioritize refrigerated FTL carriers and dispatch reefer unit data logger logs."
            )
        
        if wind_alerts:
            doc.add_heading('High Wind & Gale Warning Protocol', 2)
            doc.add_paragraph(
                f"💨 {len(wind_alerts)} high wind events recorded. "
                f"Peak: {max(a['wind_ms'] for a in wind_alerts):.1f} m/s in {city}."
            )
            doc.add_paragraph(
                "• Transit Safety: High crosswinds exceeding 15.0 m/s pose rollover hazards for high-cube curtain-sided trailers (>3.0m height).\n"
                "• Carrier Routing Directive: Suspend high-cube trailer routing over coastal bridges and elevated expressways; mandate low-profile rigid trucks.\n"
                "• Force Majeure Eligibility: Delays resulting from official IMD (India Meteorological Department) gale warnings qualify for Section 4.2 Force Majeure relief upon submission of toll camera timestamp logs."
            )
        
        if rain_alerts:
            doc.add_heading('Heavy Precipitation & Flood Advisory', 2)
            doc.add_paragraph(
                f"🌧️  {len(rain_alerts)} heavy rain events recorded. "
                f"Peak: {max(a['rain_mm'] for a in rain_alerts):.1f} mm/hr in {city}."
            )
            doc.add_paragraph(
                "• Packaging & Moisture Risk: Rainfall exceeding 20.0 mm/hr creates severe corrugated box crush hazards and corrugated carton moisture saturation.\n"
                "• Mandatory Warehouse Action: All pallets exiting the warehouse during active heavy rain advisories must receive secondary 80-gauge poly-stretch film wrapping.\n"
                "• QA Inspection Block: Any shipment incurring transit delays >24.0 hours during monsoon flood conditions must be placed on SAP QA Hold (Stock Type 'S') pending moisture probe inspection (threshold: >12% carton moisture content = 100% rejection)."
            )
        
        if visibility_alerts:
            doc.add_heading('Dense Fog & Low Visibility Protocol', 2)
            doc.add_paragraph(
                f"🌫️  {len(visibility_alerts)} low visibility events recorded. "
                f"Minimum Visibility: {min(a['visibility_km'] for a in visibility_alerts):.2f} km in {city}."
            )
            doc.add_paragraph(
                "• Highway Speed Restriction: Dense fog reduces safe highway transit velocity below 30 km/h on national corridors.\n"
                "• Copilot Action: Automatically inject a +4.0 to +8.0 hour dynamic buffer into predicted arrival time (PDD).\n"
                "• Proactive Clinic Rescheduling: Notify receiving veterinary clinics before 14:00 if night-shift linehaul is fog-delayed, preventing after-hours dock lockouts ($150 redelivery fee waiver applied)."
            )
        
        # Mitigation Actions
        doc.add_heading('Automated Copilot Actions', 1)
        doc.add_paragraph(
            "When severe weather is detected, the Copilot automatically:"
        )
        
        actions = [
            "1. Cross-references carrier location with weather alert zone",
            "2. Calculates delay probability and revised ETA",
            "3. Retrieves applicable Force Majeure clauses from vendor contracts",
            "4. Assesses QA inspection requirements based on cargo type and delay duration",
            "5. Notifies logistics planners via MS Teams with recommended mitigation",
            "6. Updates SAP delivery date (VDATU) if delay confirmed",
        ]
        
        for action in actions:
            doc.add_paragraph(action, style='List Bullet')
        
        # Save document
        filename = f"{city}_Weather_Protocol.docx"
        doc_path = self.output_dir / filename
        doc.save(str(doc_path))
        
        return doc_path
    
    def _create_master_weather_protocol(self, all_alerts: List[Dict]) -> Path:
        """Create master weather protocol document covering all cities"""
        doc = Document()
        
        title = doc.add_heading('Master Severe Weather Protocol', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_heading('Purpose', 1)
        doc.add_paragraph(
            "This master protocol provides cross-regional guidance for the O2C Delivery "
            "Risk Copilot when severe weather threatens delivery operations across India."
        )
        
        doc.add_heading('National Weather Impact Summary', 1)
        
        # Get unique cities
        cities = set(a['city'] for a in all_alerts)
        doc.add_paragraph(f"Cities Monitored: {len(cities)}")
        doc.add_paragraph(f"Total Weather Events Analyzed: {len(all_alerts)}")
        
        # Force Majeure Guidelines
        doc.add_heading('Force Majeure Eligibility Criteria', 1)
        doc.add_paragraph(
            "Weather events qualify for Force Majeure protection under "
            "Carrier Master Vendor Agreements when:"
        )
        
        criteria = [
            "Temperature exceeds 42°C (Level 5 Heat Alert)",
            "Wind speed exceeds 20 m/s (Level 4+ Storm)",
            "Rainfall exceeds 50mm/hr (Level 5 Monsoon Alert)",
            "Visibility drops below 0.5km (Level 5 Fog Alert)",
            "Government-issued transport advisory is active",
        ]
        
        for criterion in criteria:
            doc.add_paragraph(criterion, style='List Bullet')
        
        doc.add_paragraph(
            "\nNote: Carrier must provide proof of weather impact at time of delay. "
            "Copilot validates claims against weather API timestamps."
        )
        
        # Regional Routing
        doc.add_heading('Regional Rerouting Matrix', 1)
        doc.add_paragraph(
            "When primary routes are weather-impacted, use these alternatives:"
        )
        
        routes = [
            "Mumbai → Delhi: If Mumbai flooded, route via Pune → Ahmedabad → Delhi",
            "Chennai → Bangalore: If heavy rain, use NH-44 southern corridor",
            "Kolkata → Eastern deliveries: Cyclone season (May-Oct) requires 48hr buffer",
        ]
        
        for route in routes:
            doc.add_paragraph(route, style='List Bullet')
        
        # Save
        doc_path = self.output_dir / "Master_Weather_Protocol.docx"
        doc.save(str(doc_path))
        
        return doc_path


if __name__ == "__main__":
    generator = WeatherPolicyGenerator()
    files = generator.generate_all_policies()
    print(f"\n📄 Generated files:")
    for f in files:
        print(f"   - {f}")
