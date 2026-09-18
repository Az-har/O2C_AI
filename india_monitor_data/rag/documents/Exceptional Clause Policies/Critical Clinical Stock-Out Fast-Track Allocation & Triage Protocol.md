# Critical Clinical Stock-Out Fast-Track Allocation & Triage Protocol

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | EXC-POL-2026-005-STCK |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Clinical Veterinary Affairs, Emergency Triage Operations, & Customer Success |
| **Material Classification** | Life-Critical Prescription Nutrition & Urgent Therapeutics (MARA-SPECIALTY_DIET_FLAG = 'TRUE') |
| **Target SAP Tables / Fields** | MARA (MATNR, MATKL), KNA1 (KUNNR), VBAK (VBELN, NETWR), LIPS (LFIMG) |

## 2. Commercial Purpose & Operational Context

Establishes emergency inventory borrow-and-transfer mechanisms, local clinical hotshot delivery channels, and priority triage protocols when catastrophic transit disruptions threaten to cause complete life-safety stock-outs of essential therapeutic diets (Gastrointestinal, Renal, Hypoallergenic) at critical animal trauma hospitals.

## 3. Key Definitions & Operational Thresholds

- **Imminent Clinical Stock-Out**: A condition where a Tier 1 or Tier 2 hospital has less than twenty-four (24) hours of life-critical patient nutrition remaining due to an en-route transit delay.
- **Peer-Clinic Emergency Borrow**: The authorized transfer of sealed inventory from a nearby partner clinic within 50 miles to triage immediate animal patient needs.
- **Hotshot Courier Fast-Track**: Direct point-to-point dedicated courier transit bypassing all commercial freight terminals to deliver emergency supplies.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Clinical Stock-Out Declaration
A hospital veterinary director may declare an Imminent Stock-Out when verified patient diet inventory falls below 24 hours of clinical requirement and incoming delivery is delayed > 24 hours.

### 4.2 Tripartite Triage Protocol
The enterprise executes three simultaneous fast-track options: (1) Emergency borrow from closest partner clinic within 50 miles; (2) Next-Flight-Out counter-to-counter air cargo; and (3) Hotshot courier van from nearest plant hub.

### 4.3 Peer-Clinic Reimbursement Premium
Clinics providing emergency borrow stock receive an immediate credit memo equal to 110% of the invoice value, plus priority replenishment on the next morning delivery.

## 5. Financial Matrices, Penalties & Liability Caps

- **Emergency Borrow Transfer Subsidy**: 100% of transfer courier fees and clinic compensation absorbed by enterprise emergency mitigation budget.
- **110% Peer-Clinic Incentive Credit**: Loaning clinic credited 110% of standard order value in SAP FI/CO within 48 hours of inventory transfer.
- **Carrier Liability Passthrough**: If emergency triage was caused by carrier unexcused default, carrier is billed up to $1,000.00 USD of hotshot mitigation costs.

## 6. Exceptional Clauses & Relief Criteria

- **Patient Clinical Trial Non-Equivalence**: If patient is on double-blind clinical trial diet, peer-clinic borrow is prohibited; only factory-certified replacement allowed.
- **Open or Broken Inner Bag Packaging**: Only pristine, unopened, factory-sealed bags may be transferred between clinics under peer borrow protocol.

## 7. Autonomous AI Enforcement & System of Record Actions

- **Hospital alerts Copilot to < 24h stock on specialty diet**: QualityMitigation agent queries nearby clinic inventory in SAP KNA1/KNVV, identifies closest source, and drafts hotshot dispatch.
- **Peer clinic confirms stock release**: Copilot dispatches local medical courier, issues 110% credit memo to loaning clinic, and closes stock-out alert.
