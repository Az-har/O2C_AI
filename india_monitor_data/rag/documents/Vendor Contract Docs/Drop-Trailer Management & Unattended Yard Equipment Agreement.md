# Drop-Trailer Management & Unattended Yard Equipment Agreement

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | MVA-ADD-2026-019-YARD |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Warehouse Logistics, Yard Management, & Asset Protection |
| **Contractual Scope** | Contracted Dedicated and Fleet Carriers Providing Drop-Trailer Capacity |
| **Target SAP Tables / Fields** | LFA1 (LIFNR), LIKP (VSTEL, TRAID), VTTK (TKNUM) |

## 2. Commercial Purpose & Operational Context

Governs equipment custody, pre-loading staging, kingpin security, and per diem liabilities for carrier drop-trailers stationed at enterprise distribution plants in Atlanta (PL01), Chicago (PL02), and Dallas (PL03). Enhances warehouse fulfillment throughput while standardizing risk of loss for staged freight.

## 3. Key Definitions & Operational Thresholds

- **Drop-Trailer Staging**: The placement of an empty carrier trailer at plant shipping yard to permit pre-loading of scheduled sales orders by warehouse personnel prior to driver arrival.
- **Free Drop Staging Time**: A contractual forty-eight (48) hour free period for trailers to be loaded and dispatched without yard storage fees.
- **Pre-Loaded Freight Custody**: The precise legal transfer of cargo custody upon completion of loading, application of high-security bolt seal, and electronic Bill of Lading generation.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Trailer Cleanliness & Roadworthiness
Carrier drop trailers must be delivered clean, dry, odor-free, structurally sound, and pre-swept. Trailers with chemical residues or insect evidence will be rejected with $150 rejection fee.

### 4.2 Reefer Pre-Cooling & Fuel Mandate
Refrigerated drop trailers must arrive with at least three-quarters (3/4) full diesel tank and pre-cooled to designated setpoint (20°C CRT or 4°C Cold Chain).

### 4.3 High-Security Bolt Seal Protocol
Upon loading completion, enterprise staff will affix an ISO 17712 certified numbered bolt seal. Carrier assumes full custody of freight upon driver hook-up and seal verification.

### 4.4 Timely Dispatch Obligation
Once notified that pre-loading is complete, carrier must dispatch tractor and pull trailer within twenty-four (24.0) hours.

## 5. Financial Matrices, Penalties & Liability Caps

- **Trailer Rejection Surcharge**: $150.00 USD assessed against carrier if dropped equipment fails cleanliness or refrigeration mechanical audit.
- **Yard Demurrage Per Diem**: $45.00 USD per day assessed against carrier for loaded trailers sitting in yard > 24 hours past pickup window.
- **Missing Bolt Seal Penalty**: $500.00 USD penalty plus mandatory complete pallet re-inspection if carrier driver breaks seal without authorization.

## 6. Exceptional Clauses & Relief Criteria

- **Plant Fulfillment Loading Delay**: If warehouse delays loading beyond scheduled staging schedule, carrier is excused from pickup window requirements.
- **Yard Closure Due to Severe Weather**: Blizzard or tornadic plant closures suspend all drop trailer per diem and pull mandates.

## 7. Autonomous AI Enforcement & System of Record Actions

- **Trailer loaded and sealed in YMS**: Electronic pickup tender dispatched via EDI 204 to carrier dispatch; 24h pickup countdown commences.
- **Trailer remains in yard > 24 hours post-loading**: Copilot logs daily $45 per diem and flags dispatch for carrier escalation.
