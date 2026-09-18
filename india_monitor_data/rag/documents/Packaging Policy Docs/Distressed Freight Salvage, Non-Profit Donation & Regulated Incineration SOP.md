# Distressed Freight Salvage, Non-Profit Donation & Regulated Incineration SOP

**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**

---

## 1. Document Header & Scope

| Metadata Field | Parameter Value |
|---|---|
| **Document ID** | QA-SOP-2026-020-DISP |
| **Effective Date** | September 15, 2026 |
| **Controlling Department** | Sustainability, Legal Compliance, Quality Assurance, & Inventory Accounting |
| **Material Classification** | All Distressed, Refused, or Quarantined Veterinary Nutrition & Pharmaceuticals |
| **Target SAP Tables / Fields** | MARA (MATKL, SHELF_LIFE_MOS), LIPS (LFIMG), BKPF (BELNR, BUKRS), BSEG (WRBTR) |

## 2. Commercial Purpose & Operational Context

Governs the legally compliant, ethically responsible, and tax-optimized disposition of distressed, delayed, or cosmetically damaged veterinary freight. Establishes a rigorous decision hierarchy separating safe non-profit animal rescue shelter donations from mandatory high-temperature environmental incineration for hazardous pharmaceuticals.

## 3. Key Definitions & Operational Thresholds

- **Distressed Freight**: Cargo refused by consignees, damaged in transit, cosmetically flawed, or nearing minimum shelf-life thresholds (MARA-SHELF_LIFE_MOS < 3 months).
- **Non-Profit Rescue Donation**: Transfer of sound, wholesome nutrition with cosmetic carton damage to verified 501(c)(3) animal shelters per IRS Code Section 170(e)(3).
- **Regulated Incineration**: Mandatory high-temperature destruction (>1000°C) of pharmaceuticals, surgical items, or biologically adulterated goods at a certified EPA/state waste facility.

## 4. Core Binding SLA / Policy Clauses

### 4.1 Three-Tier Disposition Hierarchy
All distressed inventory must be classified into: Tier A (Commercial Restock), Tier B (Shelter Donation), or Tier C (Regulated Destruction).

### 4.2 Shelter Donation Criteria
Dry pet nutrition (PET_DRY) and intact canned diets with superficial exterior denting or carton crush, with at least 45 days remaining shelf life, must be donated to non-profit animal rescue partners.

### 4.3 Mandatory Destruction Criteria
All veterinary medications (VET_MED), opened prescription diets, sterile surgical sutures (SURGICAL), and thermally spoiled biologics are strictly barred from donation and must undergo certified incineration.

### 4.4 Certificate of Destruction (CoD) Mandate
A certified CoD signed by an EPA-licensed incinerator must be uploaded to SAP MM attachment directory within fourteen (14) days of scrap authorization.

## 5. Financial Matrices, Penalties & Liability Caps

- **Corporate Donation Tax Valuation**: Eligible for federal enhanced tax deduction under IRC 170(e)(3) equal to cost of goods plus one-half the mark-up value.
- **Destruction Processing Cost Allocation**: Incineration fee ($0.45/kg + $150 processing) charged to carrier if transit negligence caused condemnation.
- **Inventory Write-Off Accounting**: Automated posting in SAP FI/CO credit inventory account (G/L 130000) and debit salvage loss (G/L 680000).

## 6. Exceptional Clauses & Relief Criteria

- **Manufacturer Product Recall**: In the event of an FDA/USDA regulatory recall, all donation rights are suspended; 100% of lots must be quarantined for regulatory inspection.
- **Minor Secondary Carton Scuff**: If primary inner pouches are 100% pristine and > 6 months shelf life remains, goods may be repackaged for secondary distribution.

## 7. Autonomous AI Enforcement & System of Record Actions

- **QA flags shipment as 'CONDEMNED_UNRECOVERABLE'**: Copilot generates SAP Scrap Order (Movement Type 551), dispatches hazardous waste manifest to carrier, and tracks CoD completion.
- **Donation transfer approved by QA Lead**: SAP movement type 555 posted, Bill of Lading issued to verified 501(c)(3) animal sanctuary with tax receipt.
