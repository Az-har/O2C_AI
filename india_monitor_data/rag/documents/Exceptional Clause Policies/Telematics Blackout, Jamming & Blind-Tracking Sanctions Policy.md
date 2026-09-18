# Telematics Blackout, Jamming & Blind-Tracking Sanctions Policy

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | EXC-POL-2026-003-TELEM |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Asset Protection, Digital Supply Chain Security, & Logistics Legal |
| **Contractual Scope** | All Motor Carriers and Intermodal Logistics Providers |
| **Target SAP Tables / Fields** | LFA1 (LIFNR), VTTK (TKNUM), LIKP (VBELN), VBAK (KUNNR) |

## 2. Commercial Purpose & Operational Context

Enforces uninterrupted, real-time cellular and satellite IoT telematics visibility (project44, FourKites) for all commercial shipments carrying veterinary pharmaceuticals and clinical nutrition. Establishes severe commercial penalties and legal consequences for unannounced telematics blackouts, driver GPS tampering, or cargo abandonment.

## 3. Key Definitions & Operational Thresholds

- **Continuous Telematics Feed**: Automated cellular/satellite GPS location and temperature pings transmitted at intervals not exceeding fifteen (15) minutes during transit.
- **Telematics Blackout**: An unexplained cessation of GPS signal or telematics pings exceeding four (4.0) continuous hours while freight is in transit on commercial corridors.
- **Blind-Tracking Surcharge**: A punitive non-performance fee assessed against the carrier for operating in violation of the mandatory visibility charter.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Mandatory Visibility Charter
All contracted carriers must maintain active, certified API/EDI telematics integration with the enterprise tracking platform throughout linehaul transit.

### 4.2 Four-Hour Blackout Breach
Any signal loss exceeding four (4.0) consecutive hours without prior notification constitutes an immediate material breach of contract.

### 4.3 Nullification of Force Majeure Immunity
A carrier operating during a telematics blackout is legally barred from claiming weather-related Force Majeure exemptions. The burden of proof for cargo temperature and punctuality shifts entirely to the carrier.

### 4.4 GPS Jamming Zero-Tolerance
Intentional driver use of illegal GPS jamming devices or deliberate ELD manipulation results in immediate permanent carrier debarment and referral to federal law enforcement.

## 5. Financial Matrices, Penalties & Liability Caps

- **Blind-Tracking Surcharge**: $200.00 USD flat fee per blackout occurrence exceeding 4.0 hours.
- **Hourly Extended Blackout Fee**: $50.00 USD per additional hour past 4 hours until telematics signal is restored.
- **Cargo Audit Inspection Fee**: If biological cargo arrives following blackout, mandatory $350.00 QA thermal assay charged to carrier.
- **Permanent Debarment Clause**: Three (3) unexcused blackout violations within 90 days results in total contract cancellation.

## 6. Exceptional Clauses & Relief Criteria

- **Verified National Cellular Carrier Network Outage**: Documented major carrier network failures verified by carrier service advisories excuse signal loss.
- **Remote Mountain Canyons (Documented Dead Zones)**: Established geographic dead zones (< 2 hours duration) pre-mapped in telemetry database are exempt from penalties.

## 7. Autonomous AI Enforcement & System of Record Actions

- **Telematics feed silent for 4.0 hours**: Copilot flags shipment as 'BLIND_TRACKING_VIOLATION', issues $200 penalty in SAP, and alerts Corporate Asset Protection.
- **Signal restored**: Carrier required to submit ELD driver log verifying route continuity and temperature integrity within 24 hours.
