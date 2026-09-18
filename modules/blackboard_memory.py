"""
Blackboard Memory - Hierarchical Multi-Tier Working Memory (Improvement 5.4)

Provides a shared, thread-safe in-process cluster memory across active agent threads
within the same execution cycle. Allows specialist agents processing different orders
to share real-time operational discoveries (e.g. active corridor blockages, temporary
carrier holds, regional facility congestion) without redundant API or database queries.
"""

import threading
import time
from typing import Dict, Any, Optional, List
from datetime import datetime


class BlackboardMemory:
    """
    Cluster working memory singleton shared across active agent worker threads.
    Thread-safe implementation with fine-grained locking.
    """
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._corridor_hazards: Dict[str, Dict[str, Any]] = {}
                cls._instance._carrier_status: Dict[str, Dict[str, Any]] = {}
                cls._instance._regional_holds: Dict[str, Dict[str, Any]] = {}
                cls._instance._active_mitigations: Dict[str, Dict[str, Any]] = {}
                cls._instance._audit_events: List[Dict[str, Any]] = []
            return cls._instance

    def publish_corridor_hazard(self, corridor_or_city: str, hazard_details: Dict[str, Any]) -> None:
        """Publish a discovered weather or transport hazard on a corridor or city hub"""
        key = corridor_or_city.strip().lower()
        with self._lock:
            entry = {
                "corridor": corridor_or_city,
                "hazard_details": hazard_details,
                "discovered_at": datetime.now().isoformat(),
                "timestamp": time.time()
            }
            self._corridor_hazards[key] = entry
            self._audit_events.append({
                "type": "CORRIDOR_HAZARD_PUBLISHED",
                "key": key,
                "timestamp": entry["discovered_at"],
                "summary": hazard_details.get("summary", str(hazard_details))
            })

    def get_corridor_hazard(self, corridor_or_city: str) -> Optional[Dict[str, Any]]:
        """Retrieve active corridor hazard by city or corridor name"""
        key = corridor_or_city.strip().lower()
        with self._lock:
            return self._corridor_hazards.get(key)

    def publish_carrier_status(self, carrier_name: str, status_details: Dict[str, Any]) -> None:
        """Publish real-time operational status (e.g. telematics drop, strike involvement) of a carrier"""
        key = carrier_name.strip().lower()
        with self._lock:
            entry = {
                "carrier": carrier_name,
                "status_details": status_details,
                "recorded_at": datetime.now().isoformat(),
                "timestamp": time.time()
            }
            self._carrier_status[key] = entry
            self._audit_events.append({
                "type": "CARRIER_STATUS_PUBLISHED",
                "key": key,
                "timestamp": entry["recorded_at"],
                "summary": status_details.get("status", "UPDATED")
            })

    def get_carrier_status(self, carrier_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve real-time status of a carrier"""
        key = carrier_name.strip().lower()
        with self._lock:
            return self._carrier_status.get(key)

    def publish_regional_hold(self, region_or_facility: str, hold_details: Dict[str, Any]) -> None:
        """Publish regional receiving dock quarantine or regulatory hold"""
        key = region_or_facility.strip().lower()
        with self._lock:
            entry = {
                "facility": region_or_facility,
                "hold_details": hold_details,
                "created_at": datetime.now().isoformat(),
                "timestamp": time.time()
            }
            self._regional_holds[key] = entry
            self._audit_events.append({
                "type": "REGIONAL_HOLD_PUBLISHED",
                "key": key,
                "timestamp": entry["created_at"]
            })

    def get_regional_hold(self, region_or_facility: str) -> Optional[Dict[str, Any]]:
        """Retrieve active regional hold details"""
        key = region_or_facility.strip().lower()
        with self._lock:
            return self._regional_holds.get(key)

    def get_all_hazards(self) -> Dict[str, Any]:
        """Return all active corridor hazards"""
        with self._lock:
            return dict(self._corridor_hazards)

    def get_all_state(self) -> Dict[str, Any]:
        """Snapshot of entire blackboard memory state"""
        with self._lock:
            return {
                "corridor_hazards": dict(self._corridor_hazards),
                "carrier_status": dict(self._carrier_status),
                "regional_holds": dict(self._regional_holds),
                "active_mitigations": dict(self._active_mitigations),
                "event_count": len(self._audit_events),
                "recent_audit_events": list(self._audit_events[-10:])
            }

    def clear(self) -> None:
        """Reset blackboard memory (e.g. between daily batches or tests)"""
        with self._lock:
            self._corridor_hazards.clear()
            self._carrier_status.clear()
            self._regional_holds.clear()
            self._active_mitigations.clear()
            self._audit_events.clear()


# Global module-level convenience instance
_global_blackboard = BlackboardMemory()

def get_blackboard_memory() -> BlackboardMemory:
    return _global_blackboard
