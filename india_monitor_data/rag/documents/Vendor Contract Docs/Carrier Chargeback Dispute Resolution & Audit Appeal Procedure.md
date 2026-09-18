# Carrier Chargeback Dispute Resolution & Audit Appeal Procedure

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | MVA-ADD-2026-020-DISP |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Freight Audit, Carrier Relations, Legal Counsel, & Accounts Payable |
| **Contractual Scope** | All Commercial Freight Carriers Subject to Autonomous AI Chargebacks |
| **Target SAP Tables / Fields** | LFA1 (LIFNR), BKPF (BELNR, AWKEY), BSEG (WRBTR, SHKZG), VTTK (TKNUM) |

## 2. Commercial Purpose & Operational Context

Establishes a transparent, legally enforceable, and rapid dispute resolution procedure providing motor carriers due process to challenge automated AI-generated delay penalties, blind tracking fees, or detention deductions. Guarantees fair adjudication, electronic evidence submission, and prompt refunding of overturned deductions.

## 3. Key Definitions & Operational Thresholds

- **AI Freight Chargeback**: An automated deduction executed in SAP FI/CO by the AI Logistics Copilot against carrier payable invoices for documented transit failures.
- **Dispute Filing Window**: A strict thirty (30) calendar day window from the date of SAP deduction remittance advice within which carrier must submit electronic rebuttal.
- **Certified Telematics Evidence Dossier**: Electronic submission of unedited ELD GPS traces, engine telematics, official police reports, or DOT road closure notices.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Right to Electronic Appeal
Carriers maintain the contractual right to challenge any autonomous penalty or chargeback by filing an appeal through the Carrier Web Portal within thirty (30) calendar days.

### 4.2 Mandatory Evidentiary Standard
Appeals must be accompanied by raw, unedited telematics data (ELD logs, GPS pings at 15-min intervals) demonstrating driver diligence, unannounced road blockage, or consignee default.

### 4.3 Ten-Day Adjudication Mandate
The enterprise Freight Audit Committee, supported by the AI Copilot Audit Panel, must adjudicate and render a binding decision within ten (10) business days of appeal submission.

### 4.4 Immediate Credit Execution
If an appeal is upheld, the full disputed amount will be credited back to the carrier's account in the next weekly SAP FI payment run without interest or penalty.

## 5. Financial Matrices, Penalties & Liability Caps

- **Dispute Appeal Filing Fee**: $0.00 USD (No cost to file legitimate contractual disputes).
- **Frivolous Dispute Administrative Fee**: $100.00 USD assessed if carrier submits repeated disputes without supporting telematics evidence.
- **Prompt Refund Guarantee**: Overturned chargebacks paid within seven (7) business days via direct electronic funds transfer (EFT).

## 6. Exceptional Clauses & Relief Criteria

- **Untimely Dispute Submission**: Disputes submitted past thirty (30) calendar days are barred by contractual limitation; deduction becomes final.
- **Carrier Concealment of Telematics**: Failure to provide requested ELD logs within 5 business days of request results in summary dismissal of appeal.

## 7. Autonomous AI Enforcement & System of Record Actions

- **Carrier submits dispute via portal with ELD trace**: Copilot ingest dispute payload, compares against historical weather and road speed databases, and prepares recommendation for Auditor.
- **Dispute approved by Freight Audit Lead**: Autonomous posting of SAP FI reversal credit memo (Document Type 'KG') crediting carrier vendor balance.
