# Midwest Winter Storm & Snowbelt Corridor (I-80 / I-90) Logistics Protocol

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | WTH-SOP-2026-001-MIDW |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Transportation Risk Operations, Regional Logistics Hubs, & Winter Safety |
| **Geographic Region** | Midwest Freight Corridor (Chicago PL02 servicing IL, IN, MI, WI, MN, IA, OH) |
| **Target SAP Tables / Fields** | VTTK (ROUTE, TPLST), LIKP (WERKS = 'PL02', VSTEL = 'SH02'), VBAK (KUNNR) |

## 2. Commercial Purpose & Operational Context

Establishes operational triggers, heated equipment requirements, route diversion criteria, and legal liability rules for commercial veterinary freight operating across the Midwest winter snowbelt (I-80, I-90, I-94 corridors). Protects driver safety, prevents freezing of therapeutic diets, and defines winter weather Force Majeure boundaries.

## 3. Key Definitions & Operational Thresholds

- **Midwest Winter Storm Warning**: Official National Weather Service (NWS) alert forecasting snowfall > 15 cm (6 inches) in 12 hours, sustained winds > 45 km/h, or freezing rain.
- **Protect From Freezing (PFF) Mandate**: Requirement to utilize active heated dry vans or thermal insulated blankets for liquid and canned veterinary therapeutic diets.
- **Intermodal Rail Bypass Trigger**: Preemptive diversion of linehaul freight to BNSF/Union Pacific intermodal rail when highway interstate closures exceed 24 hours.

## 4. Core Binding SLA / Policy Clauses

### 4.1 PFF Heated Equipment Requirement
Between November 1 and March 31, all shipments originating from Chicago PL02 containing wet diets (VET_WET) or pharmaceuticals must be tendered to carriers providing guaranteed heated van service maintaining cargo > 5.0°C.

### 4.2 Mandatory Interstate Closure Halt
If state DOT authorities close Interstate 80, 90, or 94 due to blizzard conditions or multi-vehicle pileups, drivers must immediately divert to designated safe truck stops.

### 4.3 Preemptive 12-Hour Weather Notice
Upon issuance of an NWS Winter Storm Warning along the transit route, carrier must transmit electronic notice to all downstream clinics within twelve (12) hours to preserve Force Majeure waiver eligibility.

## 5. Financial Matrices, Penalties & Liability Caps

- **Force Majeure Delay Waiver**: 100% waiver of standard delay penalties for shipments traversing officially closed DOT corridors, conditioned on timely 12h notice.
- **Freeze Spoilage Liability**: Carrier bears 100% replacement liability for frozen cargo if PFF heated trailer service was booked but heater unit was turned off or ran out of fuel.
- **Intermodal Transfer Cost Share**: Shipper pays 50% of rail drayage differential if intermodal bypass is authorized by AI Copilot.

## 6. Exceptional Clauses & Relief Criteria

- **Localized Lake-Effect Snow Squall**: Rapid unforecasted lake-effect squalls causing sudden pileups grant automatic 24-hour penalty grace upon state police verification.
- **Dry Kibble Exemption**: Dry pet nutrition (PET_DRY) is freeze-tolerant and exempt from heated van requirements, provided moisture barrier is unbroken.

## 7. Autonomous AI Enforcement & System of Record Actions

- **NWS issues Blizzard Warning for corridor overlapping VTTK route**: Copilot automatically tags shipment as 'WEATHER_DISRUPTED', alerts receiving clinics, and recalculates PDD + 48 hours.
- **Highway reopens**: Carrier required to resume linehaul within 4 hours; delay clock reactivates 6 hours post-reopening.
