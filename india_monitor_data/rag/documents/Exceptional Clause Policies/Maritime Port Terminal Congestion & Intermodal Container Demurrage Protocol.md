# Maritime Port Terminal Congestion & Intermodal Container Demurrage Protocol

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | EXC-POL-2026-004-PORT |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | International Logistics, Ocean Freight Operations, & Trade Compliance |
| **Contractual Authority** | Ocean Shipping Reform Act (OSRA) & Federal Maritime Commission (FMC) Guidelines |
| **Target SAP Tables / Fields** | VTTK (TKNUM, TDLNR), LIKP (VBELN), MARA (MATKL = 'SURGICAL', 'VET_MED') |

## 2. Commercial Purpose & Operational Context

Governs international ocean container dwell times, railhead drayage bottlenecks, and demurrage dispute standards for imported raw materials, veterinary pharmaceuticals, and sterile surgical packaging arriving via US container ports (Port of Los Angeles/Long Beach, Port of New York/New Jersey, Port of Savannah, Port of Houston).

## 3. Key Definitions & Operational Thresholds

- **Terminal Free Time**: A standard period of four (4) business days following ocean container discharge before terminal storage demurrage commences.
- **Unjust Demurrage (OSRA Non-Compliance)**: Storage fees assessed during periods when the container was physically unavailable for pickup due to port labor strikes, gate closures, or chassis shortages.
- **Off-Dock Depot Drayage Diversion**: Emergency transfer of containers from congested marine terminals to near-dock inland container yards (CY) to halt demurrage clocks.

## 4. Core Binding SLA / Policy Clauses

### 4.1 FMC Demurrage Invalidation Standard
Per Federal Maritime Commission rules, ocean terminal operators and drayage carriers are prohibited from billing demurrage if an appointment could not be secured or container was in a closed yard stack.

### 4.2 Five-Day Dwell Action Threshold
If container dwell at marine terminal reaches five (5) calendar days, the Copilot automatically authorizes emergency off-dock drayage transfer to bypass terminal demurrage rates.

### 4.3 Customs Hold Grace Protection
Delays caused by random US Customs & Border Protection (CBP) or FDA intensive agricultural exams are deemed sovereign interventions, granting 5-day penalty immunity to downstream clinic SLAs.

## 5. Financial Matrices, Penalties & Liability Caps

- **Off-Dock Drayage Diversion Subsidy**: Enterprise funds up to $650.00 USD per container for emergency inland drayage to preserve surgical supply pipelines.
- **Illegal Demurrage Dispute Recovery**: All improper demurrage invoices disputed via FMC portal; disputed funds held in escrow pending resolution.
- **Downstream Clinic SLA Extension**: SLA delivery dates for imported goods under verified port strike extended by up to seven (7) business days without penalty.

## 6. Exceptional Clauses & Relief Criteria

- **Longshoremen Union Strike (ILA / ILWU)**: Official dockworker labor strikes shut down all demurrage accruals under OSRA Section 7 statutory protections.
- **Importer of Record Paperwork Delay**: If delay stems from enterprise customs broker paperwork error, ocean terminal demurrage is fully absorbed by enterprise.

## 7. Autonomous AI Enforcement & System of Record Actions

- **Port strike or gate closure detected via news/RSS feed**: Copilot flags all active ocean containers in transit, notifies manufacturing plants of potential raw material delays.
- **Demurrage invoice received for strike period**: Automatic generation of FMC OSRA formal dispute letter; invoice flagged 'DISPUTED_UNLAWFUL_DEMURRAGE'.
