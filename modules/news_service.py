"""
Global Multimodal Transportation Disruption Intelligence Service

Enterprise-grade news scraper and NLP extraction engine for O2C AI.
Fetches, classifies, and tracks transportation disruptions worldwide across:
- Maritime / Ocean Shipping & Seaports
- Strategic Trade Canals & Maritime Chokepoints
- Air Freight & Cargo Aviation
- Rail Freight & Intermodal Transport
- Road Freight, Trucking & Highway Corridors
- Customs, Border Crossings & Regulatory Halts
- Cyberattacks & Severe Weather Impacting Logistics Infrastructure
"""

import re
import html
import time
import urllib.parse
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from modules.config import (
    GLOBAL_AIR_HUBS,
    GLOBAL_CHOKEPOINTS,
    GLOBAL_COUNTRIES,
    GLOBAL_DISRUPTION_QUERIES,
    GLOBAL_PORTS,
    INDIA_CITIES,
    STRIKE_KEYWORDS,
)

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


class GlobalTransportDisruptionNewsService:
    """
    Scrapes and classifies multimodal global transportation disruptions from Google News RSS feeds.
    Detects transport mode, disruption category, severity level, affected countries, hubs, and chokepoints.
    """

    RSS_SEARCH_URL = "https://news.google.com/rss/search"

    # ── High-Precision Keyword Taxonomies for NLP Extraction ────────────────

    MODE_PATTERNS = [
        ("Canal / Chokepoint", [
            r"\bsuez\b", r"\bpanama canal\b", r"\bred sea\b", r"\bbab[- ]el[- ]mandeb\b",
            r"\bhormuz\b", r"\bmalacca\b", r"\bdover\b", r"\bbosphorus\b",
            r"\brhine\b", r"\bmississippi\b", r"\bchokepoint\b", r"\bwaterway\b",
            r"\bgibraltar\b", r"\briver shipping\b", r"\bbarge halt\b"
        ]),
        ("Maritime / Ocean Port", [
            r"\bport\b", r"\bseaport\b", r"\bdock\b", r"\bdocks\b", r"\bdockworker\b",
            r"\blongshoreman\b", r"\blongshoremen\b", r"\bstevedore\b", r"\bterminal\b",
            r"\bcontainer ship\b", r"\bvessel\b", r"\bmaritime\b", r"\bocean carrier\b",
            r"\bberth\b", r"\bberthing\b", r"\bquay\b", r"\bshipping line\b",
            r"\bila\b", r"\bilwu\b", r"\bjoc\b", r"\bblank sailing\b", r"\bteu\b",
            r"\bfreight ship\b", r"\bcargo ship\b", r"\bport closure\b", r"\bport closed\b",
            r"\bquayside\b", r"\bstorm surge\b"
        ]),
        ("Air Freight", [
            r"\bair cargo\b", r"\bair freight\b", r"\bcargo flight\b", r"\bfreighter\b",
            r"\bairport\b", r"\bairports\b", r"\bground handler\b", r"\bground handling\b",
            r"\bair traffic control\b", r"\batc\b", r"\bfaa\b",
            r"\bground stop\b", r"\bground delay\b", r"\bbaggage handler\b",
            r"\baviation\b", r"\bbelly cargo\b", r"\bnotam\b", r"\blufthansa cargo\b",
            r"\bfedex\b", r"\bups\b", r"\bdhl aviation\b", r"\bvolcanic ash\b",
            r"\bairspace closed\b", r"\brunway closed\b", r"\bflight cancellation\b"
        ]),
        ("Rail Freight", [
            r"\brail\b", r"\brailway\b", r"\bfreight rail\b", r"\blocomotive\b",
            r"\btrain derailment\b", r"\bderailment\b", r"\brailroad\b",
            r"\bintermodal rail\b", r"\brail freight\b", r"\brail yard\b",
            r"\bunion pacific\b", r"\bbnsf\b", r"\bcsx\b", r"\bnorfolk southern\b",
            r"\bdeutsche bahn\b", r"\brail cargo\b", r"\btrack washout\b",
            r"\brail line closed\b", r"\btrain track\b"
        ]),
        ("Road / Trucking", [
            r"\btruck\b", r"\btrucker\b", r"\btruckers\b", r"\btrucking\b",
            r"\blorry\b", r"\blorries\b", r"\bhighway\b", r"\binterstate\b",
            r"\broad blockade\b", r"\bchakka jam\b", r"\bdiesel shortage\b",
            r"\bfuel tanker\b", r"\bowner[- ]operator\b", r"\bteamster\b",
            r"\bdrayage\b", r"\bmotor freight\b", r"\bhaulage\b", r"\bconvoy\b",
            r"\btransport strike\b", r"\bbus strike\b", r"\bauto strike\b",
            r"\bbandh\b", r"\bhartal\b", r"\bmountain pass closed\b",
            r"\bhighway closed\b", r"\broad closed\b", r"\bfreeway closed\b"
        ]),
        ("Border / Customs", [
            r"\bcustoms\b", r"\bborder crossing\b", r"\bborder checkpoint\b",
            r"\bborder patrol\b", r"\bcustoms officer\b", r"\bcustoms strike\b",
            r"\btrade embargo\b", r"\bimport ban\b", r"\bexport restriction\b",
            r"\btariffs\b", r"\bsanctions\b", r"\bport of entry\b"
        ]),
        ("Multimodal / Logistics", [
            r"\bsupply chain\b", r"\blogistics\b", r"\bfreight\b", r"\bcargo\b",
            r"\bintermodal\b", r"\bwarehouse\b", r"\bdistribution center\b"
        ]),
    ]

    CATEGORY_PATTERNS = [
        ("Natural Disaster / Severe Weather", [
            # Tropical Cyclones & Hurricanes
            r"\btyphoons?\b", r"\bhurricanes?\b", r"\bcyclones?\b", r"\btropical storms?\b",
            r"\bgale force\b", r"\bstorm surge\b",
            # Floods & Inundation
            r"\bflash floods?\b", r"\bflooding\b", r"\bfloods?\b", r"\binundation\b",
            r"\btrack washout\b", r"\bwashouts?\b", r"\briver overflow\b", r"\bsubmerged\b",
            # Earthquakes & Tsunamis
            r"\bearthquakes?\b", r"\btsunamis?\b", r"\btremors?\b", r"\bseismic\b",
            r"\bliquefaction\b",
            # Volcanic Hazards
            r"\bvolcanic ash\b", r"\bvolcanoes?\b", r"\bvolcanos?\b", r"\bash clouds?\b",
            r"\beruptions?\b",
            # Winter Extremes & Snow
            r"\bblizzards?\b", r"\bwinter storms?\b", r"\bice storms?\b", r"\bfreezing rain\b",
            r"\bpolar vortex\b", r"\bsnowstorms?\b", r"\bheavy snow\b", r"\bavalanches?\b",
            r"\bfrozen waterway\b", r"\bwinter freeze\b",
            # Wildfires & Smoke
            r"\bwildfires?\b", r"\bforest fires?\b", r"\bbushfires?\b", r"\bsmoke haze\b",
            # Landslides & Mass Movement
            r"\blandslides?\b", r"\bmudslides?\b", r"\brockfalls?\b", r"\brockslides?\b",
            # Droughts & Water Shortages
            r"\bdroughts?\b", r"\blow water\b", r"\bshallow water\b", r"\bwater level drop\b"
        ]),
        ("Cyber / IT Outage", [
            r"\bcyberattack\b", r"\bransomware\b", r"\bsystem outage\b",
            r"\bit failure\b", r"\bterminal operating system\b", r"\bnetwork down\b",
            r"\bcustoms software crash\b", r"\bserver outage\b"
        ]),
        ("Geopolitical / Security Threat", [
            r"\bmissile\b", r"\bdrone attack\b", r"\bhouthi\b", r"\bwar risk\b",
            r"\bpiracy\b", r"\bhostile\b", r"\bnaval blockade\b", r"\barmed conflict\b",
            r"\bairspace closed\b", r"\bseizure\b", r"\bmilitary strike\b"
        ]),
        ("Infrastructure / Accident", [
            r"\bderailment\b", r"\bbridge collapse\b", r"\bcrane collapse\b",
            r"\btrack damage\b", r"\bfire\b", r"\bexplosion\b", r"\bcollision\b",
            r"\bstructural failure\b", r"\bpower outage\b", r"\bsignaling fault\b"
        ]),
        ("Canal / Chokepoint Blockage", [
            r"\bcanal blocked\b", r"\bgrounded\b", r"\bdrought restriction\b",
            r"\bwaterway closed\b", r"\bsuspended transit\b", r"\brerouted around\b",
            r"\bcape of good hope\b", r"\btransits halted\b", r"\bshallow water\b"
        ]),
        ("Labor Strike / Walkout", [
            r"\bstrike\b", r"\bwalkout\b", r"\bprotest\b", r"\bpicketing\b",
            r"\bindustrial action\b", r"\bwork[- ]to[- ]rule\b", r"\bunion action\b",
            r"\bbandh\b", r"\bhartal\b", r"\bchakka jam\b", r"\bdown tools\b",
            r"\blabor dispute\b", r"\bstop work\b", r"\bblockade\b", r"\bblockades\b",
            r"\bblockading\b", r"\btruck convoy\b"
        ]),
        ("Customs / Regulatory Delay", [
            r"\bcustoms delay\b", r"\binspection backlog\b", r"\bborder closure\b",
            r"\bclearance halt\b", r"\btrade embargo\b", r"\bsanction\b",
            r"\bquarantine hold\b", r"\bimport freeze\b", r"\binspection delays?\b",
            r"\bborder delays?\b"
        ]),
        ("Port / Terminal Congestion", [
            r"\bcongestion\b", r"\bbacklog\b", r"\bvessel queue\b", r"\bdwell time\b",
            r"\bberth delay\b", r"\bgridlock\b", r"\bbottleneck\b", r"\byard density\b",
            r"\bovercapacity\b"
        ]),
    ]

    SEVERITY_HIGH_TERMS = [
        "complete shutdown", "indefinite strike", "indefinite", "national strike",
        "canal blocked", "port closed", "all flights grounded", "ground stop",
        "catastrophic", "bridge collapse", "force majeure", "state of emergency",
        "unlimited strike", "paralyzed", "total shutdown", "halted indefinitely",
        "severe disruption", "blank sailings surge"
    ]

    SEVERITY_MEDIUM_TERMS = [
        "24-hour", "48-hour", "48h", "24h", "state bandh", "city strike",
        "delays", "disruption", "congestion", "backlog", "draft restrictions",
        "rerouted", "transit cuts", "warning issued", "slowdown", "protest planned",
        "strike ballot", "derailment delay"
    ]

    # Pre-compiled high-performance alternation regex sets
    COMPILED_MODE_PATTERNS = [
        (mode, re.compile("|".join(patterns), re.IGNORECASE))
        for mode, patterns in MODE_PATTERNS
    ]

    COMPILED_CATEGORY_PATTERNS = [
        (cat, re.compile("|".join(patterns), re.IGNORECASE))
        for cat, patterns in CATEGORY_PATTERNS
    ]

    def __init__(
        self,
        keywords: Optional[List[str]] = None,
        cities: Optional[Dict[str, Any]] = None,
        disruption_query_matrix: Optional[Dict[str, List[str]]] = None,
        global_ports: Optional[Dict[str, Any]] = None,
        global_air_hubs: Optional[Dict[str, Any]] = None,
        global_chokepoints: Optional[Dict[str, Any]] = None,
        global_countries: Optional[Dict[str, Any]] = None,
    ):
        self.keywords = keywords or STRIKE_KEYWORDS
        self.cities = cities or INDIA_CITIES
        self.query_matrix = disruption_query_matrix or GLOBAL_DISRUPTION_QUERIES
        self.global_ports = global_ports or GLOBAL_PORTS
        self.global_air_hubs = global_air_hubs or GLOBAL_AIR_HUBS
        self.global_chokepoints = global_chokepoints or GLOBAL_CHOKEPOINTS
        self.global_countries = global_countries or GLOBAL_COUNTRIES

        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 O2C-Disruption-Monitor/2.0"
        })

    def fetch(
        self,
        date: Optional[str] = None,
        city: Optional[str] = None,
        max_articles_per_query: int = 8,
        mode_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch multimodal disruption news across international trade corridors.
        
        Args:
            date: Optional date filter (YYYY-MM-DD).
            city: Optional specific hub / city to focus on.
            max_articles_per_query: Maximum articles returned per Google News query.
            mode_filter: Optional filter by transport mode (e.g. 'ocean', 'air', 'rail').
        """
        queries_to_run = self._compile_query_list(city=city, mode_filter=mode_filter)
        date_filter = self._date_filter(date) if date else ""

        raw_articles: List[Dict[str, Any]] = []
        seen_keys: Set[str] = set()

        # Execute queries concurrently (up to 4 worker threads for fast low-latency ingestion)
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_map = {}
            for query_text in queries_to_run:
                full_q = f"{query_text} {date_filter}".strip()
                future = executor.submit(self._execute_rss_query, full_q, max_articles_per_query)
                future_map[future] = query_text

            for future in as_completed(future_map):
                query_text = future_map[future]
                try:
                    results = future.result()
                    for item in results:
                        title_norm = re.sub(r"[^a-zA-Z0-9]", "", item.get("title", "").lower()[:70])
                        if title_norm and title_norm not in seen_keys:
                            seen_keys.add(title_norm)
                            raw_articles.append(item)
                except Exception as e:
                    pass

        # Enrich and classify each multimodal article
        enriched_articles: List[Dict[str, Any]] = []
        for article in raw_articles:
            combined_text = f"{article.get('title', '')} {article.get('description', '')}"

            transport_mode = self._classify_transport_mode(combined_text)
            disruption_category = self._classify_disruption_category(combined_text)
            severity = self._classify_severity(combined_text, transport_mode, disruption_category)
            geo_info = self._detect_geography(combined_text)

            article["transport_mode"] = transport_mode
            article["disruption_category"] = disruption_category
            article["severity"] = severity
            article["country_mentioned"] = geo_info["country"]
            article["city_mentioned"] = geo_info["hub"]
            article["state_mentioned"] = geo_info["state"]
            article["strike_type"] = self._map_legacy_strike_type(transport_mode, disruption_category)
            article["scraped_at"] = datetime.now().isoformat()

            enriched_articles.append(article)

        return enriched_articles

    def _compile_query_list(self, city: Optional[str] = None, mode_filter: Optional[str] = None) -> List[str]:
        """Compile optimized query list from the multimodal matrix"""
        compiled: List[str] = []

        if city:
            # Targeted city/hub query
            compiled.append(f"{city} port congestion OR {city} transport strike")
            compiled.append(f"{city} airport cargo disruption OR {city} freight blockade")
            return compiled

        # Multimodal global queries
        for category, queries in self.query_matrix.items():
            if mode_filter and mode_filter.lower() not in category.lower():
                continue
            compiled.extend(queries)

        return compiled

    def _execute_rss_query(self, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Execute single RSS search with international English parameters"""
        params = {
            "q": query,
            "hl": "en-US",
            "gl": "US",
            "ceid": "US:en"
        }
        try:
            resp = self._session.get(self.RSS_SEARCH_URL, params=params, timeout=12)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.content, "html.parser")
            items = soup.find_all("item")[:max_items]

            articles = []
            for it in items:
                title_text = it.title.text if it.title else ""
                desc_text = it.description.text if it.description else ""
                
                # Clean html tags from description
                desc_clean = re.sub(r"<[^>]+>", "", desc_text)
                desc_clean = html.unescape(desc_clean).strip()

                url_text = it.link.text if it.link else ""
                source_text = it.source.text if it.source else "News Agency"
                pub_date = it.pubDate.text if it.pubDate else ""

                articles.append({
                    "title": html.unescape(title_text).strip(),
                    "description": desc_clean[:2000],
                    "url": url_text.strip(),
                    "source_name": source_text.strip(),
                    "published_date": pub_date.strip(),
                    "keyword_matched": query[:60]
                })

            return articles

        except Exception as e:
            return []

    def _date_filter(self, date_str: str) -> str:
        """Create date boundary filter for Google RSS search"""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return f"after:{dt.strftime('%Y-%m-%d')} before:{dt.strftime('%Y-%m-%d')}"
        except Exception:
            return ""

    def _classify_transport_mode(self, text: str) -> str:
        """Extract primary transportation mode from text using fast pre-compiled regexes"""
        for mode, compiled_pat in self.COMPILED_MODE_PATTERNS:
            if compiled_pat.search(text):
                return mode
        return "Multimodal Logistics"

    def _classify_disruption_category(self, text: str) -> str:
        """Extract primary disruption cause category using fast pre-compiled regexes"""
        for cat, compiled_pat in self.COMPILED_CATEGORY_PATTERNS:
            if compiled_pat.search(text):
                return cat
        return "Operational Disruption"

    def _classify_severity(self, text: str, mode: str, category: str) -> str:
        """Score disruption severity with transport mode context"""
        t_low = text.lower()

        # 1. Critical triggers
        if any(term in t_low for term in self.SEVERITY_HIGH_TERMS):
            return "🔴 HIGH"

        # Strategic Chokepoints or Missile Attacks default to High if blocking traffic
        if mode == "Canal / Chokepoint" and any(k in t_low for k in ["block", "ground", "halt", "missile", "drought", "suspend"]):
            return "🔴 HIGH"

        # 2. Medium triggers
        if any(term in t_low for term in self.SEVERITY_MEDIUM_TERMS):
            return "🟡 MEDIUM"

        # Natural Disaster severity scoring
        if category == "Natural Disaster / Severe Weather":
            if any(k in t_low for k in [
                "closure", "closed", "grounded", "shutdown", "halted", "evacuation",
                "landfall", "catastrophic", "major", "tsunami", "earthquake", "volcanic ash",
                "blizzard", "washout", "emergency", "state of emergency", "damage", "cancel", "pass closed"
            ]):
                return "🔴 HIGH"
            return "🟡 MEDIUM"

        if category in ["Labor Strike / Walkout", "Port / Terminal Congestion", "Infrastructure / Accident"]:
            return "🟡 MEDIUM"

        # 3. Default advisory
        return "🟢 LOW"

    def _detect_geography(self, text: str) -> Dict[str, str]:
        """Detect country, port/airport hub, and domestic state mentioned in text"""
        t_low = text.lower()

        detected_country = "Global"
        detected_hub = "International Freight Network"
        detected_state = ""

        # 1. Check Chokepoints
        for chokepoint, meta in self.global_chokepoints.items():
            if chokepoint.lower() in t_low:
                return {
                    "country": meta.get("region", "Global Corridor"),
                    "hub": chokepoint,
                    "state": "Strategic Chokepoint"
                }

        # 2. Check Global Ports
        for port, meta in self.global_ports.items():
            if re.search(rf"\b{re.escape(port.lower())}\b", t_low):
                detected_hub = f"Port of {port}"
                detected_country = meta.get("country", "Global")
                detected_state = meta.get("region", "")
                break

        # 3. Check Global Air Hubs
        if detected_hub == "International Freight Network":
            for air_hub, meta in self.global_air_hubs.items():
                if re.search(rf"\b{re.escape(air_hub.lower())}\b", t_low):
                    detected_hub = f"{air_hub} Airport"
                    detected_country = meta.get("country", "Global")
                    detected_state = meta.get("type", "")
                    break

        # 4. Check Domestic Indian Cities
        if detected_hub == "International Freight Network":
            for city_name, meta in self.cities.items():
                if re.search(rf"\b{re.escape(city_name.lower())}\b", t_low):
                    detected_hub = city_name
                    detected_country = "India"
                    detected_state = meta.get("state", "")
                    break

        # 5. Check Global Countries if country not yet resolved
        if detected_country == "Global":
            for country, aliases in self.global_countries.items():
                if re.search(rf"\b{re.escape(country.lower())}\b", t_low) or any(
                    re.search(rf"\b{re.escape(a.lower())}\b", t_low) for a in aliases
                ):
                    detected_country = country
                    break

        return {
            "country": detected_country,
            "hub": detected_hub,
            "state": detected_state
        }

    def _map_legacy_strike_type(self, transport_mode: str, category: str) -> str:
        """Provide clean backward compatibility for legacy strike_type field"""
        if "Maritime" in transport_mode or "Port" in transport_mode:
            return "ocean_port"
        elif "Air" in transport_mode:
            return "air_freight"
        elif "Rail" in transport_mode:
            return "railway"
        elif "Road" in transport_mode or "Trucking" in transport_mode:
            return "truck"
        elif "Canal" in transport_mode:
            return "canal_chokepoint"
        elif "Border" in transport_mode:
            return "customs_border"
        elif "Natural Disaster" in category:
            return "natural_disaster"
        elif "Strike" in category:
            return "strike"
        return "general"


# Backward-compatible alias so existing orchestrators and imports work without modification
NewsService = GlobalTransportDisruptionNewsService