# Corporate Group Purchasing Organization (GPO) Performance & Rebate Clawback SLA

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | SLA-LOG-VNS-0031 |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Commercial Contracts, Enterprise GPO Management, & Finance |
| **Customer Classification** | Corporate Enterprise Group Purchasing Organizations (GPOs) |
| **Target SAP Tables / Fields** | KNVV (VKORG, VTWEG, KUNNR), VBAK (NETWR), LIKP (WBSTK), VBRK (NETWR, RFBSK) |

## 2. Commercial Purpose & Operational Context

Governs the aggregated supply chain performance obligations, monthly On-Time In-Full (OTIF) thresholds, and volume rebate penalty clawbacks established under multi-unit corporate veterinary group purchasing agreements. Establishes commercial alignment across enterprise chains representing hundreds of clinic locations.

## 3. Key Definitions & Operational Thresholds

- **GPO Master Entity**: A corporate veterinary management group representing a consolidated network of clinic member facilities under a master procurement contract.
- **On-Time In-Full (OTIF) Index**: The monthly ratio of deliveries meeting both Promised Delivery Date (within 24h grace) and 100% quantity fulfillment without stock-out split.
- **Volume Rebate Clawback**: Contractual forfeiture of corporate quarterly rebate payouts assessed against the enterprise when supply chain failures breach agreed OTIF floors.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Consolidated OTIF Benchmark
The enterprise commits to delivering a monthly minimum OTIF score of 96.0% across all member clinics under the GPO master agreement.

### 4.2 Measurement Period & Data Source
OTIF performance is calculated autonomously on the last calendar day of each month based on SAP LIKP goods issue timestamps and carrier EDI 214 delivery scans.

### 4.3 Carrier Accountability Passthrough
When failure to meet GPO OTIF floors is directly attributable to contracted 3PL carrier transit defaults, all associated rebate penalties are passed through to the non-performing carriers.

## 5. Financial Matrices, Penalties & Liability Caps

- **OTIF 93.0% to 95.9% (Tier 1 Default)**: Mandatory 2.5% reduction in monthly enterprise rebate payout across all participating member accounts.
- **OTIF 90.0% to 92.9% (Tier 2 Default)**: Mandatory 5.0% reduction in monthly enterprise rebate payout plus a $10,000.00 USD administrative cure credit.
- **OTIF Below 90.0% (Critical Default)**: Immediate right of GPO to terminate exclusive procurement and source alternative diets at enterprise expense.
- **Carrier Passthrough Recovery**: Carriers failing their individual 96% SLA allocated proportional share of GPO rebate deduction.

## 6. Exceptional Clauses & Relief Criteria

- **Widespread Verified Force Majeure**: Orders impacted by national or regional meteorological disasters are excluded from monthly OTIF denominator calculations.
- **Consignee Scheduled Order Surges**: Unforecasted clinic order surges exceeding 200% of 90-day average demand excluded from OTIF calculation if notified < 7 days in advance.

## 7. Autonomous AI Enforcement & System of Record Actions

- **Month-end OTIF calculation < 96.0%**: Financial settlement engine calculates rebate clawback, executes credit memo adjustments in SAP VBRK, and issues performance report to GPO executive board.
- **Carrier monthly OTIF < 95.0%**: Carrier allocation reduced by 15% in next quarterly freight bidding cycle.
