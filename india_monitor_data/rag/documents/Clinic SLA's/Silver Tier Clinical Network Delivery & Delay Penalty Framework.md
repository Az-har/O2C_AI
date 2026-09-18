# Silver Tier Clinical Network Delivery & Delay Penalty Framework

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | SLA-LOG-VNS-0028 |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Global Supply Chain, Commercial Sales, & Accounts Receivable |
| **Customer Classification** | Tier 2 / Silver (Regional Animal Hospitals & Mid-Sized Clinics) |
| **Target SAP Tables / Fields** | KNA1, KNVV (KUNNR, VKORG, VTWEG), VBAK (NETWR, VDATU), LIKP (WADAT, WBSTK) |

## 2. Commercial Purpose & Operational Context

This Service Level Agreement establishes the binding transit standards, delay thresholds, and financial penalty frameworks governing commercial deliveries of veterinary nutrition, clinical diets, and medical supplies to Silver Tier clinical accounts. While Silver Tier partners operate with greater inventory resilience than Tier 1 critical trauma centers, timely receipt is mandatory to ensure outpatient treatment continuity and predictable cash flow.

## 3. Key Definitions & Operational Thresholds

- **Silver Tier Consignee**: Regional veterinary practices, mid-sized multi-doctor clinics, and specialized animal outpatient clinics registered with customer classification 'Tier 2' in SAP KNVV.
- **Promised Delivery Date (PDD)**: The contractual delivery date recorded at sales order confirmation in VBAK-VDATU and synchronized to outbound delivery LIKP-LFZIN.
- **Silver Grace Period**: A standard twenty-four (24) hour operational buffer following the 23:59 local time expiration of the PDD, within which deliveries are non-penalized if freight integrity is intact.
- **Proactive Notice Discount**: A 50% penalty credit granted when carrier or shipper transmits automated electronic notice at least twelve (12) hours prior to PDD expiration.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Standard Transit Obligation
Contracted motor carriers must tender and deliver consigned freight to the designated Silver Tier clinic dock during standard clinic receiving hours (08:00 to 17:00 local time) on or before the PDD.

### 4.2 Grace Period & Delay Inception
If freight is delivered within 24 hours following PDD expiration, no delay penalty shall accrue. Delay penalty assessment begins exactly at hour 24:01 past PDD expiration.

### 4.3 Proactive Notification Mandate
If a delay is predicted by logistics telematics, the Carrier must transmit an EDI 214 status event no less than twelve (12) hours prior to PDD. Compliance qualifies the delivery for a 50% penalty reduction.

### 4.4 Freight Condition Prerequisite
Grace period immunity is immediately revoked if goods suffer thermal excursion, packaging crush, or moisture contamination during transit, triggering full delay and damage liabilities.

## 5. Financial Matrices, Penalties & Liability Caps

- **Daily Delay Penalty**: $200.00 USD per calendar day (or fraction thereof exceeding 4 hours) beyond the 24-hour grace period.
- **Proactive Notice Adjusted Penalty**: $100.00 USD per calendar day if compliant 12-hour electronic notice was transmitted.
- **Cumulative Liability Cap**: Total delay penalties for any single shipment shall not exceed 10.0% of the net order value recorded in VBAK-NETWR.
- **Deduction Execution**: Autonomous debit memo posted via SAP FI/CO module offsetting outstanding carrier freight remittance.

## 6. Exceptional Clauses & Relief Criteria

- **Force Majeure Event**: 100% waiver of delay penalties upon verification of declared catastrophic weather (Level 4/5) or state of emergency, conditioned on 12-hour advance notice.
- **Consignee Receiving Refusal**: All delay penalties waived if carrier attempted delivery within receiving hours but clinic gates were locked or receiving staff was absent.

## 7. Autonomous AI Enforcement & System of Record Actions

- **Telemetry confirms delivery > PDD + 24h**: AI Logistics Copilot autonomously calculates delay days, applies notice discount if validated, and creates SAP credit memo to customer and debit chargeback to carrier.
- **Predicted delay exceeds 72 hours**: Automated alert dispatched to Customer Success Lead and secondary fulfillment plant for stock triage.
