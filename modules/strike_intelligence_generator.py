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
        title = doc.add_heading(f'{city} Transportation Disruption Intelligence', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.add_paragraph(f"Total Incidents Analyzed: {len(articles)}")
        
        doc.add_heading('Copilot Automated Response', 1)
        doc.add_paragraph(f"When {city} disruption is detected, Copilot:")
        
        actions = [
            "1. Identifies all active shipments routing through affected city",
            "2. Calculates delay probability based on disruption scale",
            "3. Retrieves alternative routing from regional logistics matrix",
            "4. Assesses SLA impact for affected deliveries",
            "5. Notifies planners with rerouting recommendations",
        ]
        for action in actions:
            doc.add_paragraph(action, style='List Bullet')
        
        # Sanitize city name for filename (replace / with -)
        safe_city = city.replace('/', '-').replace('\\', '-')
        filename = f"{safe_city}_Strike_Intelligence.docx"
        doc_path = self.output_dir / filename
        doc.save(str(doc_path))
        return doc_path
    
    def _create_category_strike_brief(self, category: str, articles: List[Dict]) -> Path:
        doc = Document()
        cat_name = category.replace('_', ' ').title()
        title = doc.add_heading(f'{cat_name} Disruption Pattern Analysis', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph(f"Total {cat_name} Incidents: {len(articles)}")
        
        all_cities = []
        for article in articles:
            all_cities.extend(article.get('matched_cities', []))
        city_impacts = Counter(all_cities)
        
        doc.add_heading('Most Affected Cities', 2)
        for city, count in city_impacts.most_common(10):
            doc.add_paragraph(f"{city}: {count} incidents", style='List Bullet')
        
        # Sanitize category name for filename
        safe_cat = cat_name.replace('/', '-').replace('\\', '-')
        filename = f"{safe_cat}_Pattern_Analysis.docx"
        doc_path = self.output_dir / filename
        doc.save(str(doc_path))
        return doc_path
    
    def _create_master_disruption_intelligence(self, all_articles: List[Dict]) -> Path:
        doc = Document()
        title = doc.add_heading('Master Transportation Disruption Intelligence', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_heading('Purpose', 1)
        doc.add_paragraph(
            "National-level guidance for O2C Delivery Risk Copilot on transportation "
            "strikes and disruptions across India's veterinary food supply chain."
        )
        
        doc.add_heading('Copilot Automated Actions', 1)
        actions = [
            "1. Cross-reference shipment routes with disruption zones",
            "2. Calculate delay probability and revised ETA",
            "3. Identify alternative routing options",
            "4. Assess Force Majeure applicability",
            "5. Notify planners and affected clinics proactively",
            "6. Update SAP with revised delivery dates",
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