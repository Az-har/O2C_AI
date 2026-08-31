# 🧠 O2C AI MONITOR: SYSTEM DEEP DIVE SPECIFICATION
## PART 2: DUAL-ENGINE INTELLIGENCE — PREDICTIVE FEATURE STORE (ENGINE A) & HYBRID RAG VECTOR STORE (ENGINE B)

---

## 1. 📌 Overview & Scope of Part 2

This specification document provides an exhaustive, function-by-function architectural breakdown of **Part 2: Dual-Engine Intelligence** in the O2C Delivery Risk Copilot.

Part 2 bridges the gap between raw data ingestion (Part 1) and autonomous multi-agent decision execution (Part 3). It operates on a **Dual-Engine Architecture**:
1. **Engine A (Predictive Machine Learning & Feature Store):** Joins 10 normalized SAP ERP tables, computes geospatial Haversine transit vectors and operational stress signals, trains supervised machine learning models (`RandomForestClassifier` + `GradientBoostingRegressor`), outputs explainable feature attributions, and predicts delivery delay probabilities and delay hours.
2. **Engine B (Hybrid RAG & Knowledge Vectorization):** Parses unstructured contracts, SOPs, carrier agreements, and synthesized AI intelligence briefs; generates clause-aware semantic chunks; constructs a dual **Dense FAISS Vector Index** (`all-MiniLM-L6-v2`) and **Sparse BM25 Keyword Lexicon**; and fuses them using **Reciprocal Rank Fusion (RRF)** with Qwen2.5 anti-hallucination synthesis.

```mermaid
graph TD
    subgraph "Engine A: Predictive ML Feature Store"
        A1["10 SAP CSV Tables<br/>(VBAK, VBAP, LIKP, LIPS, VTTK, VTTP, KNA1, KNVV, LFA1, MARA)"] --> A2["MLDatabaseExtension<br/>(Relational Joins & Feature Engineering)"]
        A2 --> A3["ML Feature Store & Cache<br/>(haversine_distance, speed, weight_per_unit)"]
        A3 --> A4["PredictiveEngine Models<br/>(RandomForest Clf + GradientBoosting Reg)"]
        A4 --> A5["Prediction Tuple:<br/>(Delay Prob, Delay Hours, Root Cause, SLA Risk)"]
    end

    subgraph "Engine B: Hybrid RAG Knowledge Engine"
        B1["82 Corpus Documents<br/>(Contracts, SLAs, SOPs, Strike Briefs, Weather Protocols)"] --> B2["DocumentLoader & ClauseAwareChunker<br/>(Regex Boundaries & Chunk Deduplication)"]
        B2 --> B3["909 Semantic Chunks<br/>(all_chunks.json)"]
        B3 --> B4a["Dense FAISS Index<br/>(all-MiniLM-L6-v2, 384-dim)"]
        B3 --> B4b["Sparse BM25 Index<br/>(Okapi BM25 Lexicon)"]
        B4a & B4b --> B5["Hybrid Search Fusion (RRF)<br/>(Alpha Blending & Exact Clause Match)"]
    end

    A5 & B5 --> C["Multi-Agent Orchestrator (Part 3)"]
```

---

## 2. 📁 Storage Architecture & Artifact Locations for Part 2

Every file, table, serialized model artifact, and index used in Part 2 is mapped below:

### 2.1 Relational & Feature Store Tables (`india_monitor_data/database/india_monitor.db`)
- **`sap_vbak`**: Sales Order Header (Order ID `vbeln`, Customer `kunnr`, Order Date `erdat`, Requested Delivery Date `vdatu`, Net Value `netwr`).
- **`sap_vbap`**: Sales Order Items (Order ID `vbeln`, Line `posnr`, SKU `matnr`, Quantity `kwmeng`, Unit Price `netpr`).
- **`sap_likp`**: Outbound Delivery Header (Delivery `vbeln`, Customer `kunnr`, Planned Goods Issue `wadat`, Shipping Point `vstel`).
- **`sap_lips`**: Outbound Delivery Items (Delivery `vbeln`, Line `posnr`, Sales Order `vgbel`, Gross Weight `brgew`).
- **`sap_vttk`**: Shipment Linehaul Header (Shipment `tknum`, Carrier `lifnr`, Transport Mode `vsart`, Planned Departure `dpabf`, Status `status`).
- **`sap_vttp`**: Shipment Items Bridge (Shipment `tknum`, Item `tpnum`, Delivery `vbeln`).
- **`sap_kna1`**: Customer Master General (Customer `kunnr`, Name `name1`, City `ort01`, Region `regio`, Postal Code `pstlz`).
- **`sap_knvv`**: Customer Master Sales & SLAs (Customer `kunnr`, Tier `customer_tier` [Platinum/Gold/Silver], Receiving Dock Closing Time `close_time`).
- **`sap_lfa1`**: Carrier / Vendor Master (Carrier `lifnr`, Name `name1`, City `ort01`, Contact `telf1`).
- **`sap_mara`**: Material / SKU Master (Material `matnr`, Description `maktx`, Specialty Diet Flag `specialty_diet_flag`, Shelf Life Months `shelf_life_mos`).
- **`ml_predictions`**: Persisted model inferences (Order ID, Delivery ID, Delay Probability, Delay Hours, Root Cause, Financial Risk USD, Timestamp).

### 2.2 Serialized ML Model Artifacts (`india_monitor_data/models/`)
- **`rf_classifier.pkl`**: Serialized `RandomForestClassifier` (50 estimators, max depth 5) for binary delay probability scoring.
- **`gb_regressor.pkl`**: Serialized `GradientBoostingRegressor` (50 estimators, max depth 4) for continuous delay hour duration estimation.
- **`feature_importances.json`**: Global feature weights for Explainable AI (XAI) feature attribution percentages.

### 2.3 Serialized Vector & Lexical RAG Indexes (`india_monitor_data/rag/`)
- **`chunks/all_chunks.json`**: Human-readable JSON array containing all 909 vectorized text chunks with metadata (source document, category, chunk ID, char length, token count).
- **`vector_store/index.faiss`**: Dense FAISS `IndexFlatIP` vector index containing 909 normalized 384-dimensional embeddings.
- **`vector_store/bm25.pkl`**: Serialized Okapi BM25 sparse keyword lexicon (frequencies, inverted document frequencies `idf`, average document length).
- **`vector_store/metadata.pkl`**: Serialized list of chunk metadata dictionaries matching FAISS internal vector IDs 1-to-1.
- **`vector_store/chunks.pkl`**: Serialized list of full raw chunk texts for sub-millisecond document reconstruction.

---

## 3. 🧩 Detailed Function-by-Function Code Breakdown

---

### Module 1: `modules/ml_db_extension.py`
**File Location:** `d:\Progamming\O2C_AI\modules\ml_db_extension.py`  
**Class:** `MLDatabaseExtension`  
**Purpose:** Manages the relational ingestion of 10 SAP ERP tables, executes complex multi-table SQL joins, computes geospatial Haversine metrics and calendar features, and exposes sub-millisecond in-memory cached lookup APIs for ML training and inference.

#### Functions in `MLDatabaseExtension`:

#### 1. `__init__(self, db_path: Optional[Path] = None)`
- **Purpose:** Establishes SQLite connection with `check_same_thread=False`, sets `row_factory = sqlite3.Row`, enables WAL concurrency mode (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`), initializes in-memory lookup caches, and executes `_build_sap_schema()`.
- **Input Parameters:** `db_path (Path | None)` — Target database path.
- **Output Return Type:** None.
- **How it helps the data:** Guarantees thread-safe access and high-throughput zero-lock read/write operations during batch inference.

#### 2. `_build_sap_schema(self) -> None`
- **Purpose:** Executes DDL scripts creating normalized relational tables for all 10 SAP ERP structures (`sap_vbak`, `sap_vbap`, `sap_likp`, `sap_lips`, `sap_vttk`, `sap_vttp`, `sap_kna1`, `sap_knvv`, `sap_lfa1`, `sap_mara`) and `ml_predictions`, along with 8 B-Tree indexes on primary foreign keys (`idx_vbak_kunnr`, `idx_lips_vgbel`, `idx_vttp_vbeln`, etc.).
- **Input Parameters:** None.
- **Output Return Type:** None.
- **How it helps the data:** Enforces relational integrity across sales orders, warehouse deliveries, linehaul shipments, and customer tiers.

#### 3. `load_sap_data_from_csv(self, input_dir: Path) -> Dict[str, int]`
- **Purpose:** Ingests 10 SAP CSV export files from `input_dir`, cleans column names, strips whitespace, and bulk-inserts them into SQLite tables using `df.to_sql(if_exists="replace")`. Invalidates in-memory caches.
- **Input Parameters:** `input_dir (Path)` — Directory containing SAP CSV files.
- **Output Return Type:** `Dict[str, int]` — Dictionary mapping table names to ingested row counts.
- **How it helps the data:** Populates the ERP foundation of the AI system from flat enterprise exports.

#### 4. `get_ml_ready_dataset(self, force_refresh: bool = False) -> pd.DataFrame`
- **Purpose:** Executes the master 10-table relational SQL query joining sales orders, items, deliveries, shipments, carriers, customers, and materials. Applies mathematical feature engineering to produce the unified ML feature store. Results are cached in `self._cached_ml_df` and pre-indexed in `self._order_lookup_dict` for $O(1)$ instant lookups.
- **Input Parameters:** `force_refresh (bool)` — If `True`, bypasses cache and re-queries SQLite.
- **Output Return Type:** `pd.DataFrame` — 11,797+ rows with all engineered feature columns.
- **Engineered Feature Transformations:**
  - **`order_to_delivery_days`**: $\text{RDD} - \text{Order Date}$ (Turnaround window).
  - **`order_to_departure_days`**: $\text{Departure Date} - \text{Order Date}$ (Warehouse dwell).
  - **`total_weight` & `weight_per_unit`**: $\frac{\text{Total Gross Weight}}{\max(\text{Total Quantity}, 1.0)}$.
  - **`is_heavy_shipment`**: Binary indicator $(1 \text{ if } \text{Total Weight} > 1000.0\text{ kg else } 0)$.
  - **`haversine_distance_km`**: Great-circle distance calculated from origin central distribution hub (Mumbai: $19.0760^\circ\text{N}, 72.8777^\circ\text{E}$) to destination city coordinates:
    $$\Delta\sigma = 2 \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos\phi_1\cos\phi_2\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right), \quad d = R \cdot \Delta\sigma$$
  - **`required_transit_speed_kmh`**: $\frac{\text{haversine\_distance\_km}}{\max(1.0, \text{order\_to\_delivery\_days} \times 24.0)}$.
  - **`is_unrealistic_speed`**: Binary flag $(1 \text{ if } \text{required speed} > 55.0\text{ km/h else } 0)$.
  - **`is_weekend_order`**: Binary flag $(1 \text{ if day of week} \ge 4 \text{ [Fri/Sat/Sun] else } 0)$.
  - **`is_month_end`**: Binary flag $(1 \text{ if day of month} \ge 26 \text{ else } 0)$ to capture warehouse dispatch congestion surges.
  - **`customer_tier_code`**: Categorical integer mapping: $\text{Platinum} \to 3, \text{Gold} \to 2, \text{Independent} \to 2, \text{Silver/Standard} \to 1$.
  - **`shipping_risk_code`**: Modal risk mapping: $\text{Rush} \to 3, \text{LTL} \to 2, \text{FTL/Rail/Intermodal} \to 1, \text{Air} \to 0$.

#### 5. `get_order_details(self, order_id: str) -> Optional[Dict[str, Any]]`
- **Purpose:** Retrieves the complete, feature-engineered joined dictionary for any specific sales order in $O(1)$ constant time from the pre-indexed memory hash map. Supports suffix matching fallback for short order IDs.
- **Input Parameters:** `order_id (str)` — SAP Sales Order Number (e.g. `"800000000000001"`).
- **Output Return Type:** `Optional[Dict[str, Any]]` — Complete order feature dictionary or `None`.
- **How it helps the data:** Eliminates redundant disk I/O and SQL joins during real-time multi-agent order evaluation.

#### 6. `record_prediction(self, prediction: Dict[str, Any]) -> int`
- **Purpose:** Inserts an Engine A prediction record into `ml_predictions` table (Order ID, Delivery ID, Shipment ID, Customer, Carrier, Predicted ETA, Delay Probability, Delay Hours, Delay Flag, Root Cause, Financial Risk USD, Timestamp).
- **Input Parameters:** `prediction (Dict[str, Any])` — Inference result dictionary.
- **Output Return Type:** `int` — Auto-incremented `prediction_id`.
- **How it helps the data:** Maintains an immutable historical audit trail of all model predictions for model drift analysis.

#### 7. `get_predictions(self, limit: int = 100, delayed_only: bool = False) -> List[Dict[str, Any]]`
- **Purpose:** Queries historical model predictions from SQLite with optional filtering for delayed orders.
- **Input Parameters:** `limit (int)`, `delayed_only (bool)`.
- **Output Return Type:** `List[Dict[str, Any]]`.

#### 8. `get_summary_stats(self) -> Dict[str, Any]`
- **Purpose:** Aggregates overall database statistics across all SAP tables, total orders, total shipments, customer tier distribution, and active predictions.
- **Input Parameters:** None.
- **Output Return Type:** `Dict[str, Any]`.

---

### Module 2: `modules/predictive_engine.py`
**File Location:** `d:\Progamming\O2C_AI\modules\predictive_engine.py`  
**Class:** `PredictiveEngine`  
**Purpose:** Core machine learning orchestration engine for Engine A. Implements supervised classification and regression model training, model serialization/loading, explainable feature attribution (XAI), root cause diagnosis, financial risk quantification, and seamless enrichment with Engine B RAG context.

#### Functions in `PredictiveEngine`:

#### 1. `__init__(self, ml_db_extension=None, rag_engine=None, weather_service=None)`
- **Purpose:** Initializes PredictiveEngine with dependencies, defines the 19 canonical ML feature columns (`FEATURE_COLS`), initializes model instances, and calls `_preload_environmental_caches()`.
- **Input Parameters:** `ml_db_extension (MLDatabaseExtension | None)`, `rag_engine (RAGEngine | None)`, `weather_service (WeatherService | None)`.
- **Output Return Type:** None.

#### 2. `_preload_environmental_caches(self) -> None`
- **Purpose:** Pre-loads the latest weather readings across all 10 cities and the top 50 strike news events from SQLite into memory caches (`self._weather_cache` and `self._strike_cache`).
- **Input Parameters:** None.
- **Output Return Type:** None.
- **How it helps the data:** Removes per-order database query overhead, reducing multi-order batch evaluation runtime from minutes to seconds.

#### 3. `train_models(self, df: pd.DataFrame, train_size: float = 0.8) -> bool`
- **Purpose:** Trains two supervised machine learning models using Scikit-Learn:
  1. **`RandomForestClassifier`** (`n_estimators=50, max_depth=5, random_state=42`): Fits `X_train` against binary `is_delayed` labels.
  2. **`GradientBoostingRegressor`** (`n_estimators=50, max_depth=4, random_state=42`): Fits `X_train` against continuous `delay_hours`.
  Extracts feature importances and calls `save_models()`.
- **Input Parameters:** `df (pd.DataFrame)` — Feature-engineered dataset from `MLDatabaseExtension`, `train_size (float)` — Train/test split ratio (default 0.8).
- **Output Return Type:** `bool` — `True` if training succeeded, `False` otherwise.
- **How it helps the data:** Establishes mathematical predictive models that generalize across 19 complex logistics risk dimensions.

#### 4. `save_models(self, model_dir: Path = None) -> bool`
- **Purpose:** Serializes trained model objects into binary `.pkl` files (`rf_classifier.pkl`, `gb_regressor.pkl`) and exports `feature_importances.json` to `india_monitor_data/models/`.
- **Input Parameters:** `model_dir (Path | None)`.
- **Output Return Type:** `bool`.

#### 5. `load_models(self, model_dir: Path = None) -> bool`
- **Purpose:** Deserializes trained model artifacts from disk on startup, enabling instant zero-latency inference without requiring re-training.
- **Input Parameters:** `model_dir (Path | None)`.
- **Output Return Type:** `bool` — `True` if artifacts loaded successfully.

#### 6. `explain_prediction(self, order_data: Dict[str, Any], delay_prob: float) -> List[Dict[str, Any]]`
- **Purpose:** Implements Explainable AI (XAI) feature attribution. Evaluates active risk conditions for the order (e.g. Unrealistic Speed, Weekend Dispatch, Heavy Pallet, LTL Dwell, Month-End Congestion), weights them by the trained model's feature importances, and calculates normalized contribution percentages (`contribution_pct`).
- **Input Parameters:** `order_data (Dict[str, Any])`, `delay_prob (float)`.
- **Output Return Type:** `List[Dict[str, Any]]` — Top 4 contributing risk factors with human-readable explanations and percentage contributions.
- **How it helps the data:** Transforms opaque ML probability scores into clear, human-understandable root-cause narratives for logistics directors.

#### 7. `predict_delivery_delay(self, order_id: str, order_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`
- **Purpose:** Executes the end-to-end prediction and risk quantification pipeline for a single order:
  1. Fetches feature vector from `MLDatabaseExtension`.
  2. Evaluates ML models: Computes `delay_probability` (from `RandomForestClassifier`) and `delay_hours` (from `GradientBoostingRegressor`).
  3. Diagnoses primary and secondary root causes (`_diagnose_root_cause`).
  4. Calculates financial exposure and contractual SLA penalties (`_calculate_financial_risk`).
  5. Computes revised Estimated Time of Arrival (ETA).
  6. Enriches result with retrieved policy context from Engine B RAG (`_enrich_with_rag`).
- **Input Parameters:** `order_id (str)`, `order_data (Dict[str, Any] | None)`.
- **Output Return Type:** `Dict[str, Any]` — Comprehensive prediction payload consumed by Multi-Agent Specialists in Part 3.

#### 8. `_diagnose_root_cause(self, order_data: Dict[str, Any], is_delayed: bool) -> Tuple[str, str]`
- **Purpose:** Evaluates operational, environmental, and carrier signals to determine the primary and secondary root causes of predicted delay:
  - Extreme Heatwave ($>40^\circ\text{C}$) / Monsoon Flooding ($>20\text{mm/hr}$) / Gale Winds ($>15\text{m/s}$).
  - Active Transport Strike or Highway Blockade in destination city.
  - Multi-Stop LTL Terminal Consolidation Dwell ($>1000\text{kg}$ LTL).
  - Unrealistic Transit Velocity Demand ($>55\text{km/h}$ required linehaul speed).
  - Weekend Dispatch / Receiving Dock Closure (Delivery scheduled after clinic close time).
  - Month-End Warehouse Dispatch Congestion.
- **Input Parameters:** `order_data (Dict[str, Any])`, `is_delayed (bool)`.
- **Output Return Type:** `Tuple[str, str]` — `(primary_root_cause, secondary_root_cause)`.

#### 9. `_calculate_financial_risk(self, order_data: Dict[str, Any], delay_hours: float, is_delayed: bool) -> Dict[str, float]`
- **Purpose:** Computes contractual financial liabilities and SLA penalties based on customer tier and order value:
  - **Platinum Tier Customers:** $\$500.00$ per 24-hour delay increment beyond requested delivery date.
  - **Gold Tier Customers:** $5\%$ of total order value per 24-hour delay increment (capped at $25\%$).
  - **Silver / Standard Customers:** $\$150.00$ fixed late delivery penalty.
  - **Carrier Chargeback:** $100\%$ chargeback of delay penalty to carrier unless protected by Force Majeure.
  - **Perishable Spoilage Risk:** If therapeutic wet food or biologics delay exceeds product shelf-life tolerance ($>48\text{h}$ in extreme heat), flags $100\%$ order value destruction risk.
- **Input Parameters:** `order_data (Dict[str, Any])`, `delay_hours (float)`, `is_delayed (bool)`.
- **Output Return Type:** `Dict[str, float]` — `{"sla_penalty_usd", "carrier_chargeback_usd", "total_financial_risk_usd"}`.

#### 10. `_enrich_with_rag(self, order_data: Dict[str, Any], root_cause: str) -> Dict[str, Any]`
- **Purpose:** Automatically queries Engine B RAG (`rag_engine.ask`) using the detected customer tier, carrier name, destination city, and root cause.
- **Input Parameters:** `order_data (Dict[str, Any])`, `root_cause (str)`.
- **Output Return Type:** `Dict[str, Any]` — Retrieved policy excerpts, source document names, and clause citations.

---

### Module 3: `modules/rag_engine.py`
**File Location:** `d:\Progamming\O2C_AI\modules\rag_engine.py`  
**Classes:** `DocumentLoader`, `ClauseAwareChunker`, `BM25Index`, `VectorStore`, `RAGQueryEngine`, `RAGEngine`  
**Purpose:** Engine B Knowledge Retrieval Core. Ingests 82 Word, PDF, Excel, and Text policy documents; performs dynamic regex boundary chunking; builds dense FAISS vectors and sparse BM25 lexicon; and executes hybrid reciprocal rank fusion search.

#### Component Breakdown in `modules/rag_engine.py`:

```mermaid
graph TD
    A["Raw Corpus Documents (82 files)"] --> B["DocumentLoader<br/>(DOCX, PDF, XLSX, TXT)"]
    B --> C["ClauseAwareChunker<br/>(Dynamic Regex Boundary Splitting)"]
    C --> D["909 Granular Chunks (all_chunks.json)"]
    
    subgraph "Hybrid Index Construction"
        D --> E1["Dense Pipeline: SentenceTransformer('all-MiniLM-L6-v2')"]
        E1 --> E2["FAISS IndexFlatIP (Cosine Similarity, 384-dim)"]
        D --> F1["Sparse Pipeline: Custom Tokenizer & IDF Calculator"]
        F1 --> F2["Okapi BM25 Sparse Index (k1=1.5, b=0.75)"]
    end
    
    subgraph "Hybrid Query Execution"
        G["User / Agent Query"] --> H1["Dense Search (Top 5 Vectors)"]
        G --> H2["BM25 Search (Top 5 Keywords)"]
        H1 & H2 --> I["Reciprocal Rank Fusion (RRF)<br/>Score = RRF_Dense + RRF_BM25"]
        I --> J["RAGQueryEngine Synthesis (Answer + Sources + Confidence)"]
    end
```

#### Class 1: `DocumentLoader`
- **`load_all(self) -> List[Dict]`**: Iterates through `india_monitor_data/rag/documents/`, detects file format by extension (`.docx`, `.pdf`, `.xlsx`, `.txt`), extracts raw text and document metadata, and assigns category based on parent folder (`Clinic SLAs`, `Vendor Contracts`, `Packaging Policies`, `History Resolution Logs`, `Strike Intelligence`, `Weather Policies`).
- **`_load_docx(self, path: Path) -> str`**: Extracts paragraph text and table cell contents using `docx.Document`.
- **`_load_pdf(self, path: Path) -> str`**: Iterates through PDF pages using `pypdf.PdfReader`.
- **`_load_excel(self, path: Path) -> str`**: Reads active worksheet rows and tabulates cell values using `openpyxl`.
- **`_load_text(self, path: Path) -> str`**: Reads UTF-8 plain text with fallback decoding.

#### Class 2: `ClauseAwareChunker`
- **`chunk_documents(self, documents: List[Dict]) -> List[Dict]`**: Processes loaded documents into granular semantic chunks.
- **`_chunk_document(self, doc: Dict) -> List[Dict]`**: Implements two-stage hierarchical splitting:
  1. **Primary Structural Boundary Splitting:** Uses regex lookahead to split at formal clause headings:
     ```python
     re.split(r'(?=\n(?:[0-9]+\.[0-9]*\s+|TICKET\s+|SECTION\s+|INC-[0-9]+\s+|[A-Z\s]{4,}:))|\n\n+', text)
     ```
  2. **Secondary Sentence Accumulation:** If a section exceeds `max_chunk_size` (500 chars), splits at sentence boundaries (`re.split(r'(?<=[.!?])\s+', sec)`) and accumulates sentences with `chunk_overlap = 50` chars.
- **`_calculate_chunk_id(self, text: str, filename: str, index: int) -> str`**: Generates deterministic SHA-256 hash prefix identifying the chunk (`f"chk_{hashlib.sha255(...).hexdigest()[:10]}"`).
- **`save_chunks(self, chunks: List[Dict], output_path: Path = None) -> None`**: Exports all chunks to `india_monitor_data/rag/chunks/all_chunks.json`.

#### Class 3: `BM25Index`
- **`__init__(self, k1: float = 1.5, b: float = 0.75)`**: Initializes BM25 tuning parameters ($k_1 = 1.5$ term saturation, $b = 0.75$ document length normalization).
- **`_tokenize(self, text: str) -> List[str]`**: Converts text to lowercase alphanumeric tokens, preserving currency and clause symbols (`re.findall(r'[a-zA-Z0-9$_\-%]+', text)`).
- **`build_index(self, chunks: List[Dict]) -> None`**: Computes document frequencies ($df$), average document length ($avgdl$), and standard Robertson-Spärck Jones Inverse Document Frequencies ($idf$):
  $$\text{IDF}(q) = \ln\left(1.0 + \frac{N - df(q) + 0.5}{df(q) + 0.5}\right)$$
- **`search(self, query: str, top_k: int = 5, category: str = None) -> List[Dict]`**: Evaluates Okapi BM25 scoring across all documents:
  $$\text{BM25}(D, Q) = \sum_{q \in Q} \text{IDF}(q) \cdot \frac{f(q, D) \cdot (k_1 + 1)}{f(q, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{avgdl}\right)}$$

#### Class 4: `VectorStore`
- **`__init__(self, model_name: str = "all-MiniLM-L6-v2")`**: Loads HuggingFace `SentenceTransformer` model (384 embedding dimensions).
- **`build_index(self, chunks: List[Dict]) -> None`**: Generates L2-normalized dense embeddings, builds FAISS `IndexFlatIP` (Inner Product / Cosine Similarity), builds BM25 index, and serializes index files to disk (`index.faiss`, `bm25.pkl`, `metadata.pkl`, `chunks.pkl`).
- **`load_index(self) -> bool`**: Deserializes pre-built FAISS and BM25 indexes into RAM.
- **`search_hybrid(self, query: str, top_k: int = 5, category: str = None) -> List[Dict]`**: Executes dense vector search and sparse BM25 search in parallel, then merges results via **Reciprocal Rank Fusion (RRF)**:
  $$\text{RRF\_Score}(d) = \frac{1}{60 + \text{Rank}_{\text{dense}}(d)} + \frac{1}{60 + \text{Rank}_{\text{BM25}}(d)}$$
  Normalizes combined similarity score to $[0.0, 1.0]$. In-memory query cache ensures sub-millisecond retrieval.

#### Class 5: `RAGQueryEngine`
- **`ask(self, question: str, category: str = None, top_k: int = 5) -> Dict`**: Executes hybrid search, builds context window from top matching chunks, and calls `_generate_answer()`.
- **`_generate_answer(self, question: str, context: str, chunks: List[Dict]) -> str`**: Deduplicates snippets, formats clause citations with category tags and similarity scores, and constructs a structured answer payload.
- **`query(self, question: str, category: str = None, top_k: int = 5, verbose: bool = True) -> Dict`**: High-level interface formatting output for terminal display or downstream agent prompts.

#### Class 6: `RAGEngine`
- **`initialize(self, force_rebuild: bool = False) -> bool`**: Orchestrates `DocumentLoader`, `ClauseAwareChunker`, and `VectorStore`. Loads existing index or rebuilds from scratch if `force_rebuild=True`.
- **`ask(self, question: str, category: str = None) -> Dict`**: Public API for silent programmatic retrieval.
- **`query(self, question: str, category: str = None, verbose: bool = True) -> Dict`**: Public API for verbose terminal inspection.

---

### Module 4: `modules/ollama_service.py`
**File Location:** `d:\Progamming\O2C_AI\modules\ollama_service.py`  
**Class:** `OllamaService`  
**Purpose:** Provides a lightweight, high-performance interface to local Ollama LLM daemons (running `qwen2.5:7b`), implementing strict anti-hallucination guardrails and deterministic temperature constraints for dynamic policy synthesis.

#### Functions in `OllamaService`:

#### 1. `__init__(self, host: str = "http://localhost:11434", model: str = "qwen2.5:7b", timeout: int = 45)`
- **Purpose:** Initializes Ollama REST API connection parameters.
- **Input Parameters:** `host (str)`, `model (str)`, `timeout (int)`.
- **Output Return Type:** None.

#### 2. `is_available(self) -> bool`
- **Purpose:** Sends a lightweight `GET /api/tags` request (2-second timeout) to verify that the Ollama daemon is active and that `qwen2.5:7b` (or a compatible local model) is loaded in VRAM.
- **Input Parameters:** None.
- **Output Return Type:** `bool` — `True` if active and model exists, `False` otherwise.
- **How it helps the data:** Ensures the pipeline never hangs if Ollama is offline, enabling immediate fallback to deterministic templates.

#### 3. `generate(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]`
- **Purpose:** Sends generation payload to `POST /api/generate` with strict enterprise anti-hallucination settings:
  ```json
  {
    "temperature": 0.1,
    "top_p": 0.85,
    "repeat_penalty": 1.15,
    "num_predict": 1024
  }
  ```
  Applies the non-negotiable `STRICT_SYSTEM_PROMPT` mandating that the model only cite explicitly provided telemetry and facts.
- **Input Parameters:** `prompt (str)`, `system_prompt (str | None)`.
- **Output Return Type:** `Optional[str]` — Generated text completion or `None` on failure/timeout.

---

## 4. 📊 Data Summary Matrix for Part 2

| Module / Component | Primary Input Data | Core Transformation / Function | Output Artifact | Downstream Consumer |
|---|---|---|---|---|
| **`modules/ml_db_extension.py`** | 10 SAP CSV Tables & SQLite database | Relational SQL Joins, Haversine Geospatial Vectors, Calendar Stress Signals | `sap_*` tables & in-memory ML DataFrame cache | `PredictiveEngine` & `AgenticOrchestrator` |
| **`modules/predictive_engine.py`** | Feature-engineered order DataFrame | Supervised Random Forest Classifier & Gradient Boosting Regressor | `rf_classifier.pkl`, `gb_regressor.pkl`, `feature_importances.json` | `modules/agent_specialists.py` |
| **`modules/rag_engine.py` (Chunker)** | 82 Raw Word, PDF, Excel & Text Documents | Clause-Aware Regex Lookahead Splitting & Sentence Accumulation | `india_monitor_data/rag/chunks/all_chunks.json` (909 chunks) | `VectorStore` |
| **`modules/rag_engine.py` (VectorStore)** | 909 Semantic Chunks | SentenceTransformer Embedding (`all-MiniLM-L6-v2`) & Okapi BM25 Indexing | `index.faiss`, `bm25.pkl`, `metadata.pkl`, `chunks.pkl` | `RAGQueryEngine` & Multi-Agent Graph |
| **`modules/rag_engine.py` (Hybrid Search)** | Natural Language Query | Parallel Dense Vector Search + Sparse BM25 Search merged via RRF | Top 5 Ranked Chunks with Similarity Scores | `PredictiveEngine._enrich_with_rag` & Agent Specialists |
| **`modules/ollama_service.py`** | Live Telemetry & Incident Headlines | Low-temperature (`0.1`) Qwen2.5 synthesis with anti-hallucination prompt | Executive Risk Advisories & Cold-Chain Directives | `StrikeIntelligenceGenerator` & `WeatherPolicyGenerator` |

---

## 5. 🔬 Dual-Engine Synergy: How Engine A & Engine B Work Together

A defining innovation of the O2C Delivery Risk Copilot is the mathematical coupling between **Engine A (Predictive ML)** and **Engine B (Hybrid RAG)**:

```mermaid
sequenceDiagram
    autonumber
    actor Pipeline as Daily Job / Pipeline
    participant Ext as MLDatabaseExtension
    participant EngA as Engine A (Predictive ML)
    participant EngB as Engine B (Hybrid RAG)
    participant Agents as Multi-Agent Specialists (Part 3)

    Pipeline->>Ext: get_order_details("800000000000001")
    Ext-->>EngA: 19 Engineered Features (Haversine km, Speed, Weight, Tier)
    EngA->>EngA: Evaluate RandomForest & GradientBoosting
    Note over EngA: Delay Prob: 88.3% | Delay Hours: 60.9h<br/>Root Cause: Extreme Heatwave & LTL Dwell
    EngA->>EngB: Query Knowledge Base ("Thrive Pet Healthcare Mumbai Heatwave Policy")
    EngB-->>EngA: Retrieved Chunks (Mumbai_Weather_Protocol.docx Section 4 & Platinum SLA)
    EngA-->>Agents: Unified Order Risk Payload (ML Predictions + RAG Legal Citations)
```

1. **Step 1:** `MLDatabaseExtension` delivers the complete 19-dimensional feature vector for the order.
2. **Step 2:** `Engine A` computes the empirical probability of failure ($88.3\%$) and expected duration ($60.9\text{ hours}$), calculates financial SLA risk ($\$1,000.00$), and identifies root causes.
3. **Step 3:** `Engine A` automatically triggers `Engine B` with targeted semantic search queries based on the diagnosed root causes, customer contract tier, and destination city.
4. **Step 4:** `Engine B` extracts the binding legal clauses (Force Majeure Section 4.2, Cold-Chain HPLC quarantine rules, Carrier penalty waivers) and attaches them directly to the prediction payload.
5. **Step 5:** The enriched payload is handed over to the **Multi-Agent Specialist Graph** (Part 3) for autonomous ERP writebacks and MS Teams approvals.

---
*End of Part 2 Specification. Part 3 covers Multi-Agent Specialist Reasoning, Conflict Resolution, and SAP ERP / MS Teams Action Execution.*
