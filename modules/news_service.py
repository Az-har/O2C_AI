"""News Service for O2C AI Monitor"""
import requests
import time
import warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from datetime import datetime

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


class NewsService:
    """Scrapes and classifies transportation strike news from Google News RSS"""

    RSS_URL = "https://news.google.com/rss/search"
    
    _SEVERITY_HIGH = ["bharat bandh", "national strike", "indefinite", "complete shutdown"]
    _SEVERITY_MEDIUM = ["state bandh", "24-hour", "48-hour", "city strike"]
    
    _TYPE_MAP = [
        (["bus", "rtc", "ksrtc"], "bus"),
        (["truck", "lorry"], "truck"),
        (["rail", "train"], "railway"),
        (["auto", "rickshaw"], "auto"),
        (["taxi", "cab"], "taxi"),
        (["metro"], "metro"),
        (["bandh", "hartal"], "bandh"),
    ]

    def __init__(self, keywords: list, cities: dict):
        self.keywords = keywords
        self.cities = cities

    def fetch(self, date: str = None, city: str = None) -> list:
        """Fetch strike news. Optionally filter by date or city."""
        queries = self._build_queries(city)
        raw = []
        seen = set()
        
        date_filter = self._date_filter(date) if date else ""
        
        for q in queries:
            full_query = f"{q} {date_filter}".strip()
            articles = self._rss_search(full_query)
            for a in articles:
                key = a["title"].lower()[:80]
                if key not in seen:
                    seen.add(key)
                    raw.append(a)
        
        # Enrich each article
        enriched = []
        for a in raw:
            a["city_mentioned"] = self._detect_city(a["title"] + " " + a["description"])
            a["state_mentioned"] = self._get_state(a["city_mentioned"])
            a["severity"] = self._classify_severity(a["title"] + " " + a["description"])
            a["strike_type"] = self._classify_type(a["title"] + " " + a["description"])
            a["scraped_at"] = datetime.now().isoformat()
            enriched.append(a)
        
        return enriched

    def _build_queries(self, city: str = None) -> list:
        if city:
            return [f"{kw} {city} India" for kw in self.keywords]
        else:
            return [f"{kw} India" for kw in self.keywords]

    def _date_filter(self, date: str) -> str:
        """Build Google News date filter"""
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            return f"after:{dt.strftime('%Y-%m-%d')} before:{dt.strftime('%Y-%m-%d')}"
        except:
            return ""

    def _rss_search(self, query: str) -> list:
        """Execute one RSS search"""
        try:
            r = requests.get(self.RSS_URL, params={"q": query, "hl": "en-IN", "gl": "IN", "ceid": "IN:en"}, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "html.parser")
            
            articles = []
            for item in soup.find_all("item")[:10]:  # Limit 10 per query
                articles.append({
                    "title": item.title.text if item.title else "",
                    "description": item.description.text if item.description else "",
                    "url": item.link.text if item.link else "",
                    "source_name": item.source.text if item.source else "Unknown",
                    "published_date": item.pubDate.text if item.pubDate else "",
                    "keyword_matched": query.split()[0]
                })
            
            time.sleep(0.5)  # Rate limit
            return articles
        except Exception as e:
            print(f"   ❌ RSS error: {str(e)[:50]}")
            return []

    def _detect_city(self, text: str) -> str:
        text_lower = text.lower()
        for city in self.cities.keys():
            if city.lower() in text_lower:
                return city
        return "Unknown"

    def _get_state(self, city: str) -> str:
        return self.cities.get(city, {}).get("state", "")

    def _classify_severity(self, text: str) -> str:
        text_lower = text.lower()
        if any(h in text_lower for h in self._SEVERITY_HIGH):
            return "🔴 HIGH"
        elif any(m in text_lower for m in self._SEVERITY_MEDIUM):
            return "🟡 MEDIUM"
        else:
            return "🟢 LOW"

    def _classify_type(self, text: str) -> str:
        text_lower = text.lower()
        for keywords, strike_type in self._TYPE_MAP:
            if any(kw in text_lower for kw in keywords):
                return strike_type
        return "general"