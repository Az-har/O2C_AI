# Motor Carrier Dock Detention & Free-Time Demurrage Policy

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | MVA-ADD-2026-016-DET |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Transportation Management, Freight Audit, & Plant Warehouse Operations |
| **Contractual Scope** | All Contracted Full Truckload (FTL) and Less-Than-Truckload (LTL) Motor Carriers |
| **Target SAP Tables / Fields** | LFA1 (LIFNR), VTTK (TKNUM, DPABF, DPTEN), VTTP (VBELN) |

## 2. Commercial Purpose & Operational Context

Standardizes the commercial rules, electronic logging device (ELD) timestamp verifications, and financial rates governing driver and equipment detention at manufacturing plants (PL01, PL02, PL03) and destination clinic receiving docks. Eliminates invoice friction, enforces appointment discipline, and provides fair compensation for loading delays.

## 3. Key Definitions & Operational Thresholds

- **Free Time Allowance**: A standard period of two (2.0) hours (120 minutes) granted to the shipper or consignee for loading or unloading without demurrage surcharge.
- **Detention Demurrage**: An hourly compensation rate paid to the carrier for equipment and driver idle time exceeding the contractual Free Time Allowance.
- **Geofenced Telematics Verification**: Automated confirmation of tractor arrival, dock door coupling, and facility departure recorded via cellular GPS geofencing.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Punctuality Condition Precedent
To qualify for detention compensation, the Carrier must arrive within fifteen (±15) minutes of the scheduled dock appointment time recorded in the appointment management system.

### 4.2 Free Time Commencement
Free time begins precisely when the driver checks in with shipping/receiving personnel, or upon confirmed geofenced dock door coupling, whichever is verified electronically.

### 4.3 Shipper vs Consignee Detention Responsibility
Detention incurred at plants (PL01, PL02, PL03) is reimbursed directly by the enterprise. Detention incurred at customer docks due to clinic default is back-charged to the consignee.

### 4.4 Maximum Daily Cap
Standard detention is capped at six (6.0) billable hours per 24-hour cycle, after which the driver is entitled to layover compensation.

## 5. Financial Matrices, Penalties & Liability Caps

- **Hourly Detention Rate**: $85.00 USD per hour, billed in fifteen (15) minute increments ($21.25/quarter-hour) after 120 minutes free time.
- **Full Layover Day Rate**: $450.00 USD flat layover rate if shipper/consignee holds tractor overnight (> 8 hours past appointment).
- **Driver Detention Claim Window**: Detention claims must be submitted electronically via EDI 210 with ELD logs within fourteen (14) calendar days.

## 6. Exceptional Clauses & Relief Criteria

- **Late Driver Arrival**: If driver arrives > 30 minutes late for appointment, driver is placed on work-in queue; all detention rights are forfeited for that facility.
- **Carrier Packaging Defect**: If unloading is halted due to leaking, fallen, or improperly secured pallets caused by carrier transit negligence, detention is void.

## 7. Autonomous AI Enforcement & System of Record Actions

- **ELD verifies tractor on dock > 120 minutes with on-time arrival**: Copilot automatically approves detention accessorial voucher and creates payable item in SAP FI for carrier payment run.
- **Carrier submits manual detention invoice without telematics proof**: Automatic system rejection; carrier notified to provide ELD GPS trace.
