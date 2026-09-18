# Pacific Northwest Atmospheric River & Mountain Pass Closure Protocol

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | WTH-SOP-2026-005-PNW |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Mountain Corridor Logistics, Pacific Northwest Safety, & Intermodal Ops |
| **Geographic Region** | Pacific Northwest (Washington, Oregon, Idaho - I-5, I-90, I-84 Mountain Corridors) |
| **Target SAP Tables / Fields** | VTTK (ROUTE), LIKP (VSTEL, VBELN), VBAK (KUNNR) |

## 2. Commercial Purpose & Operational Context

Governs freight navigation, chain-up safety mandates, rockslide diversions, and intermodal conversions across the Pacific Northwest mountain passes (Snoqualmie Pass, Stevens Pass, Siskiyou Pass, Columbia River Gorge) during severe winter atmospheric river rainfall and heavy Cascade mountain snowfall.

## 3. Key Definitions & Operational Thresholds

- **Atmospheric River Event**: A narrow corridor of concentrated moisture producing intense precipitation exceeding 75 mm (3 inches) in 24 hours, triggering mudslides and highway washouts.
- **Mandatory Mountain Pass Closure**: Official State DOT closure of I-90 Snoqualmie or I-5 mountain passes due to avalanche control, mudslides, or multi-rig jackknifes.
- **Columbia River Gorge Diversion**: Secondary southern detour utilizing Interstate 84 when northern Cascade mountain passes are impassable.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Mandatory Tire Chain Compliance
All motor carriers operating mountain passes between November 1 and April 1 must carry certified tire chains and comply with State DOT mandatory chain-up signage.

### 4.2 Pass Closure Rerouting Mandate
If mountain pass closure is projected to exceed twelve (12) hours, carrier dispatch must immediately reroute freight via Interstate 84 or request intermodal rail conversion.

### 4.3 Proactive 12-Hour Weather Notice
Carrier must transmit weather delay notification to Seattle, Tacoma, and Portland clinics at least twelve (12) hours prior to PDD to qualify for pass closure penalty waivers.

## 5. Financial Matrices, Penalties & Liability Caps

- **Mountain Pass Force Majeure Waiver**: 100% waiver of SLA delay penalties for verifiable state DOT pass closures, conditioned on 12-hour advance notice.
- **Detour Mileage Surcharge**: Shipper reimburses verified excess detour mileage (up to 250 miles at contractual fuel rate) for authorized southern highway diversions.
- **Failure to Carry Chains Penalty**: $500.00 USD non-compliance fee assessed against carrier if driver is stranded without required snow chains.

## 6. Exceptional Clauses & Relief Criteria

- **Intermodal Rail Conversion**: If freight is transferred to BNSF Northern Rail Corridor to bypass highway closures, customer SLA extended by 48 hours without penalty.
- **Coastal Highway Availability**: Shipments operating strictly on low-elevation coastal US-101 routes are exempt from mountain pass rules.

## 7. Autonomous AI Enforcement & System of Record Actions

- **WSDOT announces Snoqualmie Pass closure > 8 hours**: Copilot detects closure via DOT API feed, notifies impacted Seattle clinics, and updates SAP delivery schedule.
- **Carrier driver stranded due to lack of snow chains**: Penalty waiver denied; carrier assessed $500 fine and held 100% liable for resulting clinic delay penalties.
