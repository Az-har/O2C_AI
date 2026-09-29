# 🚀 O2C AI Monitor: Dual-Engine Order-to-Cash Process Intelligence

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Process Intelligence](https://img.shields.io/badge/Process_Mining-Celonis%20%7C%20OCPM-2563EB?style=flat-square)](https://celonis.com)
[![ERP Domain](https://img.shields.io/badge/ERP-SAP%20O2C-000000?style=flat-square)](https://sap.com)
[![ML Framework](https://img.shields.io/badge/ML-Gradient_Boosting%20%7C%20Random_Forest-orange?style=flat-square)](https://scikit-learn.org)
[![RAG Architecture](https://img.shields.io/badge/RAG-ChromaDB%20%7C%20Embeddings-00A4EF?style=flat-square)](https://docs.trychroma.com/)

> **Enterprise Process Intelligence & Predictive Delivery Risk Platform**: Combines machine learning on SAP transactional data with semantic contract & policy retrieval to predict Order-to-Cash (O2C) delivery delays, quantify financial risk, and automate mitigation.

---

## 🏗️ High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     O2C AI MONITOR PIPELINE                     │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌────────────────────────┴────────────────────────┐
        │                                                 │
        ▼                                                 ▼
┌──────────────────┐                            ┌──────────────────┐
│   ENGINE A       │                            │   ENGINE B       │
│  Predictive ML   │                            │  RAG Knowledge   │
│                  │                            │                  │
│  • XGBoost / RF  │                            │  • ChromaDB      │
│  • SAP O2C Data  │◄─────────┐       ┌────────►│  • Enterprise SLA│
│  • Weather APIs  │          │       │         │  • Strike Docs   │
│  • Feature Eng   │          │       │         │  • Contract Pacts│
└──────────────────┘          │       │         └──────────────────┘
        │                     │       │                   │
        │                 ┌───┴───────┴───┐               │
        │                 │  ORCHESTRATOR │               │
        └────────────────►│  Integration  │◄──────────────┘
                          │  Logic & Risk │
                          └───────┬───────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │   ACTIONABLE OUTPUT    │
                      │                        │
                      │  • Financial Risk ($)  │
                      │  • Delay Probability   │
                      │  • Root Cause Analysis │
                      │  • SLA Penalty Alerts  │
                      └────────────────────────┘
```

---

## 🌟 Core Pillars

### 1. 🤖 Engine A: Predictive ML (Quantitative Forecasts)
- **Mathematical Delay Forecasting**: Trained on core SAP ERP sales and distribution tables (`VBAK` Sales Orders, `VBAP` Order Items, `LIKP` Deliveries, `LIPS` Delivery Items, `VBRK`/`VBRP` Billing).
- **External Feature Fusion**: Enriches ERP records with real-time and historical weather data across supply chain routes.
- **Explainability**: Computes localized feature importances and risk probabilities for high-risk delivery bottlenecks.

### 2. 📚 Engine B: Semantic RAG Knowledge Base (Qualitative Context)
- **Vectorized Contract & SLA Intelligence**: Chunks and indexes enterprise SLAs, customer tier policies, regional strike/disruption intelligence, and weather protocols into **ChromaDB**.
- **Contextual Reasoning**: Automatically pulls contractual grace periods, penalty clauses, and force majeure stipulations to cross-examine predicted delays.

### 3. ⚖️ Orchestrator & Risk Engine
- **Financial Penalty Calculation**: Synthesizes probability of delay from Engine A with contractual penalty clauses from Engine B to quantify exact dollar exposure ($).
- **Automated Root-Cause Diagnosis**: Classifies bottlenecks into operational, transport, weather, or supply failure modes.

### 4. ⚡ Production Batch Pipeline & Automated Validation
- **Scalable Batch Execution**: Automated daily scoring runs with vectorized feature processing and in-memory caching.
- **Continuous Validation**: Automated validation suite verifying relational schema integrity, ML model accuracy, and semantic retrieval.

---

## 📂 Project Structure

```bash
O2C_AI/
├── main_pipeline.py                                    # Primary execution and batch orchestration entrypoint
├── validate_modules.py                                 # End-to-end module validation and test suite
├── modules/                                            # Modular backend components
│   ├── database_manager.py                             # SQLite WAL database & schema manager
│   ├── ml_db_extension.py                              # SAP data ingestion & ML feature store
│   ├── predictive_engine.py                            # ML models (Random Forest & Gradient Boosting)
│   ├── rag_engine.py                                   # Hybrid BM25 & vector retrieval engine
│   ├── agentic_orchestrator.py                         # Multi-agent orchestrator & decision logic
│   ├── agent_specialists.py                            # Domain specialist agents
│   ├── action_execution_engine.py                      # Action Engine ERP write-backs & dispatchers
│   ├── weather_service.py                              # External route weather ingestion
│   └── news_service.py                                 # Strike & logistics disruption news scraper
├── india_monitor_data/                                 # Datasets, models, and policy intelligence
│   ├── models/                                         # Trained Gradient Boosting & RF model artifacts
│   └── rag/                                            # Knowledge documents & vector chunks
├── Input Files/                                        # Raw transactional SAP ERP extracts
└── ENGINE_A_B_README.md                                # In-depth technical architecture specification
```

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+
- Virtual environment (`venv` recommended)

### 1. Installation
```bash
git clone https://github.com/Az-har/O2C_AI.git
cd O2C_AI
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Main Pipeline
```bash
python Main.py
```

### 3. Run Engine A Standalone Demo
```bash
python engine_a_demo.py
```

### 4. Verify RAG Intelligence
```bash
python validate_rag_three_inputs.py
```

---

## 💼 Business Impact & Value Realization

- **DSO & Working Capital**: Minimizes uncollected receivables caused by billing disputes and delivery delays.
- **SLA Protection**: Proactively warns account managers before contractual delivery breach thresholds are crossed.
- **Operational Alignment**: Bridges the gap between ERP transactional operations (SAP) and intelligent process automation (Celonis).

---

<sub>Engineered by **Azhar** • Specialized in Celonis Process Mining, Data Engineering, and Applied AI.</sub>
