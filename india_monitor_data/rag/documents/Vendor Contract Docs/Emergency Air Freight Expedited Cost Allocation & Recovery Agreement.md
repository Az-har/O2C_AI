# Emergency Air Freight Expedited Cost Allocation & Recovery Agreement

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | MVA-ADD-2026-017-AIR |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Enterprise Freight Operations, Carrier Contracting, & Risk Management |
| **Contractual Scope** | All Commercial Linehaul Carriers & Expedited Air Logistics Providers |
| **Target SAP Tables / Fields** | LFA1 (LIFNR, VSART), VBAK (AUART, NETWR), LIKP (VBELN) |

## 2. Commercial Purpose & Operational Context

Establishes the governance parameters, authorization gates, and legal liability partitioning for upgrading delayed or threatened veterinary shipments from ground transportation (FTL/LTL) to priority commercial air freight (FedEx Priority, Delta Cargo, Southwest Cargo). Guarantees rapid patient stock-out mitigation while strictly protecting operating margins.

## 3. Key Definitions & Operational Thresholds

- **Expedited Air Mode Shift**: The emergency transfer of consigned freight to commercial air cargo to bypass road corridor blockades, severe weather, or carrier transit failures.
- **Expedited Cost Differential**: The financial difference between the premium air freight invoice and the baseline contractual ground transport rate.
- **Emergency Policy Cap**: A strict contractual expenditure ceiling of $1,000.00 USD per critical veterinary clinical order.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Carrier-At-Fault Liability Allocation
When an air freight upgrade is necessitated by carrier mechanical breakdown, missed origin tender, or unexcused driver delay, the carrier is legally liable for 100% of the air differential up to the $1,000.00 cap.

### 4.2 Shipper-Caused Delay Allocation
When air upgrades stem from warehouse stock-outs or plant loading delays, the enterprise absorbs 100% of the differential.

### 4.3 Verified Force Majeure Cost Sharing
When air freight is deployed to navigate certified meteorological disasters (Level 4/5) to save patient lives, the cost is split 50/50 between carrier and enterprise emergency freight reserve.

### 4.4 Authorization Threshold
Autonomous AI authorization is limited to $500.00 USD. Expedited air upgrades between $500.01 and $1,000.00 require one-click Supply Chain Operations Manager digital approval.

## 5. Financial Matrices, Penalties & Liability Caps

- **Emergency Air Freight Cap**: $1,000.00 USD maximum recovery per sales order (VBAK-VBELN).
- **Carrier Chargeback Mechanism**: Direct automatic deduction from outstanding freight payables via SAP FI/CO credit memo within 5 business days.
- **Air Bill Audit Fee**: 10% administrative audit fee credited to enterprise if carrier disputes verified breakdown liability.

## 6. Exceptional Clauses & Relief Criteria

- **FAA Ground Stop / Air Traffic Embargo**: If commercial air cargo is grounded by federal aviation safety mandates, liability for air upgrade failure is fully excused.
- **Non-Perishable Commercial Freight**: Air freight upgrades are strictly barred for dry pet nutrition (PET_DRY) unless pre-authorized in writing by Customer Vice President.

## 7. Autonomous AI Enforcement & System of Record Actions

- **QualityMitigation agent identifies specialty diet stock-out risk > 24 hours**: Copilot pings air freight broker API, books priority space under $1,000 cap, and records liability code in SAP LIKP.
- **Air differential invoice received**: System matches air bill to original ground shipment VBELN and executes automated chargeback to at-fault carrier.
