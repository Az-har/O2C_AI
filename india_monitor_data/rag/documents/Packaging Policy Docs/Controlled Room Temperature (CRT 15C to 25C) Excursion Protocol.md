# Controlled Room Temperature (CRT 15C to 25C) Excursion Protocol

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | QA-SOP-2026-017-CRT |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Quality Assurance, Regulatory Affairs, & Domestic Distribution |
| **Material Classification** | Liquid Therapeutic Diets, Oral Suspensions, & Topical Ointments (MARA-MATKL = VET_DIET, VET_MED) |
| **Target SAP Tables / Fields** | MARA (MATKL, SHELF_LIFE_MOS), LIPS (WERKS, LFIMG), LIKP (VBELN) |

## 2. Commercial Purpose & Operational Context

Defines acceptable transit boundaries, Mean Kinetic Temperature (MKT) calculations, and disposition protocols for clinical nutrition liquids, suspensions, and veterinary pharmaceuticals labeled for Controlled Room Temperature (15°C to 25°C / 59°F to 77°F). Mitigates emulsion separation, active ingredient degradation, and packaging delamination during extreme seasonal ambient transit.

## 3. Key Definitions & Operational Thresholds

- **Controlled Room Temperature (CRT)**: A maintained environmental state between 15.0°C and 25.0°C with transient excursions permitted up to 30.0°C based on stability data.
- **Mean Kinetic Temperature (MKT)**: The single calculated isothermal temperature that corresponds to the kinetic effects of a temperature sequence over time per USP <1160>.
- **Accelerated Shelf-Life Degradation**: The exponential reduction in remaining shelf life (MARA-SHELF_LIFE_MOS) caused by thermal stress.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Permissible Short-Term Excursions
Freight may experience transient thermal exposure between 25.1°C and 30.0°C for a cumulative period not to exceed twenty-four (24.0) hours without compromising stability.

### 4.2 Extreme Heat Violation Threshold
Any thermal record exceeding 40.0°C (104.0°F) for greater than two (2.0) continuous hours constitutes a severe product adulteration event, voiding product warranty.

### 4.3 Refrigeration Requirement in Summer Lanes
Between May 15 and September 15, all freight traversing Desert Southwest corridors (Phoenix, Las Vegas, Dallas) must utilize climate-controlled dry vans set at 20°C.

## 5. Financial Matrices, Penalties & Liability Caps

- **Adulterated Cargo Replacement**: Full replacement value charged to carrier if failure to use protective climate controls is proven.
- **Accelerated Aging Discount**: If product experienced 30°C–39°C excursion for < 24h, QA may approve release subject to a 15% markdown absorbed by carrier.
- **QA Laboratory Re-Assay Charge**: $450.00 USD lab testing fee if specialized chemical assay required to confirm product viability.

## 6. Exceptional Clauses & Relief Criteria

- **Documented Thermal Protective Pallet Blankets**: Shipments utilizing validated thermal insulation blankets (R-value >= 4.0) are granted extended 48-hour excursion tolerance.
- **Non-Nutritive Ancillary Supplies**: Surgical instruments and non-perishable consumables co-loaded are exempt from CRT disposition.

## 7. Autonomous AI Enforcement & System of Record Actions

- **Corridor telemetry indicates ambient > 40°C on uninsulated dry van**: Copilot generates QA Warning, alerts consignee intake team to perform physical inspection upon arrival.
- **MKT calculation exceeds 28.0°C across transit duration**: Automatic SAP lot quarantine block posted; sample requisitioned for stability review.
