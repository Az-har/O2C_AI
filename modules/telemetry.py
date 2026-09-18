"""
Telemetry & OpenInference Tracing Harness (Improvement 5.5)

Provides structured APM tracing across LangGraph nodes, specialist agents, tool calls,
and LLM completion cycles. Instruments execution with standard OpenTelemetry spans
and exports local JSON traces for monitoring and audit inspection.
"""

import sys
import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Generator
from contextlib import contextmanager
from datetime import datetime

# Windows encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = PROJECT_ROOT / "india_monitor_data" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TRACE_FILE = LOGS_DIR / "agent_traces.jsonl"

# Attempt OpenTelemetry initialization
_OTEL_AVAILABLE = False
tracer = None

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("o2c_agent_copilot", "1.0.0")
    _OTEL_AVAILABLE = True
except Exception:
    _OTEL_AVAILABLE = False


class AgentTraceRecorder:
    """Thread-safe local JSONL span and event recorder for AI agent execution"""
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._spans = []
            return cls._instance

    def log_span(self, span_record: Dict[str, Any]) -> None:
        with self._lock:
            self._spans.append(span_record)
            if len(self._spans) > 500:
                self._spans.pop(0)
            try:
                with open(TRACE_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(span_record) + "\n")
            except Exception:
                pass

    def get_spans(self, limit: int = 50) -> list:
        with self._lock:
            return list(self._spans[-limit:])


_trace_recorder = AgentTraceRecorder()


@contextmanager
def trace_span(span_name: str, attributes: Optional[Dict[str, Any]] = None) -> Generator[Dict[str, Any], None, None]:
    """
    Context manager for measuring agent execution spans with structured latency,
    metadata, and error tracking. Emits to OpenTelemetry and local JSON traces.
    """
    start_time = time.time()
    span_data = {
        "span_name": span_name,
        "start_time": datetime.now().isoformat(),
        "attributes": attributes or {},
        "status": "RUNNING",
        "events": []
    }
    
    otel_span = None
    if _OTEL_AVAILABLE and tracer:
        try:
            otel_span = tracer.start_span(span_name)
            if attributes:
                for k, v in attributes.items():
                    otel_span.set_attribute(str(k), str(v) if not isinstance(v, (int, float, bool)) else v)
        except Exception:
            otel_span = None

    try:
        yield span_data
        span_data["status"] = "OK"
    except Exception as e:
        span_data["status"] = "ERROR"
        span_data["error"] = str(e)
        if otel_span:
            otel_span.record_exception(e)
        raise
    finally:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        span_data["duration_ms"] = duration_ms
        span_data["end_time"] = datetime.now().isoformat()
        if otel_span:
            try:
                otel_span.end()
            except Exception:
                pass
        _trace_recorder.log_span(span_data)


def trace_agent_action(agent_name: str, order_id: str, action_type: str = "reasoning"):
    """Trace a specific specialist agent decision or debate turn"""
    return trace_span(
        f"{agent_name}.{action_type}",
        attributes={
            "agent_name": agent_name,
            "order_id": str(order_id),
            "action_type": action_type,
            "component": "agent_specialist"
        }
    )


def trace_tool_call(tool_name: str, order_id: str = "", tool_args: Optional[Dict[str, Any]] = None):
    """Trace a single LangChain tool invocation with inputs and latency"""
    attrs = {
        "tool_name": tool_name,
        "order_id": str(order_id),
        "component": "agent_tool"
    }
    if tool_args:
        attrs["args_keys"] = list(tool_args.keys())
    return trace_span(f"tool.{tool_name}", attributes=attrs)


def get_recent_traces(limit: int = 50) -> list:
    """Retrieve recent in-memory agent execution traces"""
    return _trace_recorder.get_spans(limit)
