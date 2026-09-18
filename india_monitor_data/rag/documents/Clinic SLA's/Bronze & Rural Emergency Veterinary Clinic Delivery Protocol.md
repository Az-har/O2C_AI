# Bronze & Rural Emergency Veterinary Clinic Delivery Protocol

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | SLA-LOG-VNS-0029 |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Global Supply Chain, Rural Logistics, & Customer Experience |
| **Customer Classification** | Tier 3 / Bronze / Independent Practices |
| **Target SAP Tables / Fields** | KNA1 (ORT01, REGIO, PSTLZ), VBAK (AUART, NETWR), LIKP (ROUTE, VSTEL) |

## 2. Commercial Purpose & Operational Context

This protocol governs delivery execution, extended transit buffers, and delay adjudication for independent rural veterinary practices, sole practitioners, and remote agricultural clinics located outside core metropolitan freight lanes. It balances extended geographic transit realities with emergency clinical nutritional imperatives.

## 3. Key Definitions & Operational Thresholds

- **Rural Tier 3 Clinic**: Veterinary practices located in designated non-metropolitan postal codes exceeding 150 miles from the nearest plant fulfillment hub (PL01, PL02, PL03).
- **Rural Route Buffer**: A mandatory contractual tolerance of forty-eight (48) hours past PDD recognized for long-haul LTL drayage and interline carrier handoffs.
- **Emergency Prescription Flag**: Orders tagged with MARA-SPECIALTY_DIET_FLAG = 'TRUE' or urgent veterinary medication requiring priority protection.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Transit Lead Time & Extended Buffer
Recognizing that rural freight involves intermediate terminal transfers, carriers are granted a 48-hour delivery buffer beyond standard urban PDD baselines.

### 4.2 Emergency Nutrition Fast-Track
If a rural order contains critical veterinary prescription diets (VET_DIET), the 48-hour buffer is suspended. Carrier must maintain direct linehaul delivery without terminal dwell exceeding 12 hours.

### 4.3 Interline Carrier Accountability
Primary contracted carriers who subcontract final-mile delivery to rural regional interline couriers remain 100% legally and financially responsible for performance.

## 5. Financial Matrices, Penalties & Liability Caps

- **Daily Delay Penalty**: $100.00 USD per calendar day beyond the 48-hour rural buffer.
- **Cumulative Liability Cap**: Total delay penalties capped at 5.0% of order net value (VBAK-NETWR) or $300.00 USD maximum per shipment.
- **Emergency Stock-Out Recovery Surcharge**: If prescription diet failure forces clinic to source emergency local feed, carrier reimburses up to $250.00 USD in substitute nutrition costs upon proof of fault.

## 6. Exceptional Clauses & Relief Criteria

- **Unpassable Rural Road Infrastructure**: Documented seasonal washouts, mudslides, or county road closures verified by State DOT grant immediate penalty waiver.
- **Farm / Mobile Vet Unattended Drop**: If clinic authorises an unattended farm-gate drop, risk of loss and delivery delay terminates upon geofenced delivery scan.

## 7. Autonomous AI Enforcement & System of Record Actions

- **Rural shipment delay > 48 hours**: Copilot initiates automated check of regional feeder terminal EDI 214 and notifies rural clinic manager via SMS/Email.
- **Critical Rx diet delayed > 24 hours in rural zone**: QualityMitigation agent triggers automated courier quote for same-day hotshot dispatch from closest regional distributor.
