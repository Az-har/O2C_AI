"""Strike Intelligence Generator - Converts strike news into RAG-ready policy documents"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from collections import Counter

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


class StrikeIntelligenceGenerator:
    """
    Converts strike/disruption news into intelligence briefs for RAG.
    
    Purpose:
    - Strike news is NOT for validating RAG
    - Strike intelligence is RAG knowledge for route planning
    - Used by Copilot to avoid disrupted zones, find alternatives
    """
    
    def __init__(self, db_path=str(DB_PATH), output_dir=None):
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx not installed. Run: pip install python-docx")
        
        self.db_path = db_path
        self.output_dir = output_dir or (DOCS_DIR / "Strike_Intelligence")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all_intelligence(self) -> List[str]:
        """Generate strike intelligence documents from all news articles"""
        print("\n" + "="*80)
        print("🚨 STRIKE INTELLIGENCE GENERATOR")
        print("="*80)
        
        articles = self._fetch_strike_articles()
        print(f"\n📊 Found {len(articles)} strike articles in database")
        
        if not articles:
            print("⚠️  No strike articles found. Run the main pipeline first.")
            return []
        
        intel_by_city = self._group_articles_by_city(articles)
        intel_by_category = self._group_articles_by_category(articles)
        
        generated_files = []
        print(f"\n📝 Generating intelligence briefs...")
        
        for city, city_articles in intel_by_city.items():
            if len(city_articles) >= 3:
                doc_path = self._create_city_strike_brief(city, city_articles)
                generated_files.append(doc_path)
                print(f"   ✅ {doc_path.name}")
        
        for category, cat_articles in intel_by_category.items():
            if len(cat_articles) >= 5:
                doc_path = self._create_category_strike_brief(category, cat_articles)
                generated_files.append(doc_path)
                print(f"   ✅ {doc_path.name}")
        
        master_doc = self._create_master_disruption_intelligence(articles)
        generated_files.append(master_doc)
        print(f"   ✅ {master_doc.name}")
        
        print(f"\n✅ Generated {len(generated_files)} intelligence documents")
        print(f"📁 Saved to: {self.output_dir}")
        print("="*80 + "\n")
        
        return [str(f) for f in generated_files]
    
    def _fetch_strike_articles(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """SELECT title, city_mentioned as matched_cities, strike_type as category, 
                   published_date as published, source_name as source
                   FROM strike_news ORDER BY published_date DESC"""
        
        cursor.execute(query)
        articles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        for article in articles:
            # city_mentioned is a single string, convert to list
            city = article.get('matched_cities')
            if city and city != 'Unknown':
                article['matched_cities'] = [city]
            else:
                article['matched_cities'] = []
        return articles
    
    def _group_articles_by_city(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        by_city = {}
        for article in articles:
            for city in article.get('matched_cities', []):
                if city not in by_city:
                    by_city[city] = []
                by_city[city].append(article)
        return by_city
    
    def _group_articles_by_category(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        by_category = {}
        for article in articles:
            category = article.get('category', 'general')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(article)
        return by_category
    
    def _create_city_strike_brief(self, city: str, articles: List[Dict]) -> Path:
        doc = Document()
        
        # Header
        title = doc.add_heading(f'{city} Transportation Disruption Intelligence & Routing Protocol', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.add_paragraph(f"Monitored Geographic Hub: {city} Logistics Cluster")
        doc.add_paragraph(f"Total Disruption Events Analyzed: {len(articles)}")
        
        # 1. Executive Summary
        doc.add_heading('1. Executive Regional Disruption Assessment', 1)
        high_sev = [a for a in articles if 'HIGH' in str(a.get('severity', '')).upper()]
        med_sev = [a for a in articles if 'MEDIUM' in str(a.get('severity', '')).upper()]
        types = Counter([a.get('category', 'general') for a in articles])
        
        doc.add_paragraph(
            f"This intelligence brief evaluates active and historical transportation strikes, roadway blockades, "
            f"and labor disruptions impacting freight transit in the {city} commercial logistics corridor. "
            f"Of the {len(articles)} analyzed disruption records, {len(high_sev)} are classified as HIGH severity "
            f"(e.g., indefinite strikes, complete bandhs) and {len(med_sev)} as MEDIUM severity. "
            f"Dominant disruption modalities: {', '.join(f'{k.title()} ({v})' for k, v in types.items())}."
        )
        
        # 2. Key Logistics Corridors & Bottlenecks
        doc.add_heading('2. Critical Corridors & Choke Points', 1)
        corridor_info = {
            "Mumbai": "NH-48 (Mumbai-Pune / Mumbai-Gujarat Corridor), JNPT Port Container Freight Stations, Bhiwandi Warehouse Cluster.",
            "Delhi": "NH-44 (Delhi-Agra / Delhi-Chandigarh), Kundli-Manesar-Palwal (KMP) Expressway, Sanjay Gandhi Transport Nagar.",
            "Bangalore": "NH-44 (Hosur Road / Chennai Link), Nelamangala Logistics Hub, Electronic City toll junction.",
            "Chennai": "NH-16 (Chennai-Kolkata corridor), Sriperumbudur Industrial Corridor, Chennai Port Trust gates.",
            "Kolkata": "NH-19 (Durgapur Expressway), Dankuni Freight Terminal, Vidyasagar Setu approach.",
            "Hyderabad": "NH-65 (Hyderabad-Vijayawada), Outer Ring Road (ORR) logistics exits, Shamshabad cargo terminal.",
            "Pune": "Pune-Bangalore Highway (NH-48), Chakan Industrial Belt, Talegaon Logistics Park.",
            "Ahmedabad": "Ahmedabad-Vadodara Expressway (NE-1), Changodar Industrial Estate, Sanand GIDC corridor.",
            "Jaipur": "NH-48 (Jaipur-Delhi Highway), Vishwakarma Industrial Area, Transport Nagar bypass.",
            "Lucknow": "Lucknow-Agra Expressway, Transport Nagar Kanpur Road, Shaheed Path logistics junctions."
        }
        corridor_desc = corridor_info.get(city, f"{city} primary national highway entry points and regional transshipment yards.")
        doc.add_paragraph(f"Primary Inbound/Outbound Transit Routes: {corridor_desc}")
        doc.add_paragraph(
            "Impact Profile: Labor strikes and bandhs in this cluster directly impede primary FTL linehauls "
            "and disrupt secondary final-mile dispatch to veterinary clinics and regional animal hospitals."
        )
        
        # 3. Incident Registry
        doc.add_heading('3. Chronological Disruption Incidents & Intelligence Registry', 1)
        for idx, art in enumerate(articles[:15], 1):
            p = doc.add_paragraph()
            p.add_run(f"Incident #{idx}: {art.get('title', 'Unknown Title')}\n").bold = True
            p.add_run(f"• Published Date: {art.get('published', 'N/A')} | Source: {art.get('source', 'News Wire')}\n")
            p.add_run(f"• Modality: {art.get('category', 'general').title()} | Severity: {art.get('severity', 'LOW')}\n")
            if art.get('description'):
                clean_desc = art.get('description', '').replace('<a', '').replace('</a>', '').replace('&nbsp;', ' ')
                p.add_run(f"• Intelligence Summary: {clean_desc[:300]}...\n")
        
        # 4. Autonomous Copilot Operational Playbook
        doc.add_heading('4. Autonomous Copilot Operational & Legal Rules', 1)
        doc.add_paragraph(
            f"When active transit strikes or civil disruptions are detected in {city}, the O2C Copilot "
            f"applies the following deterministic decision rules:"
        )
        
        rules = [
            f"Force Majeure Adjudication (Clause 8.4): If a government-sanctioned bandh or total union road blockade in {city} delays transit by >12 hours, the carrier delay SLA penalty ($500/day) is waived upon submission of verified e-way bill telematics or police traffic advisory.",
            f"Dynamic Transit Buffer: For any order scheduled to pass through {city} with active strike news, automatically inject a +12.0 to +24.0 hour safety buffer into the predicted ETA.",
            f"Mode Shift Escalation: For life-critical veterinary diets and urgent pharmaceuticals routed through {city} with strike duration >24h, authorize emergency intermodal rail shift or $1,000 Air Freight replacement per Medical Stock-Out Policy 2024-04.",
            f"Receiving Window Compliance: If transit delays push delivery past clinic receiving hours (after 17:00), automatically reschedule delivery to 09:00 next business morning and trigger carrier redelivery fee waiver ($150 cap).",
            f"Proactive Stakeholder Notification: Send automated Microsoft Teams escalation card to Regional Logistics Director when order financial risk exceeds $500 threshold."
        ]
        for rule in rules:
            doc.add_paragraph(f"• {rule}")
        
        # Sanitize city name for filename
        safe_city = city.replace('/', '-').replace('\\', '-')
        filename = f"{safe_city}_Strike_Intelligence.docx"
        doc_path = self.output_dir / filename
        doc.save(str(doc_path))
        return doc_path
    
    def _create_category_strike_brief(self, category: str, articles: List[Dict]) -> Path:
        doc = Document()
        cat_name = category.replace('_', ' ').title()
        title = doc.add_heading(f'{cat_name} Transportation Disruption Pattern & Risk Analysis', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.add_paragraph(f"Transit Modality Category: {cat_name} Logistics Operations")
        doc.add_paragraph(f"Total Sector Incidents Analyzed: {len(articles)}")
        
        # 1. Modality Profile
        doc.add_heading('1. Sector Disruption Profile & Vulnerability', 1)
        doc.add_paragraph(
            f"This operational brief outlines systemic risk patterns, union actions, and transit vulnerabilities "
            f"specific to {cat_name} transportation across India. Disruptions in this sector typically stem from "
            f"toll tariff revisions, fuel price volatility, regulatory compliance enforcement (e.g. e-way bill disputes), "
            f"and driver union strikes."
        )
        
        # 2. Geographic Distribution
        all_cities = []
        for article in articles:
            all_cities.extend(article.get('matched_cities', []))
        city_impacts = Counter(all_cities)
        
        doc.add_heading('2. Geographic Impact Distribution', 1)
        for city, count in city_impacts.most_common(10):
            doc.add_paragraph(f"• {city}: {count} recorded incident(s)")
            
        # 3. Selected Real-World Incident Case Studies
        doc.add_heading('3. Key Sector Incidents & Historical Evidence', 1)
        for idx, art in enumerate(articles[:10], 1):
            p = doc.add_paragraph()
            p.add_run(f"Case #{idx}: {art.get('title', 'Unknown')}\n").bold = True
            p.add_run(f"• Date: {art.get('published', 'N/A')} | Source: {art.get('source', 'Unknown')}\n")
            if art.get('description'):
                clean_desc = art.get('description', '').replace('<a', '').replace('</a>', '').replace('&nbsp;', ' ')
                p.add_run(f"• Context: {clean_desc[:250]}...\n")
        
        # 4. Carrier Contract Adjudication & Mitigation
        doc.add_heading('4. Carrier SLA Adjudication & Operational Directives', 1)
        doc.add_paragraph(
            f"Standard operating procedures when {cat_name} disruptions impact Order-to-Cash deliveries:"
        )
        
        modality_guidance = {
            "truck": [
                "FTL Freight Rerouting: If primary highway corridor is blocked by truck strikes, carriers must attempt approved secondary state highway bypasses within 4 hours.",
                "Demurrage & Detention Caps: Carrier detention claims during nationwide truck strikes are capped at $100/day and require GPS geofence verification.",
                "Short-Dated Inventory Protection: For products with <60 days shelf-life stuck in highway transit, trigger Quality QA hold if transit exceeds 48 hours."
            ],
            "railway": [
                "Rail Yard Demurrage Rules: Rail container demurrage incurred due to labor strikes at inland container depots (ICDs) is reimbursable up to $500 per container upon railway receipt submission.",
                "Intermodal Drayage Shift: Transfer stranded rail cargo to dedicated road linehauls within 24 hours of rail stoppage."
            ],
            "bandh": [
                "Total Force Majeure Exemption: Complete Bharat Bandh or State Bandhs automatically activate Force Majeure Section 8.2 across all transit modes.",
                "Warehouse Dispatch Lockdown: No outbound shipments may be tendered during active bandh curfew hours to prevent en-route cargo damage or looting."
            ],
            "bus": [
                "Commuter Spillover Effect: State transport bus strikes cause heavy arterial road congestion (+2 to +4 hours linehaul delay). Planners should adjust dispatch times."
            ]
        }
        
        guidelines = modality_guidance.get(category.lower(), [
            "Assess transit delay duration against contractual delivery grace period (24 hours).",
            "Verify whether disruption is recognized by local transport authority as Force Majeure.",
            "Proactively notify destination clinics of revised ETA window."
        ])
        
        for g in guidelines:
            doc.add_paragraph(f"• {g}")
            
        # Sanitize category name for filename
        safe_cat = cat_name.replace('/', '-').replace('\\', '-')
        filename = f"{safe_cat}_Pattern_Analysis.docx"
        doc_path = self.output_dir / filename
        doc.save(str(doc_path))
        return doc_path
    
    def _create_master_disruption_intelligence(self, all_articles: List[Dict]) -> Path:
        doc = Document()
        title = doc.add_heading('Master Transportation Disruption Intelligence & National Playbook', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.add_paragraph(f"National Scope: India Logistics Network & Veterinary Supply Chain")
        doc.add_paragraph(f"Total National Disruption Records Analyzed: {len(all_articles)}")
        
        doc.add_heading('1. National Supply Chain Risk Overview', 1)
        doc.add_paragraph(
            "This master intelligence brief synthesizes nationwide transportation labor disruptions, strike trends, "
            "and highway bottlenecks across India. It serves as the primary ground-truth knowledge base for the "
            "O2C Autonomous Delivery Risk Copilot (Phases 2, 4, and 5)."
        )
        
        # High Severity Summary
        high_sev = [a for a in all_articles if 'HIGH' in str(a.get('severity', '')).upper()]
        doc.add_heading('2. Critical National Disruptions (High Severity)', 1)
        doc.add_paragraph(f"Identified {len(high_sev)} major nationwide or state-wide disruption events:")
        
        for idx, art in enumerate(high_sev[:10], 1):
            p = doc.add_paragraph()
            p.add_run(f"• [{art.get('published', 'N/A')}] {art.get('title', 'Unknown')}\n").bold = True
            p.add_run(f"  Source: {art.get('source', 'Unknown')} | Region: {art.get('matched_cities', ['National'])[0]}\n")
            
        doc.add_heading('3. Autonomous AI Orchestration Decision Matrix', 1)
        actions = [
            "Phase 1 Ingestion Integration: Automatically query live weather and strike news on daily schedule; populate SQLite database and update vector knowledge base.",
            "Phase 2 RAG Retrieval: When an order risk is evaluated, retrieve matching city and modality intelligence to adjudicate Force Majeure eligibility and transit delay buffers.",
            "Phase 3 ML Synergy: Combine strike severity alerts with historical transit velocity to adjust predicted delay hours and probability.",
            "Phase 4 Multi-Agent Adjudication: Route Supervisor verifies alternative corridors; Contract Adjudicator calculates carrier chargebacks and SLA penalties ($500/day vs 5%/day); Quality Mitigation agent enforces cold-chain holds.",
            "Phase 5 ERP & Teams Action: Update SAP ERP delivery block / date (VDATU); dispatch Actionable Adaptive Card to Regional Logistics Director for approvals exceeding $500."
        ]
        for action in actions:
            doc.add_paragraph(action, style='List Bullet')
        
        doc_path = self.output_dir / "Master_Disruption_Intelligence.docx"
        doc.save(str(doc_path))
        return doc_path


if __name__ == "__main__":
    generator = StrikeIntelligenceGenerator()
    files = generator.generate_all_intelligence()
    print(f"\n📄 Generated files:")
    for f in files:
        print(f"   - {f}")