# 🚀 Dual AI Engine Architecture: Engine A + Engine B

## 📋 Overview

The O2C AI Monitor implements a **Dual AI Engine** approach for delivery delay prediction and risk assessment:

- **Engine A (Predictive ML)**: Mathematical prediction of delivery delays using machine learning on SAP transactional data
- **Engine B (RAG Knowledge Base)**: Semantic retrieval of business policies, SLAs, and contracts using Retrieval-Augmented Generation
- **Integration**: Combines quantitative predictions with qualitative business rules for actionable insights

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     O2C AI MONITOR PIPELINE                     │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
        ┌────────────────────────┴────────────────────────┐
        │                                                  │
        ▼                                                  ▼
┌──────────────────┐                            ┌──────────────────┐
│   ENGINE A       │                            │   ENGINE B       │
│  Predictive ML   │                            │  RAG Knowledge   │
│                  │                            │                  │
│  • XGBoost/RF    │                            │  • ChromaDB      │
│  • SAP Data      │◄──────┐         ┐────────►│  • Policies      │
│  • Weather API   │        │         │         │  • SLAs          │
│  • Feature Eng   │        │         │         │  • Contracts     │
└──────────────────┘        │         │         └──────────────────┘
        │                   │         │                  │
        │               ┌───┴─────────┴───┐             │
        │               │  ORCHESTRATOR   │             │
        └──────────────►│  Integration    │◄────────────┘
                        │  Logic          │
                        └───────┬─────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │   ACTIONABLE OUTPUT    │
                    │                        │
                    │  • Financial Risk ($)  │
                    │  • Root Cause          │
                    │  • Recommendations     │
                    │  • SLA Penalties       │
                    └────────────────────────┘
```

---

## 🤖 Engine A: Predictive ML

### Purpose
Predict **when** deliveries will be delayed and **why**, using mathematical models trained on historical data.

### Data Sources
1. **SAP Tables** (from `/Input Files/`):
   - `VBAK` - Sales Orders
   - `VBAP` - Order Items
   - `LIKP` - Deliveries
   - `LIPS` - Delivery Items
   - `VTTK` - Shipments
   - `VTTP` - Shipment Items
   - `KNA1` - Customer Master
   - `KNVV` - Customer Sales Data
   - `LFA1` - Carrier/Vendor Master
   - `MARA` - Material Master

2. **Weather API** (OpenWeather):
   - Real-time weather conditions
   - Storm alerts and disruptions

### ML Models
- **Classifier**: Random Forest → Will it be delayed? (Yes/No)
- **Regressor**: Gradient Boosting → How many hours delayed?

### Engineered Features
```python
feature_cols = [
    'order_to_delivery_days',      # Lead time
    'order_to_departure_days',     # Planning time
    'days_since_order',            # Age
    'days_until_delivery',         # Urgency
    'total_quantity',              # Volume
    'total_weight',                # Weight
    'weight_per_unit',             # Density
    'is_heavy_shipment',           # Heavy flag
    'has_specialty_diet',          # Critical item flag
    'min_shelf_life',              # Perishability
    'customer_tier_code',          # Priority (Platinum/Gold/Silver)
    'shipping_risk_code',          # Mode risk (FTL/LTL/Air)
    'status_code'                  # Current status
]
```

### Output
```python
{
    "predicted_eta": "2026-06-15 14:30",
    "delay_probability": 0.72,
    "delay_hours": 48.5,
    "will_be_delayed": True,
    "root_cause": "Severe weather (heavy rain); LTL consolidation delays"
}
```

---

## 📚 Engine B: RAG Knowledge Base

### Purpose
Retrieve **business rules** that govern how to handle predicted delays: What penalties apply? What exceptions exist?

### Knowledge Sources
1. **Weather Policies** (generated documents):
   - Force Majeure clauses
   - Weather exception rules
   - Storm response procedures

2. **Strike Intelligence** (news-based documents):
   - Labor disruption impacts
   - Alternative routing recommendations

3. **Customer SLAs** (future integration):
   - Delivery time windows
   - Penalty matrices by tier
   - After-hours delivery policies

4. **Vendor Contracts** (future integration):
   - Carrier liability rules
   - Insurance coverage
   - Service level commitments

### Technology Stack
- **Vector Store**: ChromaDB / FAISS
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Chunking**: Recursive character split (500 chars, 100 overlap)

### Query Process
```python
# Engine A provides context
query = f"""
Customer: Banfield Pet Hospital (Tier: Platinum)
Carrier: FedEx Freight
Predicted Delay: 52 hours
Weather Risk: High (Level 4 blizzard)

What are the SLA penalties, delivery time windows, and 
force majeure clauses that apply?
"""

# Engine B retrieves policies
rag_response = rag_engine.query(query)
```

### Output
```python
{
    "policies": [
        "Platinum tier customers require delivery between 8 AM - 5 PM...",
        "FedEx Force Majeure clause applies when weather severity >= Level 4...",
        "Late penalty: $500 per day for Platinum tier..."
    ],
    "sla_penalty": 500.0
}
```

---

## 🔗 Integration: Engine A + Engine B

### How They Work Together

1. **Engine A runs first** (ML Prediction):
   ```python
   ml_prediction = {
       "delay_hours": 52,
       "delay_probability": 0.85,
       "will_be_delayed": True,
       "predicted_eta": "2026-06-18 14:00"
   }
   ```

2. **Prediction triggers RAG query** (Engine B):
   ```python
   # Orchestrator builds contextual query
   query = build_rag_query(
       customer_name=order_data['customer_name'],
       carrier_name=order_data['carrier_name'],
       customer_tier=order_data['customer_tier'],
       delay_hours=ml_prediction['delay_hours'],
       weather_context=weather_data
   )
   
   rag_context = rag_engine.query(query)
   ```

3. **Integration calculates financial risk**:
   ```python
   financial_risk = (
       rag_context['sla_penalty'] +                    # $500 (from RAG)
       (order_value * 0.1 if delayed else 0) +         # 10% order value risk
       (1000 if specialty_diet and delay > 48 else 0)  # Emergency air freight
   )
   ```

4. **Final output combines both**:
   ```python
   {
       # From Engine A
       "delay_probability": 0.85,
       "delay_hours": 52,
       "predicted_eta": "2026-06-18 14:00",
       "root_cause": "Severe weather (Level 4 blizzard); LTL delays",
       
       # From Engine B
       "rag_policies": ["Force Majeure applies...", "$500 penalty..."],
       "sla_penalty": 500,
       
       # Integrated
       "financial_risk_usd": 1850.00,
       "recommendation": "Approve air freight upgrade to avoid penalty"
   }
   ```

---

## 🎯 Business Value

### Without Dual Engine (Traditional Approach)
- ❌ ML predicts delay, but doesn't know business impact
- ❌ Policies exist, but no trigger to retrieve them
- ❌ Manual lookup required to determine action
- ❌ Slow, reactive, error-prone

### With Dual Engine (This System)
- ✅ Automatic financial risk quantification
- ✅ Context-aware policy retrieval
- ✅ Proactive, not reactive
- ✅ Actionable recommendations with justification

---

## 📁 File Structure

```
O2C_AI/
├── modules/
│   ├── ml_db_extension.py      # Engine A: SAP data handling
│   ├── predictive_engine.py    # Engine A: ML models & prediction
│   ├── rag_engine.py           # Engine B: RAG implementation
│   ├── weather_service.py      # Weather API integration
│   └── config.py               # Configuration
│
├── Input Files/                # SAP CSV data (10 tables)
│   ├── VBAK.csv
│   ├── VBAP.csv
│   ├── LIKP.csv
│   └── ...
│
├── policies/                   # RAG knowledge documents
│   ├── weather_policies/
│   └── strike_intelligence/
│
├── main_pipeline.py            # Full orchestration
├── engine_integration_demo.py  # Standalone Engine A+B demo
└── ENGINE_A_B_README.md        # This file
```

---

## 🚀 Quick Start

### 1. Run Integration Demo (Recommended First)
```bash
python engine_integration_demo.py
```
This shows Engine A + Engine B working together on sample orders.

### 2. Run Full Pipeline
```bash
python main_pipeline.py
```
This runs all 8 steps:
1. Fetch weather data
2. Fetch strike news
3. Generate policy documents
4. Load SAP data
5. Initialize RAG
6. Train ML models
7. Run predictions (Engine A + B)
8. Export results

---

## 📊 Output Files

### ML Predictions
```
output/ml_predictions_latest.csv
```
Columns:
- `order_id`, `shipment_id`, `customer_name`, `carrier_name`
- `predicted_eta`, `delay_probability`, `delay_hours`
- `financial_risk`, `root_cause`, `rag_context`
- `created_at`

### Weather Data
```
output/weather_YYYY-MM-DD.csv
```

### Strike News
```
output/strikes_YYYY-MM-DD.csv
```

---

## 🛠️ Dependencies

### Engine A (ML)
```bash
pip install scikit-learn pandas numpy
```

### Engine B (RAG)
```bash
pip install sentence-transformers faiss-cpu pypdf python-docx openpyxl
```

### Weather API
```bash
pip install requests pyowm
```

---

## 🔄 Integration Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  ORDER: 800000000000001                                     │
│  Customer: Banfield Pet Hospital (Platinum)                 │
│  Carrier: FedEx Freight                                     │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  ENGINE A: ML PREDICTION                                    │
├─────────────────────────────────────────────────────────────┤
│  • Load order features (weight, tier, shipping type)       │
│  • Check weather at destination (Chicago: Level 4 blizzard)│
│  • Run ML models:                                           │
│    - Classifier: 85% probability of delay                   │
│    - Regressor: Predict 52 hours late                       │
│  • Root cause: "Severe weather + LTL consolidation"        │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR: BUILD RAG QUERY                              │
├─────────────────────────────────────────────────────────────┤
│  Query: "Banfield (Platinum) + FedEx + 52hr delay +         │
│          Level 4 weather → What penalties and exceptions?"  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  ENGINE B: RAG RETRIEVAL                                    │
├─────────────────────────────────────────────────────────────┤
│  • Search vector DB for matching policies                   │
│  • Retrieved documents:                                      │
│    1. "Platinum SLA: $500/day penalty"                      │
│    2. "FedEx Force Majeure: Applies at Level 4+ weather"   │
│    3. "After-hours delivery: Carrier pays $150 redelivery" │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR: CALCULATE FINANCIAL RISK                     │
├─────────────────────────────────────────────────────────────┤
│  • SLA penalty: $500 (from RAG)                             │
│  • Order value risk: $912 (10% of $9,125 order)            │
│  • No specialty diet penalty (not applicable)               │
│  • TOTAL RISK: $1,412                                       │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  FINAL OUTPUT                                               │
├─────────────────────────────────────────────────────────────┤
│  Delay Prediction: 52 hours (85% probability)               │
│  Financial Risk: $1,412                                     │
│  SLA Status: Force Majeure MAY apply (Level 4 weather)     │
│  Recommendation:                                            │
│    1. Document weather event for carrier liability          │
│    2. Proactively notify customer                           │
│    3. Consider air freight upgrade ($1,000) vs penalty      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎓 Key Concepts

### Why Two Engines?

**Engine A** answers: *"What will happen?"* (Math)
- Delay probability: 85%
- Delay hours: 52
- ETA: June 18, 2:00 PM

**Engine B** answers: *"What should we do about it?"* (Rules)
- Penalty: $500
- Exception: Force Majeure may apply
- Action: Document weather, notify customer

**Integration** answers: *"What's the business impact?"* (Decision)
- Total risk: $1,412
- Cost/benefit: Air freight ($1,000) vs penalty ($500)
- Recommendation: Document + monitor

---

## 📈 Future Enhancements (Phase 4+)

### Agentic Orchestration (Not Yet Implemented)
- **LangGraph**: Multi-agent workflow
- **LLM Reasoning**: GPT-4 / Llama 3.1 for synthesis
- **Action Flows**: Automated notifications and approvals

The current implementation (Phase 3) focuses on:
- ✅ Engine A: ML prediction
- ✅ Engine B: RAG retrieval
- ✅ Basic integration logic
- ⏸️ Phase 4: Advanced orchestration (not started per your request)

---

## 💡 Examples

### Example 1: High-Risk Platinum Customer
```python
Order: 800000000000001
Customer: Banfield Pet Hospital (Platinum)
Carrier: FedEx

Engine A Output:
  Delay: 52 hours (85% probability)
  Root Cause: Level 4 blizzard + LTL delays

Engine B Output:
  SLA: $500/day penalty for Platinum
  Exception: Force Majeure at Level 4+

Integrated Risk:
  Financial: $1,412 ($500 penalty + $912 order value risk)
  Action: Document weather, consider air freight
```

### Example 2: Specialty Diet Critical Item
```python
Order: 800000000000003
Customer: VCA Animal Hospital (Gold)
Carrier: XPO Logistics
Item: Renal Support Diet (Specialty)

Engine A Output:
  Delay: 72 hours (78% probability)
  Root Cause: Heavy shipment + tight schedule

Engine B Output:
  SLA: $300/day penalty for Gold
  Policy: Specialty diet delay >48hrs → Emergency air freight

Integrated Risk:
  Financial: $1,900 ($300 penalty + $1,000 air freight + $600 order risk)
  Action: CRITICAL - Approve air freight immediately
```

---

## ❓ FAQ

### Q: Why not just use one AI model?
**A**: Specialization is more powerful than generalization:
- Engine A excels at **pattern recognition** in numerical data
- Engine B excels at **semantic understanding** of text policies
- Together, they provide both "what will happen" and "what it means"

### Q: Can I run without Engine B (RAG)?
**A**: Yes! Engine A provides predictions independently. You'll get delay forecasts but no policy context or penalty amounts.

### Q: Can I run without Engine A (ML)?
**A**: Partially. You can still query RAG for policies, but you won't have automated delay predictions to trigger the queries.

### Q: What if I don't have SAP data?
**A**: The demo CSV files in `/Input Files/` are synthetic SAP-format data. You can replace them with your actual data or other ERP exports.

---

## 📞 Support

For questions or issues:
1. Check this README
2. Review `engine_integration_demo.py` for working examples
3. Inspect `modules/predictive_engine.py` for integration logic

---

**Last Updated**: 2025-01-15  
**Status**: Phase 3 Complete (Engine A + Engine B Integrated)  
**Next**: Phase 4 (Agentic Orchestration) - Not Started
