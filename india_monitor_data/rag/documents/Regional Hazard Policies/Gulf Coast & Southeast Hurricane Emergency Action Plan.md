# Gulf Coast & Southeast Hurricane Emergency Action Plan

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | WTH-SOP-2026-003-GULF |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Enterprise Emergency Management, Maritime Logistics, & Southeast Operations |
| **Geographic Region** | Southeast & Gulf Coast (Atlanta PL01 servicing GA, FL, SC, NC, AL, MS) |
| **Target SAP Tables / Fields** | VTTK (ROUTE, TPLST), LIKP (WERKS = 'PL01', VSTEL = 'SH01'), VBAK (KUNNR) |

## 2. Commercial Purpose & Operational Context

Governs preemptive supply chain adjustments, coastal freight embargoes, storm surge asset protections, and post-landfall relief operations for tropical storms and Category 1 through 5 hurricanes impacting the Gulf Coast and Southeastern seaboard. Balances life-safety mandatory evacuations with critical animal hospital disaster supplies.

## 3. Key Definitions & Operational Thresholds

- **NHC Hurricane Warning (36h Lead)**: National Hurricane Center notification that hurricane-force winds (>= 119 km/h / 74 mph) are expected within coastal territory within 36 hours.
- **Preemptive Advance Fulfillment (PAF)**: The automated advance shipment of 14 to 21 days of critical veterinary diets dispatched 72 hours prior to forecast storm landfall.
- **Coastal Transit Embargo**: Total cessation of commercial freight dispatches into mandatory coastal evacuation zones twenty-four (24) hours prior to projected landfall.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Preemptive Order Acceleration
Upon issuance of a 72-hour Hurricane Watch, the AI Copilot autonomously identifies all partner clinics in the projected cone of uncertainty and releases advance replenish orders from Atlanta PL01.

### 4.2 Mandatory 24-Hour Embargo
Twenty-four (24) hours prior to forecast landfall, all inbound freight movements into the evacuation zone are halted to ensure highways remain clear for civilian evacuation.

### 4.3 State of Emergency SLA Immunity
All SLA delivery mandates, delay penalties, and dock receiving rules are suspended 100% across the affected geographic region upon official gubernatorial declaration of state of emergency.

## 5. Financial Matrices, Penalties & Liability Caps

- **Hurricane Force Majeure Waiver**: Total 100% waiver of all SLA delay penalties throughout the state of emergency plus seventy-two (72) hours post-storm recovery.
- **Emergency Advance Order Freight Subsidy**: Enterprise covers 100% of expedited linehaul freight surcharges for advance disaster buffer stock dispatched to clinics.
- **Storm Surge Product Loss**: Freight destroyed by storm surge inundation covered under enterprise global marine cargo casualty insurance policy.

## 6. Exceptional Clauses & Relief Criteria

- **Official Post-Landfall Relief Convoy**: Carriers operating authorized humanitarian relief convoys under state police escort are exempt from curfew restrictions.
- **False Alarm / Dissipating Storm**: If storm veers out to sea or drops below tropical storm strength, standard transit operations and SLA rules resume within 24 hours.

## 7. Autonomous AI Enforcement & System of Record Actions

- **NHC forecasts Category 1+ landfall within 72 hours**: Copilot triggers Preemptive Advance Fulfillment orders in SAP, reserves dedicated reefer capacity at Atlanta PL01, and issues clinic advisories.
- **Gubernatorial State of Emergency signed**: System logs automatic blanket Force Majeure immunity in SAP for all affected ZIP codes.
