# Consignee Default, Unauthorized Refusal & Redelivery Surcharge SOP

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | SLA-LOG-VNS-0032 |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Customer Service Operations, Transportation Accounting, & Logistics |
| **Customer Classification** | All Consignee Customer Tiers (Platinum, Gold, Silver, Bronze) |
| **Target SAP Tables / Fields** | KNA1 (ORT01), LIKP (ABLAD, VSTEL), VTTK (TKNUM), VBRK (NETWR) |

## 2. Commercial Purpose & Operational Context

Defines the legal rights, operational protocols, and financial liabilities when a consignee veterinary clinic causes an unexcused delivery failure by refusing a conforming shipment, locking clinic intake docks during posted receiving hours, or failing to maintain authorized receiving personnel. Protects carriers and shippers from unjustified SLA claims.

## 3. Key Definitions & Operational Thresholds

- **Consignee Default**: Failure of the receiving clinic to accept conforming freight tendered during posted receiving windows (08:00–17:00 Monday–Friday).
- **Unauthorized Refusal**: Refusal to sign Bill of Lading (POD) for undamaged goods due to clinic storage shortage, staff unavailability, or scheduling convenience.
- **Redelivery Surcharge**: A mandatory accessorial charge imposed to recover equipment, fuel, and driver labor for secondary delivery attempts.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Mandatory Receiving Window Availability
Clinics must maintain receiving capability during the operating hours recorded in SAP KNVV customer master. Dock personnel must commence unloading within 15 minutes of carrier arrival.

### 4.2 Burden of Proof for Refusal
Refusal of freight is lawful ONLY when physical product damage, thermal breach, or erroneous SKU delivery is verified and documented with timestamped photos on the driver's handheld device.

### 4.3 Nullification of Delay Claims
Any delivery delayed as a consequence of consignee default immediately forfeits all contractual SLA delay penalties. PDD compliance is legally deemed fulfilled at initial tender.

## 5. Financial Matrices, Penalties & Liability Caps

- **Standard Redelivery Surcharge**: $150.00 USD assessed against consignee account for secondary delivery attempt.
- **Extended Weekend / Layover Holding Fee**: $100.00 USD per 24 hours if freight must be held at carrier regional terminal due to Friday refusal.
- **Restocking & Return Freight Charge**: If consignee refuses redelivery, full two-way freight plus 15% restocking fee charged to consignee invoice.

## 6. Exceptional Clauses & Relief Criteria

- **Verified Clinic Catastrophic Emergency**: Power failure, structural facility damage, or biological quarantine exempts clinic from surcharge if reported prior to carrier arrival.
- **Non-Conforming Freight Delivery**: Consignee is exempt from refusal fees if delivered shipment contains wrong material numbers (MARA-MATNR) or compromised seals.

## 7. Autonomous AI Enforcement & System of Record Actions

- **Carrier driver logs 'Consignee Closed / Refused' with GPS proof**: AI Copilot flags delivery in SAP LIKP with status 'HELD_CONSIGNEE_DEFAULT', nullifies SLA clock, and issues $150.00 invoice debit to clinic.
- **Clinic disputes refusal charge**: Telematics GPS geofence validation and driver timestamp audited; claim resolved in 48 hours.
