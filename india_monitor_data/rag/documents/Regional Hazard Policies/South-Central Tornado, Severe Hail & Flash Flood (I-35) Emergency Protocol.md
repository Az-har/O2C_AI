# South-Central Tornado, Severe Hail & Flash Flood (I-35) Emergency Protocol

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | WTH-SOP-2026-002-SCEN |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Disaster Response, Fleet Safety, & South-Central Regional Logistics |
| **Geographic Region** | South-Central Corridor (Dallas PL03 servicing TX, OK, KS, MO, AR, LA) |
| **Target SAP Tables / Fields** | VTTK (ROUTE, TPLST), LIKP (WERKS = 'PL03', VSTEL = 'SH03'), VBAK (KUNNR) |

## 2. Commercial Purpose & Operational Context

Establishes emergency response procedures, driver safety protocols, and commercial claim boundaries for tornadoes, severe hail outbreaks (> 1.5 inch diameter), and catastrophic flash flooding across the Interstate 35 and Interstate 40 transit lanes. Prioritizes human life preservation while maintaining clinical diet supply chains.

## 3. Key Definitions & Operational Thresholds

- **Tornado Warning (Severe Threat)**: NWS confirmation that a tornado is occurring or imminent; immediate trigger for freight transit suspension within the warning polygon.
- **Hail Protection Shelter Protocol**: Mandatory parking of commercial tractors and trailers beneath covered structures or reinforced fuel canopies when hail > 1.5 inches is predicted.
- **Flash Flood Inundation Zone**: Low-lying highway segments experiencing water over roadway exceeding 15 cm (6 inches); strict prohibition against crossing.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Immediate Shelter-In-Place Mandate
When a Tornado Warning polygon intersects a commercial vehicle's GPS coordinates, driver is legally mandated to seek hardened shelter immediately. Commercial transit must remain suspended until warning expires.

### 4.2 Flash Flood Rerouting Obligation
Drivers must never drive into standing floodwaters. Carrier dispatch must utilize dynamic GPS rerouting to circumvent submerged river valleys and low-water crossings.

### 4.3 Proactive 12-Hour Weather Notice
Carrier must transmit weather disruption notification to destination clinics and Copilot within twelve (12) hours of severe storm outbreak to qualify for Act of God immunity.

## 5. Financial Matrices, Penalties & Liability Caps

- **Tornadic / Flood Delay Immunity**: 100% waiver of SLA delay penalties for duration of active NWS warnings plus twelve (12) hours road recovery window.
- **Flood Cargo Destruction Liability**: Carrier strictly liable for 100% of cargo losses if driver drowns engine or trailer by entering marked high-water flood zones.
- **Hail Damage Liability Waiver**: Tractor cosmetic hail damage is non-compensable; trailer roof puncture resulting in cargo water damage requires carrier liability insurance claim.

## 6. Exceptional Clauses & Relief Criteria

- **Unheralded Nighttime Tornadogenesis**: Tornadoes touching down with < 10 minutes NWS lead time grant immediate, total penalty exoneration for affected carriers.
- **Consignee Clinic Flood Damage**: If destination veterinary clinic is flooded, clinic receiving surcharge waived and cargo held at terminal free for 7 days.

## 7. Autonomous AI Enforcement & System of Record Actions

- **NOAA API confirms active Tornado Warning intersecting tractor coordinates**: Copilot dispatches emergency safety SMS to driver, flags order in SAP with Force Majeure waiver code.
- **Flood halts I-35 transit > 24 hours**: Copilot calculates alternate transit route via I-20 / I-45 and re-optimizes delivery schedule.
