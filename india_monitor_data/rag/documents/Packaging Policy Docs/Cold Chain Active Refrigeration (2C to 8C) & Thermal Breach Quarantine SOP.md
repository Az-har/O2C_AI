# Cold Chain Active Refrigeration (2C to 8C) & Thermal Breach Quarantine SOP

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | QA-SOP-2026-016-COLD |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Global Quality Assurance, Life Sciences Regulatory Compliance, & Cold Chain Logistics |
| **Material Classification** | Temperature-Sensitive Veterinary Biologics & Pharmaceuticals (MARA-MATKL = VET_MED) |
| **Target SAP Tables / Fields** | MARA (MATNR, MATKL, TEMPB), LIPS (WERKS, LGORT), LIKP (LIFSK, WBSTK) |

## 2. Commercial Purpose & Operational Context

Establishes strict quality assurance mandates, continuous IoT data logger monitoring, and quarantine procedures for veterinary biologicals, injectable therapeutics, vaccines, and insulin requiring continuous refrigeration between 2.0°C and 8.0°C (35.6°F to 46.4°F). Preserves efficacy and patient safety against thermal degradation.

## 3. Key Definitions & Operational Thresholds

- **Active Cold Chain Cargo**: Veterinary medical substances marked with SAP temperature condition code '02' requiring active mechanical refrigeration.
- **Thermal Excursion**: Any temperature reading exceeding 8.0°C or falling below 2.0°C recorded by NIST-calibrated continuous digital IoT data loggers.
- **SAP Quarantine Delivery Block 01**: A systematic lock placed on SAP LIKP delivery documents preventing commercial release or financial invoice billing until QA audit approval.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Continuous Active Monitoring
Reefer trailers and thermal containers must carry calibrated IoT cellular temperature sensors transmitting readings every fifteen (15) minutes to the AI Copilot telematics platform.

### 4.2 Critical Thermal Breach Definition
Any cumulative exposure above 8.0°C for greater than sixty (60) minutes, or any single transient spike above 15.0°C, constitutes an irreversible Critical Thermal Breach.

### 4.3 Freeze Damage Zero-Tolerance
Because freezing irreversibly denatures biological proteins, any temperature record falling below 0.0°C for more than fifteen (15) minutes requires immediate 100% batch condemnation.

### 4.4 Mandatory Quarantine Diversion
Upon thermal breach detection, the carrier must immediately halt transit and divert cargo to the nearest certified cold storage depot.

## 5. Financial Matrices, Penalties & Liability Caps

- **Carrier Liability for Spoiled Cargo**: Carrier liable for 100% of the invoice manufacturing cost of all condemned freight (MARA-NETPR * LIPS-LFIMG).
- **Replacement Freight Expedited Cost**: Carrier at fault must fund priority air replacement freight up to $1,000.00 USD per clinical order.
- **Certified Disposal Fee**: Hazardous biological disposal surcharge of $350.00 USD assessed against carrier if reefer unit mechanical failure caused excursion.

## 6. Exceptional Clauses & Relief Criteria

- **Pre-Cooling Calibration Grace Period**: Transient 15-minute thermal spikes during trailer door opening at loading dock are permissible if core probe remains < 6.0°C.
- **Catastrophic Sensor Malfunction**: If backup analog chemical phase-change indicator confirms no thaw, electronic false alarms may be overturned by QA Director.

## 7. Autonomous AI Enforcement & System of Record Actions

- **IoT sensor reports > 8.0°C for 60 minutes**: AI Copilot instantly writes Delivery Block '01' into SAP LIKP, notifies consignee clinic of replacement shipment, and files carrier claim.
- **Carrier driver attempts delivery of breached lot**: Consignee scanner rejects delivery barcode; goods diverted to QA quarantine storage.
