# Desert Southwest Extreme Ambient Heat (>42C) Transit Protocol

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | WTH-SOP-2026-004-HEAT |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Cold Chain Engineering, Fleet Maintenance, & Southwest Regional Safety |
| **Geographic Region** | Desert Southwest (Transit through Phoenix, Tucson, Las Vegas, Imperial Valley) |
| **Target SAP Tables / Fields** | VTTK (ROUTE), LIKP (VBELN, BTGEW), MARA (MATKL, SPECIALTY_DIET_FLAG) |

## 2. Commercial Purpose & Operational Context

Mitigates cargo thermal degradation, trailer tire blowout risks, and driver heat stroke during extreme summer temperature events exceeding 42.0°C (107.6°F) across the Desert Southwest logistics corridors. Enforces night-transit windows and thermal barrier protection for sensitive clinical nutrition.

## 3. Key Definitions & Operational Thresholds

- **Extreme Thermal Hazard (>42°C)**: Ambient outdoor temperature forecast exceeding 42.0°C recorded by NWS weather stations along Interstate 10, Interstate 8, or Interstate 40.
- **Nocturnal Transit Window**: Mandatory scheduling of long-haul linehaul driving strictly between 20:00 (8 PM) and 06:00 (6 AM) local time to avoid peak solar radiation.
- **Radiant Heat Pallet Barrier**: Heavy-duty reflective aluminum thermal barrier blankets placed over pallet loads to reflect radiant trailer ceiling heat.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Mandatory Nocturnal Linehaul
During declared Extreme Heat events, non-refrigerated trailers carrying veterinary nutrition must execute highway transit between 20:00 and 06:00. Daytime parking must utilize shaded rest facilities where available.

### 4.2 Refrigeration Requirement for Clinical Diets
All therapeutic prescription diets (VET_DIET) and medicines must be transported in refrigerated trailers with cooling units operating continuously at 20.0°C (68.0°F) or below.

### 4.3 Dock Door Exposure Limitation
Receiving docks in Phoenix, Tucson, and Las Vegas must complete pallet unloading and indoor air-conditioned staging within thirty (30) minutes of trailer door opening.

## 5. Financial Matrices, Penalties & Liability Caps

- **Thermal Spoilage Chargeback**: Carrier strictly liable for 100% cargo value if dry nutrition melts or spoils due to failure to utilize required nocturnal linehaul or thermal blankets.
- **Tire Blowout Delay Relief**: Delays caused by extreme asphalt heat tire delamination granted a 4-hour grace buffer, provided driver replaces tire and resumes transit within 6 hours.
- **Emergency Reefer Fuel Surcharge**: Approved $25.00 USD per day fuel allowance for continuous refrigeration unit operation during heat waves.

## 6. Exceptional Clauses & Relief Criteria

- **Active Refrigerated Intermodal Rail**: Cargo moving via refrigerated well-car container rail across desert corridors is exempt from nocturnal scheduling.
- **Short Final-Mile Drayage (< 50 miles)**: Final-mile delivery from local climate-controlled cross-dock to clinic allowed during morning hours (06:00–10:00).

## 7. Autonomous AI Enforcement & System of Record Actions

- **NWS forecast predicts Phoenix corridor temp >= 42°C**: Copilot checks dispatch schedule, reschedules linehaul departure for 20:00, and verifies reefer requirement in SAP.
- **IoT temperature sensor inside trailer exceeds 40°C**: Real-time thermal alert sent to driver and QA lead; delivery rerouted to emergency refrigerated cross-dock.
