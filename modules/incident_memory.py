"""
Long-Term Episodic Incident Memory Store (Phase 6)
Provides persistent storage and semantic retrieval of past order resolutions,
dispute precedents, and carrier performance history using ChromaDB and dense embeddings.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

import chromadb
from chromadb.config import Settings

from modules.config import BASE_DIR

logger = logging.getLogger("IncidentMemory")

INCIDENT_MEMORY_DIR = BASE_DIR / "rag" / "incident_memory"


class EpisodicMemoryStore:
    """
    ChromaDB-backed Episodic Memory Store for Supply Chain Risk Resolutions.
    Persists historical incidents, root causes, approved mitigations,
    and carrier arbitration precedents for multi-agent retrieval.
    """

    def __init__(self, persist_dir: Optional[Path] = None):
        self.persist_dir = Path(persist_dir) if persist_dir else INCIDENT_MEMORY_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False, is_persistent=True)
        )
        self.collection = self.client.get_or_create_collection(
            name="o2c_incident_precedents",
            metadata={"description": "Historical order dispute and mitigation precedents"}
        )
        
        # Auto-seed initial precedents if collection is empty
        if self.collection.count() == 0:
            self.seed_default_precedents()

    def store_incident_resolution(
        self,
        order_id: str,
        carrier_name: str,
        dest_city: str,
        root_causes: List[str],
        resolution_summary: str,
        financial_impact_usd: float,
        approved_by: str = "Logistics Director",
        metadata_extra: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record an episodic incident resolution into ChromaDB.
        """
        doc_id = f"inc_{order_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        cause_str = ", ".join(root_causes) if isinstance(root_causes, list) else str(root_causes)
        
        document_text = (
            f"Order: {order_id} | Destination: {dest_city} | Carrier: {carrier_name} | "
            f"Root Causes: {cause_str} | Resolution: {resolution_summary} | "
            f"Financial Impact: ${financial_impact_usd:,.2f} USD | Approved by: {approved_by}"
        )
        
        metadata = {
            "order_id": str(order_id),
            "carrier_name": str(carrier_name),
            "dest_city": str(dest_city),
            "financial_impact_usd": float(financial_impact_usd),
            "approved_by": str(approved_by),
            "timestamp": datetime.now().isoformat()
        }
        if metadata_extra:
            for k, v in metadata_extra.items():
                if isinstance(v, (str, int, float, bool)):
                    metadata[k] = v

        self.collection.upsert(
            ids=[doc_id],
            documents=[document_text],
            metadatas=[metadata]
        )
        logger.info(f"Stored incident precedent for Order {order_id} in ChromaDB (ID: {doc_id})")
        return doc_id

    def query_precedents(
        self,
        query_text: str,
        carrier_name: Optional[str] = None,
        dest_city: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant historical incident precedents using semantic vector search.
        Filters by carrier or destination city if specified.
        """
        where_filter = None
        if carrier_name and dest_city:
            where_filter = {"$and": [{"carrier_name": carrier_name}, {"dest_city": dest_city}]}
        elif carrier_name:
            where_filter = {"carrier_name": carrier_name}
        elif dest_city:
            where_filter = {"dest_city": dest_city}

        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(top_k, max(1, self.collection.count())),
                where=where_filter
            )
        except Exception as e:
            logger.warning(f"Filtered query failed ({e}), retrying without metadata filter...")
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(top_k, max(1, self.collection.count()))
            )

        precedents = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0] if "distances" in results else [0.0] * len(docs)

            for i, doc in enumerate(docs):
                meta = metas[i] if i < len(metas) else {}
                dist = distances[i] if i < len(distances) else 0.0
                precedents.append({
                    "precedent_text": doc,
                    "order_id": meta.get("order_id", "HISTORICAL"),
                    "carrier_name": meta.get("carrier_name", "Unknown"),
                    "dest_city": meta.get("dest_city", "Unknown"),
                    "financial_impact_usd": meta.get("financial_impact_usd", 0.0),
                    "approved_by": meta.get("approved_by", "System Precedent"),
                    "relevance_distance": round(float(dist), 4),
                    "mitigation_action": meta.get("resolution_summary", doc[:100])
                })
        return precedents

    def query_similar_incidents(
        self,
        query_text: str,
        carrier_name: Optional[str] = None,
        dest_city: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Alias for query_precedents for semantic retrieval"""
        return self.query_precedents(query_text, carrier_name=carrier_name, dest_city=dest_city, top_k=top_k)

    def get_collection_stats(self) -> Dict[str, Any]:
        """Return statistics on the ChromaDB incident collection"""
        return {
            "collection_name": self.collection.name,
            "record_count": self.collection.count(),
            "vector_db_path": str(self.persist_dir)
        }

    def seed_default_precedents(self) -> None:
        """Seed initial authoritative supply chain precedents into ChromaDB"""
        initial_precedents = [
            {
                "order_id": "PREC_2025_001",
                "carrier_name": "DHL Supply Chain",
                "dest_city": "Mumbai",
                "root_causes": ["Severe monsoon flooding", "Waterlogged terminal dock"],
                "resolution_summary": "Invoked Master Agreement Section 8.1 Force Majeure. 100% customer delay SLA penalty waived. Carrier granted 48h arrival extension without penalty.",
                "financial_impact_usd": 0.0,
                "approved_by": "VP Supply Chain"
            },
            {
                "order_id": "PREC_2025_002",
                "carrier_name": "SafeLogistics Express",
                "dest_city": "Delhi",
                "root_causes": ["Telematics disconnected >14 hours", "Carrier failure to report tracking outage"],
                "resolution_summary": "Assessed $200 blind-tracking penalty against carrier AP ledger. Invalidation of Force Majeure defense due to telematics breach.",
                "financial_impact_usd": 200.0,
                "approved_by": "Regional Logistics Director"
            },
            {
                "order_id": "PREC_2025_003",
                "carrier_name": "BlueDart Surface",
                "dest_city": "Hyderabad",
                "root_causes": ["Extreme heatwave >42°C", "Veterinary prescription diet thermal threshold breach"],
                "resolution_summary": "Authorized $1,000 emergency replacement air shipment from Bangalore hub. Placed road consignment on SAP QA quarantine hold '01' for lab potency testing.",
                "financial_impact_usd": 1000.0,
                "approved_by": "Quality Assurance Director"
            },
            {
                "order_id": "PREC_2025_004",
                "carrier_name": "Gati KWE",
                "dest_city": "Chennai",
                "root_causes": ["Port dockworkers strike", "Corridor highway blockade NH-16"],
                "resolution_summary": "Proactive 12-hour warning dispatched to 14 veterinary clinics. Applied 50% liquidated damages credit under Clause 4.2.",
                "financial_impact_usd": 450.0,
                "approved_by": "Senior Operations Manager"
            },
            {
                "order_id": "PREC_2025_005",
                "carrier_name": "Transport Corp of India (TCI)",
                "dest_city": "Bangalore",
                "root_causes": ["Receiving dock overtime violation", "Arrival after 17:30 closing window"],
                "resolution_summary": "Assessed $150 redelivery fee charged back to carrier via debit memo. Consignee delivery rescheduled for 09:00 next business day.",
                "financial_impact_usd": 150.0,
                "approved_by": "Receiving Dock Supervisor"
            }
        ]

        for p in initial_precedents:
            self.store_incident_resolution(
                order_id=p["order_id"],
                carrier_name=p["carrier_name"],
                dest_city=p["dest_city"],
                root_causes=p["root_causes"],
                resolution_summary=p["resolution_summary"],
                financial_impact_usd=p["financial_impact_usd"],
                approved_by=p["approved_by"]
            )
        logger.info(f"Seeded {len(initial_precedents)} default incident precedents into ChromaDB")


_episodic_store_instance: Optional[EpisodicMemoryStore] = None


def get_incident_memory_store() -> EpisodicMemoryStore:
    """Returns the singleton instance of EpisodicMemoryStore"""
    global _episodic_store_instance
    if _episodic_store_instance is None:
        _episodic_store_instance = EpisodicMemoryStore()
    return _episodic_store_instance

