# 🚀 O2C AI Monitor: Dual-Engine Order-to-Cash Process Intelligence

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Databricks](https://img.shields.io/badge/Platform-Databricks-FF3621?style=flat-square&logo=databricks&logoColor=white)](https://databricks.com)
[![Process Intelligence](https://img.shields.io/badge/Domain-Celonis%20%7C%20SAP%20O2C-000000?style=flat-square&logo=celonis&logoColor=white)](https://celonis.com)
[![ML Framework](https://img.shields.io/badge/ML-XGBoost%20%7C%20Random%20Forest-orange?style=flat-square)](https://xgboost.readthedocs.io/)
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

### 4. ⚡ Databricks Enterprise Pipeline
- **Master Batch Orchestration**: `O2C_AI_Databricks_Master.py` / `.ipynb` runs scalable daily scoring jobs with vectorized batch inference and environmental memory caching.
- **Continuous Evaluation**: Multi-input RAG validation scripts (`validate_rag_three_inputs.py`, `check_ml_evaluation.py`) ensure production accuracy and prevent hallucination.

---

## 📂 Project Structure

```bash
O2C_AI/
├── Main.py                                             # Primary CLI orchestration entrypoint
├── O2C_AI_Databricks_Master.py                         # Production Databricks pipeline script
├── O2C_AI_Databricks_Master.ipynb                      # Databricks interactive notebook
├── databricks_daily_job.py                             # Scheduled daily batch scoring job
├── build_databricks_master.py                          # Build generator for Databricks artifacts
├── check_ml_evaluation.py                              # ML performance evaluation suite
├── validate_rag_three_inputs.py                        # RAG multi-vector retrieval verification
├── engine_a_demo.py                                    # Standalone Engine A predictive demo
├── modules/                                            # Modular backend components
│   ├── engine_a_predictor.py                           # ML feature extraction & scoring
│   ├── engine_b_rag.py                                 # ChromaDB semantic retrieval engine
│   ├── weather_fetcher.py                              # External route weather ingestion
│   └── risk_scorer.py                                  # Financial SLA risk scoring
├── india_monitor_data/                                 # Datasets, models, and policy intelligence
│   ├── models/                                         # Trained XGBoost & RF model artifacts
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
