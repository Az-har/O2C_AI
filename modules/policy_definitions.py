"""
Enterprise Policy & SLA Definitions Catalog.
Contains complete, legally binding, operationally rigorous specifications for 25 policy documents
aligned with the SAP ERP Order-to-Cash (O2C) synthetic data and industry best practices.
"""

import os
import sys
from pathlib import Path

# Add project root and modules to path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

POLICY_DOCUMENTS = [
    # =========================================================================
    # CATEGORY 1: CLINIC SLAS & GPO MASTER AGREEMENTS
    # Target Directory: Clinic SLA's/
    # =========================================================================
    {
        "category": "Clinic SLA's",
        "file_stem": "Silver Tier Clinical Network Delivery & Delay Penalty Framework",
        "title": "Silver Tier Clinical Network Delivery & Delay Penalty Framework",
        "header": {
            "Document ID": "SLA-LOG-VNS-0028",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Global Supply Chain, Commercial Sales, & Accounts Receivable",
            "Customer Classification": "Tier 2 / Silver (Regional Animal Hospitals & Mid-Sized Clinics)",
            "Target SAP Tables / Fields": "KNA1, KNVV (KUNNR, VKORG, VTWEG), VBAK (NETWR, VDATU), LIKP (WADAT, WBSTK)"
        },
        "purpose": (
            "This Service Level Agreement establishes the binding transit standards, delay thresholds, and financial "
            "penalty frameworks governing commercial deliveries of veterinary nutrition, clinical diets, and medical supplies "
            "to Silver Tier clinical accounts. While Silver Tier partners operate with greater inventory resilience than Tier 1 "
            "critical trauma centers, timely receipt is mandatory to ensure outpatient treatment continuity and predictable cash flow."
        ),
        "definitions": [
            {"term": "Silver Tier Consignee", "definition": "Regional veterinary practices, mid-sized multi-doctor clinics, and specialized animal outpatient clinics registered with customer classification 'Tier 2' in SAP KNVV."},
            {"term": "Promised Delivery Date (PDD)", "definition": "The contractual delivery date recorded at sales order confirmation in VBAK-VDATU and synchronized to outbound delivery LIKP-LFZIN."},
            {"term": "Silver Grace Period", "definition": "A standard twenty-four (24) hour operational buffer following the 23:59 local time expiration of the PDD, within which deliveries are non-penalized if freight integrity is intact."},
            {"term": "Proactive Notice Discount", "definition": "A 50% penalty credit granted when carrier or shipper transmits automated electronic notice at least twelve (12) hours prior to PDD expiration."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Standard Transit Obligation", "text": "Contracted motor carriers must tender and deliver consigned freight to the designated Silver Tier clinic dock during standard clinic receiving hours (08:00 to 17:00 local time) on or before the PDD."},
            {"num": "4.2", "title": "Grace Period & Delay Inception", "text": "If freight is delivered within 24 hours following PDD expiration, no delay penalty shall accrue. Delay penalty assessment begins exactly at hour 24:01 past PDD expiration."},
            {"num": "4.3", "title": "Proactive Notification Mandate", "text": "If a delay is predicted by logistics telematics, the Carrier must transmit an EDI 214 status event no less than twelve (12) hours prior to PDD. Compliance qualifies the delivery for a 50% penalty reduction."},
            {"num": "4.4", "title": "Freight Condition Prerequisite", "text": "Grace period immunity is immediately revoked if goods suffer thermal excursion, packaging crush, or moisture contamination during transit, triggering full delay and damage liabilities."}
        ],
        "financial": [
            {"item": "Daily Delay Penalty", "detail": "$200.00 USD per calendar day (or fraction thereof exceeding 4 hours) beyond the 24-hour grace period."},
            {"item": "Proactive Notice Adjusted Penalty", "detail": "$100.00 USD per calendar day if compliant 12-hour electronic notice was transmitted."},
            {"item": "Cumulative Liability Cap", "detail": "Total delay penalties for any single shipment shall not exceed 10.0% of the net order value recorded in VBAK-NETWR."},
            {"item": "Deduction Execution", "detail": "Autonomous debit memo posted via SAP FI/CO module offsetting outstanding carrier freight remittance."}
        ],
        "exceptions": [
            {"condition": "Force Majeure Event", "detail": "100% waiver of delay penalties upon verification of declared catastrophic weather (Level 4/5) or state of emergency, conditioned on 12-hour advance notice."},
            {"condition": "Consignee Receiving Refusal", "detail": "All delay penalties waived if carrier attempted delivery within receiving hours but clinic gates were locked or receiving staff was absent."}
        ],
        "enforcement": [
            {"trigger": "Telemetry confirms delivery > PDD + 24h", "action": "AI Logistics Copilot autonomously calculates delay days, applies notice discount if validated, and creates SAP credit memo to customer and debit chargeback to carrier."},
            {"trigger": "Predicted delay exceeds 72 hours", "action": "Automated alert dispatched to Customer Success Lead and secondary fulfillment plant for stock triage."}
        ]
    },

    {
        "category": "Clinic SLA's",
        "file_stem": "Bronze & Rural Emergency Veterinary Clinic Delivery Protocol",
        "title": "Bronze & Rural Emergency Veterinary Clinic Delivery Protocol",
        "header": {
            "Document ID": "SLA-LOG-VNS-0029",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Global Supply Chain, Rural Logistics, & Customer Experience",
            "Customer Classification": "Tier 3 / Bronze / Independent Practices",
            "Target SAP Tables / Fields": "KNA1 (ORT01, REGIO, PSTLZ), VBAK (AUART, NETWR), LIKP (ROUTE, VSTEL)"
        },
        "purpose": (
            "This protocol governs delivery execution, extended transit buffers, and delay adjudication for independent "
            "rural veterinary practices, sole practitioners, and remote agricultural clinics located outside core metropolitan "
            "freight lanes. It balances extended geographic transit realities with emergency clinical nutritional imperatives."
        ),
        "definitions": [
            {"term": "Rural Tier 3 Clinic", "definition": "Veterinary practices located in designated non-metropolitan postal codes exceeding 150 miles from the nearest plant fulfillment hub (PL01, PL02, PL03)."},
            {"term": "Rural Route Buffer", "definition": "A mandatory contractual tolerance of forty-eight (48) hours past PDD recognized for long-haul LTL drayage and interline carrier handoffs."},
            {"term": "Emergency Prescription Flag", "definition": "Orders tagged with MARA-SPECIALTY_DIET_FLAG = 'TRUE' or urgent veterinary medication requiring priority protection."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Transit Lead Time & Extended Buffer", "text": "Recognizing that rural freight involves intermediate terminal transfers, carriers are granted a 48-hour delivery buffer beyond standard urban PDD baselines."},
            {"num": "4.2", "title": "Emergency Nutrition Fast-Track", "text": "If a rural order contains critical veterinary prescription diets (VET_DIET), the 48-hour buffer is suspended. Carrier must maintain direct linehaul delivery without terminal dwell exceeding 12 hours."},
            {"num": "4.3", "title": "Interline Carrier Accountability", "text": "Primary contracted carriers who subcontract final-mile delivery to rural regional interline couriers remain 100% legally and financially responsible for performance."}
        ],
        "financial": [
            {"item": "Daily Delay Penalty", "detail": "$100.00 USD per calendar day beyond the 48-hour rural buffer."},
            {"item": "Cumulative Liability Cap", "detail": "Total delay penalties capped at 5.0% of order net value (VBAK-NETWR) or $300.00 USD maximum per shipment."},
            {"item": "Emergency Stock-Out Recovery Surcharge", "detail": "If prescription diet failure forces clinic to source emergency local feed, carrier reimburses up to $250.00 USD in substitute nutrition costs upon proof of fault."}
        ],
        "exceptions": [
            {"condition": "Unpassable Rural Road Infrastructure", "detail": "Documented seasonal washouts, mudslides, or county road closures verified by State DOT grant immediate penalty waiver."},
            {"condition": "Farm / Mobile Vet Unattended Drop", "detail": "If clinic authorises an unattended farm-gate drop, risk of loss and delivery delay terminates upon geofenced delivery scan."}
        ],
        "enforcement": [
            {"trigger": "Rural shipment delay > 48 hours", "action": "Copilot initiates automated check of regional feeder terminal EDI 214 and notifies rural clinic manager via SMS/Email."},
            {"trigger": "Critical Rx diet delayed > 24 hours in rural zone", "action": "QualityMitigation agent triggers automated courier quote for same-day hotshot dispatch from closest regional distributor."}
        ]
    },

    {
        "category": "Clinic SLA's",
        "file_stem": "Academic & Veterinary Teaching Hospital Zero-Defect Master SLA",
        "title": "Academic & Veterinary Teaching Hospital Zero-Defect Master SLA",
        "header": {
            "Document ID": "SLA-LOG-VNS-0030",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Enterprise Healthcare Logistics, Quality Assurance, & Legal Affairs",
            "Customer Classification": "Tier 1A / Academic Veterinary Medical Centers & Research Institutions",
            "Target SAP Tables / Fields": "KNA1 (KUNNR, KTOKD), VBAK (AUART, VDATU), MARA (MATNR, MATKL), LIKP (VBELN)"
        },
        "purpose": (
            "Establishes a zero-defect delivery mandate for accredited university veterinary teaching hospitals, ICU veterinary trauma "
            "facilities, and clinical trial research facilities. Deliveries to these institutions directly impact ongoing clinical "
            "surgical trials and critical patient intensive care units, demanding strict schedule adherence and rigorous batch documentation."
        ),
        "definitions": [
            {"term": "Tier 1A Academic Consignee", "definition": "University-affiliated veterinary hospitals, veterinary clinical trial research centers, and tertiary referral emergency centers."},
            {"term": "Zero-Tolerance Delivery Window", "definition": "A mandatory delivery appointment window of plus or minus thirty (±30) minutes with zero (0) grace period tolerance."},
            {"term": "Batch Documentation Dossier", "definition": "Manufacturer Certificates of Analysis (CoA), sterile release certificates, and chain-of-custody temperature logs mandatory upon delivery."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Zero Grace Period Execution", "text": "Due to strict hospital pharmacy intake schedules, deliveries arriving outside the confirmed dock appointment window are classified as non-compliant."},
            {"num": "4.2", "title": "Mandatory Batch Traceability", "text": "Every shipment containing surgical products (MARA-MATKL = SURGICAL) or specialty diets must include physical and electronic CoA documentation matching SAP batch records."},
            {"num": "4.3", "title": "Rapid Escalation Threshold", "text": "Any predicted delivery delay exceeding four (4.0) hours requires immediate dispatch of high-priority alerts to the Hospital Director of Pharmacy and enterprise logistics command."}
        ],
        "financial": [
            {"item": "Tier 1A Delay Penalty", "detail": "$750.00 USD per calendar day (or fraction thereof exceeding 2 hours) past the scheduled appointment window."},
            {"item": "Documentation Non-Compliance Surcharge", "detail": "$250.00 USD per occurrence for missing, illegible, or mismatched Certificate of Analysis documentation."},
            {"item": "Emergency Surgical Surgery Reschedule Indemnity", "detail": "Carrier liable for up to $1,500.00 USD in verified clinic preparation costs if late delivery causes cancellation of scheduled patient surgery."}
        ],
        "exceptions": [
            {"condition": "Certified Campus Security Lockout", "detail": "University-wide police or security lockdowns verified by official university dispatch grant full penalty relief."},
            {"condition": "Hospital Receiving Dock Refusal Due to Surge", "detail": "If hospital ICU emergency forces temporary dock closure, carrier granted detention pay and penalty immunity."}
        ],
        "enforcement": [
            {"trigger": "Delay prediction > 2 hours for Tier 1A", "action": "Copilot autonomously pings carrier dispatch via API, escalates to National Logistics Director, and prepares backup courier dispatch."},
            {"trigger": "Delivery confirmed > appointment window", "action": "Automatic posting of $750.00 debit memo to SAP Accounts Payable against carrier contract."}
        ]
    },

    {
        "category": "Clinic SLA's",
        "file_stem": "Corporate Group Purchasing Organization (GPO) Performance & Rebate Clawback SLA",
        "title": "Corporate Group Purchasing Organization (GPO) Performance & Rebate Clawback SLA",
        "header": {
            "Document ID": "SLA-LOG-VNS-0031",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Commercial Contracts, Enterprise GPO Management, & Finance",
            "Customer Classification": "Corporate Enterprise Group Purchasing Organizations (GPOs)",
            "Target SAP Tables / Fields": "KNVV (VKORG, VTWEG, KUNNR), VBAK (NETWR), LIKP (WBSTK), VBRK (NETWR, RFBSK)"
        },
        "purpose": (
            "Governs the aggregated supply chain performance obligations, monthly On-Time In-Full (OTIF) thresholds, and volume "
            "rebate penalty clawbacks established under multi-unit corporate veterinary group purchasing agreements. Establishes "
            "commercial alignment across enterprise chains representing hundreds of clinic locations."
        ),
        "definitions": [
            {"term": "GPO Master Entity", "definition": "A corporate veterinary management group representing a consolidated network of clinic member facilities under a master procurement contract."},
            {"term": "On-Time In-Full (OTIF) Index", "definition": "The monthly ratio of deliveries meeting both Promised Delivery Date (within 24h grace) and 100% quantity fulfillment without stock-out split."},
            {"term": "Volume Rebate Clawback", "definition": "Contractual forfeiture of corporate quarterly rebate payouts assessed against the enterprise when supply chain failures breach agreed OTIF floors."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Consolidated OTIF Benchmark", "text": "The enterprise commits to delivering a monthly minimum OTIF score of 96.0% across all member clinics under the GPO master agreement."},
            {"num": "4.2", "title": "Measurement Period & Data Source", "text": "OTIF performance is calculated autonomously on the last calendar day of each month based on SAP LIKP goods issue timestamps and carrier EDI 214 delivery scans."},
            {"num": "4.3", "title": "Carrier Accountability Passthrough", "text": "When failure to meet GPO OTIF floors is directly attributable to contracted 3PL carrier transit defaults, all associated rebate penalties are passed through to the non-performing carriers."}
        ],
        "financial": [
            {"item": "OTIF 93.0% to 95.9% (Tier 1 Default)", "detail": "Mandatory 2.5% reduction in monthly enterprise rebate payout across all participating member accounts."},
            {"item": "OTIF 90.0% to 92.9% (Tier 2 Default)", "detail": "Mandatory 5.0% reduction in monthly enterprise rebate payout plus a $10,000.00 USD administrative cure credit."},
            {"item": "OTIF Below 90.0% (Critical Default)", "detail": "Immediate right of GPO to terminate exclusive procurement and source alternative diets at enterprise expense."},
            {"item": "Carrier Passthrough Recovery", "detail": "Carriers failing their individual 96% SLA allocated proportional share of GPO rebate deduction."}
        ],
        "exceptions": [
            {"condition": "Widespread Verified Force Majeure", "detail": "Orders impacted by national or regional meteorological disasters are excluded from monthly OTIF denominator calculations."},
            {"condition": "Consignee Scheduled Order Surges", "detail": "Unforecasted clinic order surges exceeding 200% of 90-day average demand excluded from OTIF calculation if notified < 7 days in advance."}
        ],
        "enforcement": [
            {"trigger": "Month-end OTIF calculation < 96.0%", "action": "Financial settlement engine calculates rebate clawback, executes credit memo adjustments in SAP VBRK, and issues performance report to GPO executive board."},
            {"trigger": "Carrier monthly OTIF < 95.0%", "action": "Carrier allocation reduced by 15% in next quarterly freight bidding cycle."}
        ]
    },

    {
        "category": "Clinic SLA's",
        "file_stem": "Consignee Default, Unauthorized Refusal & Redelivery Surcharge SOP",
        "title": "Consignee Default, Unauthorized Refusal & Redelivery Surcharge SOP",
        "header": {
            "Document ID": "SLA-LOG-VNS-0032",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Customer Service Operations, Transportation Accounting, & Logistics",
            "Customer Classification": "All Consignee Customer Tiers (Platinum, Gold, Silver, Bronze)",
            "Target SAP Tables / Fields": "KNA1 (ORT01), LIKP (ABLAD, VSTEL), VTTK (TKNUM), VBRK (NETWR)"
        },
        "purpose": (
            "Defines the legal rights, operational protocols, and financial liabilities when a consignee veterinary clinic "
            "causes an unexcused delivery failure by refusing a conforming shipment, locking clinic intake docks during posted "
            "receiving hours, or failing to maintain authorized receiving personnel. Protects carriers and shippers from unjustified SLA claims."
        ),
        "definitions": [
            {"term": "Consignee Default", "definition": "Failure of the receiving clinic to accept conforming freight tendered during posted receiving windows (08:00–17:00 Monday–Friday)."},
            {"term": "Unauthorized Refusal", "definition": "Refusal to sign Bill of Lading (POD) for undamaged goods due to clinic storage shortage, staff unavailability, or scheduling convenience."},
            {"term": "Redelivery Surcharge", "definition": "A mandatory accessorial charge imposed to recover equipment, fuel, and driver labor for secondary delivery attempts."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Mandatory Receiving Window Availability", "text": "Clinics must maintain receiving capability during the operating hours recorded in SAP KNVV customer master. Dock personnel must commence unloading within 15 minutes of carrier arrival."},
            {"num": "4.2", "title": "Burden of Proof for Refusal", "text": "Refusal of freight is lawful ONLY when physical product damage, thermal breach, or erroneous SKU delivery is verified and documented with timestamped photos on the driver's handheld device."},
            {"num": "4.3", "title": "Nullification of Delay Claims", "text": "Any delivery delayed as a consequence of consignee default immediately forfeits all contractual SLA delay penalties. PDD compliance is legally deemed fulfilled at initial tender."}
        ],
        "financial": [
            {"item": "Standard Redelivery Surcharge", "detail": "$150.00 USD assessed against consignee account for secondary delivery attempt."},
            {"item": "Extended Weekend / Layover Holding Fee", "detail": "$100.00 USD per 24 hours if freight must be held at carrier regional terminal due to Friday refusal."},
            {"item": "Restocking & Return Freight Charge", "detail": "If consignee refuses redelivery, full two-way freight plus 15% restocking fee charged to consignee invoice."}
        ],
        "exceptions": [
            {"condition": "Verified Clinic Catastrophic Emergency", "detail": "Power failure, structural facility damage, or biological quarantine exempts clinic from surcharge if reported prior to carrier arrival."},
            {"condition": "Non-Conforming Freight Delivery", "detail": "Consignee is exempt from refusal fees if delivered shipment contains wrong material numbers (MARA-MATNR) or compromised seals."}
        ],
        "enforcement": [
            {"trigger": "Carrier driver logs 'Consignee Closed / Refused' with GPS proof", "action": "AI Copilot flags delivery in SAP LIKP with status 'HELD_CONSIGNEE_DEFAULT', nullifies SLA clock, and issues $150.00 invoice debit to clinic."},
            {"trigger": "Clinic disputes refusal charge", "action": "Telematics GPS geofence validation and driver timestamp audited; claim resolved in 48 hours."}
        ]
    },

    # =========================================================================
    # CATEGORY 2: QUALITY ASSURANCE & PACKAGING POLICY SOPS
    # Target Directory: Packaging Policy Docs/
    # =========================================================================
    {
        "category": "Packaging Policy Docs",
        "file_stem": "Cold Chain Active Refrigeration (2C to 8C) & Thermal Breach Quarantine SOP",
        "title": "Cold Chain Active Refrigeration (2C to 8C) & Thermal Breach Quarantine SOP",
        "header": {
            "Document ID": "QA-SOP-2026-016-COLD",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Global Quality Assurance, Life Sciences Regulatory Compliance, & Cold Chain Logistics",
            "Material Classification": "Temperature-Sensitive Veterinary Biologics & Pharmaceuticals (MARA-MATKL = VET_MED)",
            "Target SAP Tables / Fields": "MARA (MATNR, MATKL, TEMPB), LIPS (WERKS, LGORT), LIKP (LIFSK, WBSTK)"
        },
        "purpose": (
            "Establishes strict quality assurance mandates, continuous IoT data logger monitoring, and quarantine procedures "
            "for veterinary biologicals, injectable therapeutics, vaccines, and insulin requiring continuous refrigeration between "
            "2.0°C and 8.0°C (35.6°F to 46.4°F). Preserves efficacy and patient safety against thermal degradation."
        ),
        "definitions": [
            {"term": "Active Cold Chain Cargo", "definition": "Veterinary medical substances marked with SAP temperature condition code '02' requiring active mechanical refrigeration."},
            {"term": "Thermal Excursion", "definition": "Any temperature reading exceeding 8.0°C or falling below 2.0°C recorded by NIST-calibrated continuous digital IoT data loggers."},
            {"term": "SAP Quarantine Delivery Block 01", "definition": "A systematic lock placed on SAP LIKP delivery documents preventing commercial release or financial invoice billing until QA audit approval."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Continuous Active Monitoring", "text": "Reefer trailers and thermal containers must carry calibrated IoT cellular temperature sensors transmitting readings every fifteen (15) minutes to the AI Copilot telematics platform."},
            {"num": "4.2", "title": "Critical Thermal Breach Definition", "text": "Any cumulative exposure above 8.0°C for greater than sixty (60) minutes, or any single transient spike above 15.0°C, constitutes an irreversible Critical Thermal Breach."},
            {"num": "4.3", "title": "Freeze Damage Zero-Tolerance", "text": "Because freezing irreversibly denatures biological proteins, any temperature record falling below 0.0°C for more than fifteen (15) minutes requires immediate 100% batch condemnation."},
            {"num": "4.4", "title": "Mandatory Quarantine Diversion", "text": "Upon thermal breach detection, the carrier must immediately halt transit and divert cargo to the nearest certified cold storage depot."}
        ],
        "financial": [
            {"item": "Carrier Liability for Spoiled Cargo", "detail": "Carrier liable for 100% of the invoice manufacturing cost of all condemned freight (MARA-NETPR * LIPS-LFIMG)."},
            {"item": "Replacement Freight Expedited Cost", "detail": "Carrier at fault must fund priority air replacement freight up to $1,000.00 USD per clinical order."},
            {"item": "Certified Disposal Fee", "detail": "Hazardous biological disposal surcharge of $350.00 USD assessed against carrier if reefer unit mechanical failure caused excursion."}
        ],
        "exceptions": [
            {"condition": "Pre-Cooling Calibration Grace Period", "detail": "Transient 15-minute thermal spikes during trailer door opening at loading dock are permissible if core probe remains < 6.0°C."},
            {"condition": "Catastrophic Sensor Malfunction", "detail": "If backup analog chemical phase-change indicator confirms no thaw, electronic false alarms may be overturned by QA Director."}
        ],
        "enforcement": [
            {"trigger": "IoT sensor reports > 8.0°C for 60 minutes", "action": "AI Copilot instantly writes Delivery Block '01' into SAP LIKP, notifies consignee clinic of replacement shipment, and files carrier claim."},
            {"trigger": "Carrier driver attempts delivery of breached lot", "action": "Consignee scanner rejects delivery barcode; goods diverted to QA quarantine storage."}
        ]
    },

    {
        "category": "Packaging Policy Docs",
        "file_stem": "Controlled Room Temperature (CRT 15C to 25C) Excursion Protocol",
        "title": "Controlled Room Temperature (CRT 15C to 25C) Excursion Protocol",
        "header": {
            "Document ID": "QA-SOP-2026-017-CRT",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Quality Assurance, Regulatory Affairs, & Domestic Distribution",
            "Material Classification": "Liquid Therapeutic Diets, Oral Suspensions, & Topical Ointments (MARA-MATKL = VET_DIET, VET_MED)",
            "Target SAP Tables / Fields": "MARA (MATKL, SHELF_LIFE_MOS), LIPS (WERKS, LFIMG), LIKP (VBELN)"
        },
        "purpose": (
            "Defines acceptable transit boundaries, Mean Kinetic Temperature (MKT) calculations, and disposition protocols "
            "for clinical nutrition liquids, suspensions, and veterinary pharmaceuticals labeled for Controlled Room Temperature (15°C to 25°C / 59°F to 77°F). "
            "Mitigates emulsion separation, active ingredient degradation, and packaging delamination during extreme seasonal ambient transit."
        ),
        "definitions": [
            {"term": "Controlled Room Temperature (CRT)", "definition": "A maintained environmental state between 15.0°C and 25.0°C with transient excursions permitted up to 30.0°C based on stability data."},
            {"term": "Mean Kinetic Temperature (MKT)", "definition": "The single calculated isothermal temperature that corresponds to the kinetic effects of a temperature sequence over time per USP <1160>."},
            {"term": "Accelerated Shelf-Life Degradation", "definition": "The exponential reduction in remaining shelf life (MARA-SHELF_LIFE_MOS) caused by thermal stress."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Permissible Short-Term Excursions", "text": "Freight may experience transient thermal exposure between 25.1°C and 30.0°C for a cumulative period not to exceed twenty-four (24.0) hours without compromising stability."},
            {"num": "4.2", "title": "Extreme Heat Violation Threshold", "text": "Any thermal record exceeding 40.0°C (104.0°F) for greater than two (2.0) continuous hours constitutes a severe product adulteration event, voiding product warranty."},
            {"num": "4.3", "title": "Refrigeration Requirement in Summer Lanes", "text": "Between May 15 and September 15, all freight traversing Desert Southwest corridors (Phoenix, Las Vegas, Dallas) must utilize climate-controlled dry vans set at 20°C."}
        ],
        "financial": [
            {"item": "Adulterated Cargo Replacement", "detail": "Full replacement value charged to carrier if failure to use protective climate controls is proven."},
            {"item": "Accelerated Aging Discount", "detail": "If product experienced 30°C–39°C excursion for < 24h, QA may approve release subject to a 15% markdown absorbed by carrier."},
            {"item": "QA Laboratory Re-Assay Charge", "detail": "$450.00 USD lab testing fee if specialized chemical assay required to confirm product viability."}
        ],
        "exceptions": [
            {"condition": "Documented Thermal Protective Pallet Blankets", "detail": "Shipments utilizing validated thermal insulation blankets (R-value >= 4.0) are granted extended 48-hour excursion tolerance."},
            {"condition": "Non-Nutritive Ancillary Supplies", "detail": "Surgical instruments and non-perishable consumables co-loaded are exempt from CRT disposition."}
        ],
        "enforcement": [
            {"trigger": "Corridor telemetry indicates ambient > 40°C on uninsulated dry van", "action": "Copilot generates QA Warning, alerts consignee intake team to perform physical inspection upon arrival."},
            {"trigger": "MKT calculation exceeds 28.0°C across transit duration", "action": "Automatic SAP lot quarantine block posted; sample requisitioned for stability review."}
        ]
    },

    {
        "category": "Packaging Policy Docs",
        "file_stem": "Sterile Medical Device & Hermetic Surgical Packaging Integrity Protocol",
        "title": "Sterile Medical Device & Hermetic Surgical Packaging Integrity Protocol",
        "header": {
            "Document ID": "QA-SOP-2026-018-SURG",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Surgical Device Quality Assurance & Medical Device Regulatory Affairs",
            "Material Classification": "Sterile Veterinary Surgical Supplies, Suture Packs, & Implants (MARA-MATKL = SURGICAL)",
            "Target SAP Tables / Fields": "MARA (MATNR, MATKL = 'SURGICAL'), LIPS (LFIMG, VRKME), LIKP (VBELN)"
        },
        "purpose": (
            "Establishes physical packaging standards, transit vibration thresholds, and zero-tolerance breach protocols "
            "for sterile medical devices, veterinary surgical suture packs, orthopedic implants, and sterile procedure sets. "
            "Ensures strict compliance with ISO 11607 packaging standards to eliminate post-operative infection risks in animal patients."
        ),
        "definitions": [
            {"term": "Hermetic Sterile Barrier", "definition": "The primary sealed pouch or thermoformed blister pack engineered to prevent microbial ingress under ambient atmospheric pressure."},
            {"term": "Micro-Puncture Defect", "definition": "Any breach, pinhole, tear, or channel seal separation in the sterile barrier exceeding 50 microns."},
            {"term": "Crush Compromise", "definition": "Deformation of outer corrugated packaging exceeding 20% vertical compression that compromises secondary sterile barrier integrity."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Zero-Tolerance Sterility Mandate", "text": "Because compromised packaging can lead to fatal systemic animal sepsis, any physical tear, puncture, moisture absorption, or seal separation results in mandatory 100% batch rejection."},
            {"num": "4.2", "title": "Top-Load Stacking Prohibition", "text": "Cartons labeled 'SURGICAL / STERILE - DO NOT DOUBLE STACK' must be placed strictly on top tier of pallets. Double-stacking pallet freight atop sterile goods is a contractual violation."},
            {"num": "4.3", "title": "Moisture & Condensation Barrier", "text": "Sterile packaging must remain bone dry. Water-stained cartons, condensation droplets, or humidity exposure exceeding 80% RH require immediate quarantine."}
        ],
        "financial": [
            {"item": "Full Batch Rejection Liability", "detail": "Carrier liable for 100% invoice value of all cartons displaying crush or moisture damage (MARA-NETPR * quantity)."},
            {"item": "Emergency Surgical Courier Expedited Fee", "detail": "Up to $750.00 USD dedicated hotshot courier cost to deliver replacement sutures to scheduled surgeries."},
            {"item": "Sterile Scrappage Assessment", "detail": "Carrier pays $200.00 USD certified medical waste disposal and destruction processing fee."}
        ],
        "exceptions": [
            {"condition": "Secondary Carton Cosmetic Blemish", "detail": "Superficial scuffing or tape peeling on tertiary outer shipper cartons is acceptable provided primary pouch passes dye-penetration inspection."},
            {"condition": "Pre-Shipment Warehouse Exception", "detail": "If warehouse WMS inspection photos prove damage existed prior to carrier tender, carrier is fully exonerated."}
        ],
        "enforcement": [
            {"trigger": "Consignee receiving dock logs 'Damp or Crushed Surgical Box'", "action": "Copilot immediately issues replacement delivery order in SAP, applies full chargeback to delivering carrier."},
            {"trigger": "Carrier driver photographs damaged outer crate", "action": "Immediate SAP credit memo generated to clinic within 1 hour."}
        ]
    },

    {
        "category": "Packaging Policy Docs",
        "file_stem": "Hypoallergenic Diet Cross-Contamination & Allergen Isolation SOP",
        "title": "Hypoallergenic Diet Cross-Contamination & Allergen Isolation SOP",
        "header": {
            "Document ID": "QA-SOP-2026-019-HYPO",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Clinical Nutrition Quality Assurance & Allergen Control Operations",
            "Material Classification": "Hydrolyzed Protein Diets & Elimination Trial Formulations (MARA-MATKL = VET_DIET)",
            "Target SAP Tables / Fields": "MARA (MATNR, MAKTX, SPECIALTY_DIET_FLAG), LIPS (WERKS, LGORT), LIKP (VBELN)"
        },
        "purpose": (
            "Establishes operational and transportation safeguards to prevent environmental cross-contamination of hypoallergenic, "
            "hydrolyzed protein, and novel-antigen veterinary clinical diets. Patients consuming these formulations suffer severe "
            "anaphylactoid, dermatological, and gastrointestinal reactions if trace poultry, beef, or dairy proteins contaminate cargo."
        ),
        "definitions": [
            {"term": "Hydrolyzed Protein Diet", "definition": "Specialized prescription nutrition where proteins are enzymatically broken down below 3,000 Daltons to prevent immune recognition by sensitized canine/feline patients."},
            {"term": "Cross-Contact Contamination", "definition": "The unintentional transfer of common dietary protein dust, animal dander, or feed residues from adjacent cargo into hypoallergenic packaging."},
            {"term": "Poly-Barrier Shrink Overwrap", "definition": "A continuous, heat-sealed 80-gauge linear low-density polyethylene wrap encasing the entire pallet."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Mandatory Pallet Barrier Wrapping", "text": "All hypoallergenic clinical diets must be encapsulated in full 360-degree poly-barrier shrink film at the manufacturing plant before warehouse staging."},
            {"num": "4.2", "title": "Co-Loading Prohibitions", "text": "Hydrolyzed protein pallets must NEVER be co-loaded in the same trailer compartment with open, torn, or bulk unsealed agricultural grains, meat meal, or standard livestock feeds."},
            {"num": "4.3", "title": "Torn Packaging Quarantine", "text": "Any punctured or torn bag of hypoallergenic diet cannot be taped, resealed, or delivered to clinical customers. It must be immediately condemned."}
        ],
        "financial": [
            {"item": "Contaminated Lot Replacement Cost", "detail": "Carrier or facility at fault pays 100% replacement cost plus expedited replacement freight."},
            {"item": "Veterinary Patient Clinical Trial Indemnity", "detail": "Up to $1,000.00 USD reimbursement for diagnostic allergy re-testing if contaminated food resets patient clinical trial."},
            {"item": "Restocking Surcharge", "detail": "Zero restocking fees for clinics returning suspected cross-contact product."}
        ],
        "exceptions": [
            {"condition": "Factory Sealed Metal Cans", "detail": "Hermetically sealed wet canned hypoallergenic formulations are exempt from ambient dust cross-contact restrictions."},
            {"condition": "Dedicated Clean Dry Van Certification", "detail": "Trailers presenting certified wash-out documentation prior to loading are exempt from secondary pallet shrouding."}
        ],
        "enforcement": [
            {"trigger": "Dock intake flags torn hypoallergenic bag", "action": "Copilot immediately cancels billing line item in SAP VBRP, triggers scrap order in SAP MM, and generates hotshot reshipment."},
            {"trigger": "Trailer inspection reports livestock feed co-loading", "action": "Entire shipment placed on SAP QA Hold '01' pending ELISA protein residue swab testing."}
        ]
    },

    {
        "category": "Packaging Policy Docs",
        "file_stem": "Distressed Freight Salvage, Non-Profit Donation & Regulated Incineration SOP",
        "title": "Distressed Freight Salvage, Non-Profit Donation & Regulated Incineration SOP",
        "header": {
            "Document ID": "QA-SOP-2026-020-DISP",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Sustainability, Legal Compliance, Quality Assurance, & Inventory Accounting",
            "Material Classification": "All Distressed, Refused, or Quarantined Veterinary Nutrition & Pharmaceuticals",
            "Target SAP Tables / Fields": "MARA (MATKL, SHELF_LIFE_MOS), LIPS (LFIMG), BKPF (BELNR, BUKRS), BSEG (WRBTR)"
        },
        "purpose": (
            "Governs the legally compliant, ethically responsible, and tax-optimized disposition of distressed, delayed, "
            "or cosmetically damaged veterinary freight. Establishes a rigorous decision hierarchy separating safe non-profit "
            "animal rescue shelter donations from mandatory high-temperature environmental incineration for hazardous pharmaceuticals."
        ),
        "definitions": [
            {"term": "Distressed Freight", "definition": "Cargo refused by consignees, damaged in transit, cosmetically flawed, or nearing minimum shelf-life thresholds (MARA-SHELF_LIFE_MOS < 3 months)."},
            {"term": "Non-Profit Rescue Donation", "definition": "Transfer of sound, wholesome nutrition with cosmetic carton damage to verified 501(c)(3) animal shelters per IRS Code Section 170(e)(3)."},
            {"term": "Regulated Incineration", "definition": "Mandatory high-temperature destruction (>1000°C) of pharmaceuticals, surgical items, or biologically adulterated goods at a certified EPA/state waste facility."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Three-Tier Disposition Hierarchy", "text": "All distressed inventory must be classified into: Tier A (Commercial Restock), Tier B (Shelter Donation), or Tier C (Regulated Destruction)."},
            {"num": "4.2", "title": "Shelter Donation Criteria", "text": "Dry pet nutrition (PET_DRY) and intact canned diets with superficial exterior denting or carton crush, with at least 45 days remaining shelf life, must be donated to non-profit animal rescue partners."},
            {"num": "4.3", "title": "Mandatory Destruction Criteria", "text": "All veterinary medications (VET_MED), opened prescription diets, sterile surgical sutures (SURGICAL), and thermally spoiled biologics are strictly barred from donation and must undergo certified incineration."},
            {"num": "4.4", "title": "Certificate of Destruction (CoD) Mandate", "text": "A certified CoD signed by an EPA-licensed incinerator must be uploaded to SAP MM attachment directory within fourteen (14) days of scrap authorization."}
        ],
        "financial": [
            {"item": "Corporate Donation Tax Valuation", "detail": "Eligible for federal enhanced tax deduction under IRC 170(e)(3) equal to cost of goods plus one-half the mark-up value."},
            {"item": "Destruction Processing Cost Allocation", "detail": "Incineration fee ($0.45/kg + $150 processing) charged to carrier if transit negligence caused condemnation."},
            {"item": "Inventory Write-Off Accounting", "detail": "Automated posting in SAP FI/CO credit inventory account (G/L 130000) and debit salvage loss (G/L 680000)."}
        ],
        "exceptions": [
            {"condition": "Manufacturer Product Recall", "detail": "In the event of an FDA/USDA regulatory recall, all donation rights are suspended; 100% of lots must be quarantined for regulatory inspection."},
            {"condition": "Minor Secondary Carton Scuff", "detail": "If primary inner pouches are 100% pristine and > 6 months shelf life remains, goods may be repackaged for secondary distribution."}
        ],
        "enforcement": [
            {"trigger": "QA flags shipment as 'CONDEMNED_UNRECOVERABLE'", "action": "Copilot generates SAP Scrap Order (Movement Type 551), dispatches hazardous waste manifest to carrier, and tracks CoD completion."},
            {"trigger": "Donation transfer approved by QA Lead", "action": "SAP movement type 555 posted, Bill of Lading issued to verified 501(c)(3) animal sanctuary with tax receipt."}
        ]
    },

    # =========================================================================
    # CATEGORY 3: CARRIER CONTRACTS & VENDOR LOGISTICS AGREEMENTS
    # Target Directory: Vendor Contract Docs/
    # =========================================================================
    {
        "category": "Vendor Contract Docs",
        "file_stem": "Motor Carrier Dock Detention & Free-Time Demurrage Policy",
        "title": "Motor Carrier Dock Detention & Free-Time Demurrage Policy",
        "header": {
            "Document ID": "MVA-ADD-2026-016-DET",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Transportation Management, Freight Audit, & Plant Warehouse Operations",
            "Contractual Scope": "All Contracted Full Truckload (FTL) and Less-Than-Truckload (LTL) Motor Carriers",
            "Target SAP Tables / Fields": "LFA1 (LIFNR), VTTK (TKNUM, DPABF, DPTEN), VTTP (VBELN)"
        },
        "purpose": (
            "Standardizes the commercial rules, electronic logging device (ELD) timestamp verifications, and financial rates "
            "governing driver and equipment detention at manufacturing plants (PL01, PL02, PL03) and destination clinic receiving docks. "
            "Eliminates invoice friction, enforces appointment discipline, and provides fair compensation for loading delays."
        ),
        "definitions": [
            {"term": "Free Time Allowance", "definition": "A standard period of two (2.0) hours (120 minutes) granted to the shipper or consignee for loading or unloading without demurrage surcharge."},
            {"term": "Detention Demurrage", "definition": "An hourly compensation rate paid to the carrier for equipment and driver idle time exceeding the contractual Free Time Allowance."},
            {"term": "Geofenced Telematics Verification", "definition": "Automated confirmation of tractor arrival, dock door coupling, and facility departure recorded via cellular GPS geofencing."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Punctuality Condition Precedent", "text": "To qualify for detention compensation, the Carrier must arrive within fifteen (±15) minutes of the scheduled dock appointment time recorded in the appointment management system."},
            {"num": "4.2", "title": "Free Time Commencement", "text": "Free time begins precisely when the driver checks in with shipping/receiving personnel, or upon confirmed geofenced dock door coupling, whichever is verified electronically."},
            {"num": "4.3", "title": "Shipper vs Consignee Detention Responsibility", "text": "Detention incurred at plants (PL01, PL02, PL03) is reimbursed directly by the enterprise. Detention incurred at customer docks due to clinic default is back-charged to the consignee."},
            {"num": "4.4", "title": "Maximum Daily Cap", "text": "Standard detention is capped at six (6.0) billable hours per 24-hour cycle, after which the driver is entitled to layover compensation."}
        ],
        "financial": [
            {"item": "Hourly Detention Rate", "detail": "$85.00 USD per hour, billed in fifteen (15) minute increments ($21.25/quarter-hour) after 120 minutes free time."},
            {"item": "Full Layover Day Rate", "detail": "$450.00 USD flat layover rate if shipper/consignee holds tractor overnight (> 8 hours past appointment)."},
            {"item": "Driver Detention Claim Window", "detail": "Detention claims must be submitted electronically via EDI 210 with ELD logs within fourteen (14) calendar days."}
        ],
        "exceptions": [
            {"condition": "Late Driver Arrival", "detail": "If driver arrives > 30 minutes late for appointment, driver is placed on work-in queue; all detention rights are forfeited for that facility."},
            {"condition": "Carrier Packaging Defect", "detail": "If unloading is halted due to leaking, fallen, or improperly secured pallets caused by carrier transit negligence, detention is void."}
        ],
        "enforcement": [
            {"trigger": "ELD verifies tractor on dock > 120 minutes with on-time arrival", "action": "Copilot automatically approves detention accessorial voucher and creates payable item in SAP FI for carrier payment run."},
            {"trigger": "Carrier submits manual detention invoice without telematics proof", "action": "Automatic system rejection; carrier notified to provide ELD GPS trace."}
        ]
    },

    {
        "category": "Vendor Contract Docs",
        "file_stem": "Emergency Air Freight Expedited Cost Allocation & Recovery Agreement",
        "title": "Emergency Air Freight Expedited Cost Allocation & Recovery Agreement",
        "header": {
            "Document ID": "MVA-ADD-2026-017-AIR",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Enterprise Freight Operations, Carrier Contracting, & Risk Management",
            "Contractual Scope": "All Commercial Linehaul Carriers & Expedited Air Logistics Providers",
            "Target SAP Tables / Fields": "LFA1 (LIFNR, VSART), VBAK (AUART, NETWR), LIKP (VBELN)"
        },
        "purpose": (
            "Establishes the governance parameters, authorization gates, and legal liability partitioning for upgrading delayed "
            "or threatened veterinary shipments from ground transportation (FTL/LTL) to priority commercial air freight (FedEx Priority, "
            "Delta Cargo, Southwest Cargo). Guarantees rapid patient stock-out mitigation while strictly protecting operating margins."
        ),
        "definitions": [
            {"term": "Expedited Air Mode Shift", "definition": "The emergency transfer of consigned freight to commercial air cargo to bypass road corridor blockades, severe weather, or carrier transit failures."},
            {"term": "Expedited Cost Differential", "definition": "The financial difference between the premium air freight invoice and the baseline contractual ground transport rate."},
            {"term": "Emergency Policy Cap", "definition": "A strict contractual expenditure ceiling of $1,000.00 USD per critical veterinary clinical order."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Carrier-At-Fault Liability Allocation", "text": "When an air freight upgrade is necessitated by carrier mechanical breakdown, missed origin tender, or unexcused driver delay, the carrier is legally liable for 100% of the air differential up to the $1,000.00 cap."},
            {"num": "4.2", "title": "Shipper-Caused Delay Allocation", "text": "When air upgrades stem from warehouse stock-outs or plant loading delays, the enterprise absorbs 100% of the differential."},
            {"num": "4.3", "title": "Verified Force Majeure Cost Sharing", "text": "When air freight is deployed to navigate certified meteorological disasters (Level 4/5) to save patient lives, the cost is split 50/50 between carrier and enterprise emergency freight reserve."},
            {"num": "4.4", "title": "Authorization Threshold", "text": "Autonomous AI authorization is limited to $500.00 USD. Expedited air upgrades between $500.01 and $1,000.00 require one-click Supply Chain Operations Manager digital approval."}
        ],
        "financial": [
            {"item": "Emergency Air Freight Cap", "detail": "$1,000.00 USD maximum recovery per sales order (VBAK-VBELN)."},
            {"item": "Carrier Chargeback Mechanism", "detail": "Direct automatic deduction from outstanding freight payables via SAP FI/CO credit memo within 5 business days."},
            {"item": "Air Bill Audit Fee", "detail": "10% administrative audit fee credited to enterprise if carrier disputes verified breakdown liability."}
        ],
        "exceptions": [
            {"condition": "FAA Ground Stop / Air Traffic Embargo", "detail": "If commercial air cargo is grounded by federal aviation safety mandates, liability for air upgrade failure is fully excused."},
            {"condition": "Non-Perishable Commercial Freight", "detail": "Air freight upgrades are strictly barred for dry pet nutrition (PET_DRY) unless pre-authorized in writing by Customer Vice President."}
        ],
        "enforcement": [
            {"trigger": "QualityMitigation agent identifies specialty diet stock-out risk > 24 hours", "action": "Copilot pings air freight broker API, books priority space under $1,000 cap, and records liability code in SAP LIKP."},
            {"trigger": "Air differential invoice received", "action": "System matches air bill to original ground shipment VBELN and executes automated chargeback to at-fault carrier."}
        ]
    },

    {
        "category": "Vendor Contract Docs",
        "file_stem": "Driver Hours of Service (HOS) Compliance & Breakdown Relief Mandate",
        "title": "Driver Hours of Service (HOS) Compliance & Breakdown Relief Mandate",
        "header": {
            "Document ID": "MVA-ADD-2026-018-HOS",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Transportation Safety, Carrier Compliance, & Fleet Operations",
            "Contractual Scope": "All Motor Carriers Operating Under Master Vendor Agreements (MVAs)",
            "Target SAP Tables / Fields": "LFA1 (LIFNR), VTTK (TKNUM, DPABF, DPTEN), LIKP (VBELN)"
        },
        "purpose": (
            "Enforces strict compliance with Federal Motor Carrier Safety Administration (FMCSA) 49 CFR Part 395 Hours of Service "
            "regulations while prohibiting carriers from improperly invoking driver duty exhaustion as an excuse for unmitigated delivery delays. "
            "Mandates rapid tractor-trailer breakdown recovery protocols to safeguard perishable clinical freight."
        ),
        "definitions": [
            {"term": "FMCSA HOS Limits", "definition": "Federal limits restricting property-carrying commercial drivers to 11 hours driving time following 10 consecutive hours off duty, within a 14-hour duty window."},
            {"term": "Catastrophic Tractor Breakdown", "definition": "Mechanical, electrical, or tire failure rendering the commercial power unit incapable of safe highway operation."},
            {"term": "Relief Power Unit Mandate", "definition": "Contractual obligation to dispatch a replacement tractor or team driver within four (4.0) hours of verified roadside breakdown."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Pre-Dispatch HOS Feasibility", "text": "Carrier certifies that upon accepting tender, assigned drivers have sufficient legal duty hours available under FMCSA rules to complete the transit run within Promised Delivery Date bounds."},
            {"num": "4.2", "title": "HOS Invalidation as Force Majeure", "text": "Normal driver clock exhaustion is an operational scheduling failure, NOT a Force Majeure event. Carriers are strictly barred from claiming Act of God immunity for driver hours violations."},
            {"num": "4.3", "title": "Four-Hour Breakdown Relief Window", "text": "In the event of a highway breakdown, carrier must dispatch a secondary recovery tractor or certified roadside mobile mechanic within four (4.0) hours of the stoppage."},
            {"num": "4.4", "title": "Refrigerated Cargo Protection During Breakdown", "text": "Driver must verify that trailer refrigeration auxiliary power unit (APU) remains continuously fueled and operational throughout the mechanical breakdown."}
        ],
        "financial": [
            {"item": "Failure to Dispatch Relief Tractor", "detail": "$300.00 USD non-mitigation penalty assessed if relief power unit is not in transit within 4 hours of breakdown."},
            {"item": "Standard Delay Penalties Maintained", "detail": "Full daily SLA penalties ($500/$300/$200) continue to accrue without interruption during mechanical breakdowns."},
            {"item": "Thermal Loss Indemnity", "detail": "100% product replacement liability if driver neglects reefer APU during breakdown leading to cargo spoilage."}
        ],
        "exceptions": [
            {"condition": "Unforeseeable Multi-Vehicle Catastrophic Highway Closure", "detail": "Interstate highway blockages verified by State Highway Patrol that trap the truck in gridlock constitute valid temporary delay relief."},
            {"condition": "Severe Driver Medical Emergency", "detail": "Documented acute driver hospitalization excuses delay penalty for a maximum 12-hour grace window while carrier routes replacement."}
        ],
        "enforcement": [
            {"trigger": "Telematics indicates zero velocity > 2 hours outside rest stop", "action": "Copilot pings carrier dispatch via API demanding breakdown status and relief ETA."},
            {"trigger": "No relief tractor dispatched after 4 hours", "action": "Autonomous $300 penalty logged; Copilot authorizes third-party heavy recovery tow at carrier expense."}
        ]
    },

    {
        "category": "Vendor Contract Docs",
        "file_stem": "Drop-Trailer Management & Unattended Yard Equipment Agreement",
        "title": "Drop-Trailer Management & Unattended Yard Equipment Agreement",
        "header": {
            "Document ID": "MVA-ADD-2026-019-YARD",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Warehouse Logistics, Yard Management, & Asset Protection",
            "Contractual Scope": "Contracted Dedicated and Fleet Carriers Providing Drop-Trailer Capacity",
            "Target SAP Tables / Fields": "LFA1 (LIFNR), LIKP (VSTEL, TRAID), VTTK (TKNUM)"
        },
        "purpose": (
            "Governs equipment custody, pre-loading staging, kingpin security, and per diem liabilities for carrier drop-trailers "
            "stationed at enterprise distribution plants in Atlanta (PL01), Chicago (PL02), and Dallas (PL03). Enhances warehouse "
            "fulfillment throughput while standardizing risk of loss for staged freight."
        ),
        "definitions": [
            {"term": "Drop-Trailer Staging", "definition": "The placement of an empty carrier trailer at plant shipping yard to permit pre-loading of scheduled sales orders by warehouse personnel prior to driver arrival."},
            {"term": "Free Drop Staging Time", "definition": "A contractual forty-eight (48) hour free period for trailers to be loaded and dispatched without yard storage fees."},
            {"term": "Pre-Loaded Freight Custody", "definition": "The precise legal transfer of cargo custody upon completion of loading, application of high-security bolt seal, and electronic Bill of Lading generation."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Trailer Cleanliness & Roadworthiness", "text": "Carrier drop trailers must be delivered clean, dry, odor-free, structurally sound, and pre-swept. Trailers with chemical residues or insect evidence will be rejected with $150 rejection fee."},
            {"num": "4.2", "title": "Reefer Pre-Cooling & Fuel Mandate", "text": "Refrigerated drop trailers must arrive with at least three-quarters (3/4) full diesel tank and pre-cooled to designated setpoint (20°C CRT or 4°C Cold Chain)."},
            {"num": "4.3", "title": "High-Security Bolt Seal Protocol", "text": "Upon loading completion, enterprise staff will affix an ISO 17712 certified numbered bolt seal. Carrier assumes full custody of freight upon driver hook-up and seal verification."},
            {"num": "4.4", "title": "Timely Dispatch Obligation", "text": "Once notified that pre-loading is complete, carrier must dispatch tractor and pull trailer within twenty-four (24.0) hours."}
        ],
        "financial": [
            {"item": "Trailer Rejection Surcharge", "detail": "$150.00 USD assessed against carrier if dropped equipment fails cleanliness or refrigeration mechanical audit."},
            {"item": "Yard Demurrage Per Diem", "detail": "$45.00 USD per day assessed against carrier for loaded trailers sitting in yard > 24 hours past pickup window."},
            {"item": "Missing Bolt Seal Penalty", "detail": "$500.00 USD penalty plus mandatory complete pallet re-inspection if carrier driver breaks seal without authorization."}
        ],
        "exceptions": [
            {"condition": "Plant Fulfillment Loading Delay", "detail": "If warehouse delays loading beyond scheduled staging schedule, carrier is excused from pickup window requirements."},
            {"condition": "Yard Closure Due to Severe Weather", "detail": "Blizzard or tornadic plant closures suspend all drop trailer per diem and pull mandates."}
        ],
        "enforcement": [
            {"trigger": "Trailer loaded and sealed in YMS", "action": "Electronic pickup tender dispatched via EDI 204 to carrier dispatch; 24h pickup countdown commences."},
            {"trigger": "Trailer remains in yard > 24 hours post-loading", "action": "Copilot logs daily $45 per diem and flags dispatch for carrier escalation."}
        ]
    },

    {
        "category": "Vendor Contract Docs",
        "file_stem": "Carrier Chargeback Dispute Resolution & Audit Appeal Procedure",
        "title": "Carrier Chargeback Dispute Resolution & Audit Appeal Procedure",
        "header": {
            "Document ID": "MVA-ADD-2026-020-DISP",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Freight Audit, Carrier Relations, Legal Counsel, & Accounts Payable",
            "Contractual Scope": "All Commercial Freight Carriers Subject to Autonomous AI Chargebacks",
            "Target SAP Tables / Fields": "LFA1 (LIFNR), BKPF (BELNR, AWKEY), BSEG (WRBTR, SHKZG), VTTK (TKNUM)"
        },
        "purpose": (
            "Establishes a transparent, legally enforceable, and rapid dispute resolution procedure providing motor carriers "
            "due process to challenge automated AI-generated delay penalties, blind tracking fees, or detention deductions. "
            "Guarantees fair adjudication, electronic evidence submission, and prompt refunding of overturned deductions."
        ),
        "definitions": [
            {"term": "AI Freight Chargeback", "definition": "An automated deduction executed in SAP FI/CO by the AI Logistics Copilot against carrier payable invoices for documented transit failures."},
            {"term": "Dispute Filing Window", "definition": "A strict thirty (30) calendar day window from the date of SAP deduction remittance advice within which carrier must submit electronic rebuttal."},
            {"term": "Certified Telematics Evidence Dossier", "definition": "Electronic submission of unedited ELD GPS traces, engine telematics, official police reports, or DOT road closure notices."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Right to Electronic Appeal", "text": "Carriers maintain the contractual right to challenge any autonomous penalty or chargeback by filing an appeal through the Carrier Web Portal within thirty (30) calendar days."},
            {"num": "4.2", "title": "Mandatory Evidentiary Standard", "text": "Appeals must be accompanied by raw, unedited telematics data (ELD logs, GPS pings at 15-min intervals) demonstrating driver diligence, unannounced road blockage, or consignee default."},
            {"num": "4.3", "title": "Ten-Day Adjudication Mandate", "text": "The enterprise Freight Audit Committee, supported by the AI Copilot Audit Panel, must adjudicate and render a binding decision within ten (10) business days of appeal submission."},
            {"num": "4.4", "title": "Immediate Credit Execution", "text": "If an appeal is upheld, the full disputed amount will be credited back to the carrier's account in the next weekly SAP FI payment run without interest or penalty."}
        ],
        "financial": [
            {"item": "Dispute Appeal Filing Fee", "detail": "$0.00 USD (No cost to file legitimate contractual disputes)."},
            {"item": "Frivolous Dispute Administrative Fee", "detail": "$100.00 USD assessed if carrier submits repeated disputes without supporting telematics evidence."},
            {"item": "Prompt Refund Guarantee", "detail": "Overturned chargebacks paid within seven (7) business days via direct electronic funds transfer (EFT)."}
        ],
        "exceptions": [
            {"condition": "Untimely Dispute Submission", "detail": "Disputes submitted past thirty (30) calendar days are barred by contractual limitation; deduction becomes final."},
            {"condition": "Carrier Concealment of Telematics", "detail": "Failure to provide requested ELD logs within 5 business days of request results in summary dismissal of appeal."}
        ],
        "enforcement": [
            {"trigger": "Carrier submits dispute via portal with ELD trace", "action": "Copilot ingest dispute payload, compares against historical weather and road speed databases, and prepares recommendation for Auditor."},
            {"trigger": "Dispute approved by Freight Audit Lead", "action": "Autonomous posting of SAP FI reversal credit memo (Document Type 'KG') crediting carrier vendor balance."}
        ]
    },

    # =========================================================================
    # CATEGORY 4: REGIONAL CORRIDOR WEATHER & HAZARD PROTOCOLS
    # Target Directory: Regional Hazard Policies/
    # =========================================================================
    {
        "category": "Regional Hazard Policies",
        "file_stem": "Midwest Winter Storm & Snowbelt Corridor (I-80  I-90) Logistics Protocol",
        "title": "Midwest Winter Storm & Snowbelt Corridor (I-80 / I-90) Logistics Protocol",
        "header": {
            "Document ID": "WTH-SOP-2026-001-MIDW",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Transportation Risk Operations, Regional Logistics Hubs, & Winter Safety",
            "Geographic Region": "Midwest Freight Corridor (Chicago PL02 servicing IL, IN, MI, WI, MN, IA, OH)",
            "Target SAP Tables / Fields": "VTTK (ROUTE, TPLST), LIKP (WERKS = 'PL02', VSTEL = 'SH02'), VBAK (KUNNR)"
        },
        "purpose": (
            "Establishes operational triggers, heated equipment requirements, route diversion criteria, and legal liability "
            "rules for commercial veterinary freight operating across the Midwest winter snowbelt (I-80, I-90, I-94 corridors). "
            "Protects driver safety, prevents freezing of therapeutic diets, and defines winter weather Force Majeure boundaries."
        ),
        "definitions": [
            {"term": "Midwest Winter Storm Warning", "definition": "Official National Weather Service (NWS) alert forecasting snowfall > 15 cm (6 inches) in 12 hours, sustained winds > 45 km/h, or freezing rain."},
            {"term": "Protect From Freezing (PFF) Mandate", "definition": "Requirement to utilize active heated dry vans or thermal insulated blankets for liquid and canned veterinary therapeutic diets."},
            {"term": "Intermodal Rail Bypass Trigger", "definition": "Preemptive diversion of linehaul freight to BNSF/Union Pacific intermodal rail when highway interstate closures exceed 24 hours."}
        ],
        "clauses": [
            {"num": "4.1", "title": "PFF Heated Equipment Requirement", "text": "Between November 1 and March 31, all shipments originating from Chicago PL02 containing wet diets (VET_WET) or pharmaceuticals must be tendered to carriers providing guaranteed heated van service maintaining cargo > 5.0°C."},
            {"num": "4.2", "title": "Mandatory Interstate Closure Halt", "text": "If state DOT authorities close Interstate 80, 90, or 94 due to blizzard conditions or multi-vehicle pileups, drivers must immediately divert to designated safe truck stops."},
            {"num": "4.3", "title": "Preemptive 12-Hour Weather Notice", "text": "Upon issuance of an NWS Winter Storm Warning along the transit route, carrier must transmit electronic notice to all downstream clinics within twelve (12) hours to preserve Force Majeure waiver eligibility."}
        ],
        "financial": [
            {"item": "Force Majeure Delay Waiver", "detail": "100% waiver of standard delay penalties for shipments traversing officially closed DOT corridors, conditioned on timely 12h notice."},
            {"item": "Freeze Spoilage Liability", "detail": "Carrier bears 100% replacement liability for frozen cargo if PFF heated trailer service was booked but heater unit was turned off or ran out of fuel."},
            {"item": "Intermodal Transfer Cost Share", "detail": "Shipper pays 50% of rail drayage differential if intermodal bypass is authorized by AI Copilot."}
        ],
        "exceptions": [
            {"condition": "Localized Lake-Effect Snow Squall", "detail": "Rapid unforecasted lake-effect squalls causing sudden pileups grant automatic 24-hour penalty grace upon state police verification."},
            {"condition": "Dry Kibble Exemption", "detail": "Dry pet nutrition (PET_DRY) is freeze-tolerant and exempt from heated van requirements, provided moisture barrier is unbroken."}
        ],
        "enforcement": [
            {"trigger": "NWS issues Blizzard Warning for corridor overlapping VTTK route", "action": "Copilot automatically tags shipment as 'WEATHER_DISRUPTED', alerts receiving clinics, and recalculates PDD + 48 hours."},
            {"trigger": "Highway reopens", "action": "Carrier required to resume linehaul within 4 hours; delay clock reactivates 6 hours post-reopening."}
        ]
    },

    {
        "category": "Regional Hazard Policies",
        "file_stem": "South-Central Tornado, Severe Hail & Flash Flood (I-35) Emergency Protocol",
        "title": "South-Central Tornado, Severe Hail & Flash Flood (I-35) Emergency Protocol",
        "header": {
            "Document ID": "WTH-SOP-2026-002-SCEN",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Disaster Response, Fleet Safety, & South-Central Regional Logistics",
            "Geographic Region": "South-Central Corridor (Dallas PL03 servicing TX, OK, KS, MO, AR, LA)",
            "Target SAP Tables / Fields": "VTTK (ROUTE, TPLST), LIKP (WERKS = 'PL03', VSTEL = 'SH03'), VBAK (KUNNR)"
        },
        "purpose": (
            "Establishes emergency response procedures, driver safety protocols, and commercial claim boundaries for tornadoes, "
            "severe hail outbreaks (> 1.5 inch diameter), and catastrophic flash flooding across the Interstate 35 and Interstate 40 "
            "transit lanes. Prioritizes human life preservation while maintaining clinical diet supply chains."
        ),
        "definitions": [
            {"term": "Tornado Warning (Severe Threat)", "definition": "NWS confirmation that a tornado is occurring or imminent; immediate trigger for freight transit suspension within the warning polygon."},
            {"term": "Hail Protection Shelter Protocol", "definition": "Mandatory parking of commercial tractors and trailers beneath covered structures or reinforced fuel canopies when hail > 1.5 inches is predicted."},
            {"term": "Flash Flood Inundation Zone", "definition": "Low-lying highway segments experiencing water over roadway exceeding 15 cm (6 inches); strict prohibition against crossing."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Immediate Shelter-In-Place Mandate", "text": "When a Tornado Warning polygon intersects a commercial vehicle's GPS coordinates, driver is legally mandated to seek hardened shelter immediately. Commercial transit must remain suspended until warning expires."},
            {"num": "4.2", "title": "Flash Flood Rerouting Obligation", "text": "Drivers must never drive into standing floodwaters. Carrier dispatch must utilize dynamic GPS rerouting to circumvent submerged river valleys and low-water crossings."},
            {"num": "4.3", "title": "Proactive 12-Hour Weather Notice", "text": "Carrier must transmit weather disruption notification to destination clinics and Copilot within twelve (12) hours of severe storm outbreak to qualify for Act of God immunity."}
        ],
        "financial": [
            {"item": "Tornadic / Flood Delay Immunity", "detail": "100% waiver of SLA delay penalties for duration of active NWS warnings plus twelve (12) hours road recovery window."},
            {"item": "Flood Cargo Destruction Liability", "detail": "Carrier strictly liable for 100% of cargo losses if driver drowns engine or trailer by entering marked high-water flood zones."},
            {"item": "Hail Damage Liability Waiver", "detail": "Tractor cosmetic hail damage is non-compensable; trailer roof puncture resulting in cargo water damage requires carrier liability insurance claim."}
        ],
        "exceptions": [
            {"condition": "Unheralded Nighttime Tornadogenesis", "detail": "Tornadoes touching down with < 10 minutes NWS lead time grant immediate, total penalty exoneration for affected carriers."},
            {"condition": "Consignee Clinic Flood Damage", "detail": "If destination veterinary clinic is flooded, clinic receiving surcharge waived and cargo held at terminal free for 7 days."}
        ],
        "enforcement": [
            {"trigger": "NOAA API confirms active Tornado Warning intersecting tractor coordinates", "action": "Copilot dispatches emergency safety SMS to driver, flags order in SAP with Force Majeure waiver code."},
            {"trigger": "Flood halts I-35 transit > 24 hours", "action": "Copilot calculates alternate transit route via I-20 / I-45 and re-optimizes delivery schedule."}
        ]
    },

    {
        "category": "Regional Hazard Policies",
        "file_stem": "Gulf Coast & Southeast Hurricane Emergency Action Plan",
        "title": "Gulf Coast & Southeast Hurricane Emergency Action Plan",
        "header": {
            "Document ID": "WTH-SOP-2026-003-GULF",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Enterprise Emergency Management, Maritime Logistics, & Southeast Operations",
            "Geographic Region": "Southeast & Gulf Coast (Atlanta PL01 servicing GA, FL, SC, NC, AL, MS)",
            "Target SAP Tables / Fields": "VTTK (ROUTE, TPLST), LIKP (WERKS = 'PL01', VSTEL = 'SH01'), VBAK (KUNNR)"
        },
        "purpose": (
            "Governs preemptive supply chain adjustments, coastal freight embargoes, storm surge asset protections, and "
            "post-landfall relief operations for tropical storms and Category 1 through 5 hurricanes impacting the Gulf Coast "
            "and Southeastern seaboard. Balances life-safety mandatory evacuations with critical animal hospital disaster supplies."
        ),
        "definitions": [
            {"term": "NHC Hurricane Warning (36h Lead)", "definition": "National Hurricane Center notification that hurricane-force winds (>= 119 km/h / 74 mph) are expected within coastal territory within 36 hours."},
            {"term": "Preemptive Advance Fulfillment (PAF)", "definition": "The automated advance shipment of 14 to 21 days of critical veterinary diets dispatched 72 hours prior to forecast storm landfall."},
            {"term": "Coastal Transit Embargo", "definition": "Total cessation of commercial freight dispatches into mandatory coastal evacuation zones twenty-four (24) hours prior to projected landfall."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Preemptive Order Acceleration", "text": "Upon issuance of a 72-hour Hurricane Watch, the AI Copilot autonomously identifies all partner clinics in the projected cone of uncertainty and releases advance replenish orders from Atlanta PL01."},
            {"num": "4.2", "title": "Mandatory 24-Hour Embargo", "text": "Twenty-four (24) hours prior to forecast landfall, all inbound freight movements into the evacuation zone are halted to ensure highways remain clear for civilian evacuation."},
            {"num": "4.3", "title": "State of Emergency SLA Immunity", "text": "All SLA delivery mandates, delay penalties, and dock receiving rules are suspended 100% across the affected geographic region upon official gubernatorial declaration of state of emergency."}
        ],
        "financial": [
            {"item": "Hurricane Force Majeure Waiver", "detail": "Total 100% waiver of all SLA delay penalties throughout the state of emergency plus seventy-two (72) hours post-storm recovery."},
            {"item": "Emergency Advance Order Freight Subsidy", "detail": "Enterprise covers 100% of expedited linehaul freight surcharges for advance disaster buffer stock dispatched to clinics."},
            {"item": "Storm Surge Product Loss", "detail": "Freight destroyed by storm surge inundation covered under enterprise global marine cargo casualty insurance policy."}
        ],
        "exceptions": [
            {"condition": "Official Post-Landfall Relief Convoy", "detail": "Carriers operating authorized humanitarian relief convoys under state police escort are exempt from curfew restrictions."},
            {"condition": "False Alarm / Dissipating Storm", "detail": "If storm veers out to sea or drops below tropical storm strength, standard transit operations and SLA rules resume within 24 hours."}
        ],
        "enforcement": [
            {"trigger": "NHC forecasts Category 1+ landfall within 72 hours", "action": "Copilot triggers Preemptive Advance Fulfillment orders in SAP, reserves dedicated reefer capacity at Atlanta PL01, and issues clinic advisories."},
            {"trigger": "Gubernatorial State of Emergency signed", "action": "System logs automatic blanket Force Majeure immunity in SAP for all affected ZIP codes."}
        ]
    },

    {
        "category": "Regional Hazard Policies",
        "file_stem": "Desert Southwest Extreme Ambient Heat (Over 42C) Transit Protocol",
        "title": "Desert Southwest Extreme Ambient Heat (>42C) Transit Protocol",
        "header": {
            "Document ID": "WTH-SOP-2026-004-HEAT",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Cold Chain Engineering, Fleet Maintenance, & Southwest Regional Safety",
            "Geographic Region": "Desert Southwest (Transit through Phoenix, Tucson, Las Vegas, Imperial Valley)",
            "Target SAP Tables / Fields": "VTTK (ROUTE), LIKP (VBELN, BTGEW), MARA (MATKL, SPECIALTY_DIET_FLAG)"
        },
        "purpose": (
            "Mitigates cargo thermal degradation, trailer tire blowout risks, and driver heat stroke during extreme summer "
            "temperature events exceeding 42.0°C (107.6°F) across the Desert Southwest logistics corridors. Enforces night-transit "
            "windows and thermal barrier protection for sensitive clinical nutrition."
        ),
        "definitions": [
            {"term": "Extreme Thermal Hazard (>42°C)", "definition": "Ambient outdoor temperature forecast exceeding 42.0°C recorded by NWS weather stations along Interstate 10, Interstate 8, or Interstate 40."},
            {"term": "Nocturnal Transit Window", "definition": "Mandatory scheduling of long-haul linehaul driving strictly between 20:00 (8 PM) and 06:00 (6 AM) local time to avoid peak solar radiation."},
            {"term": "Radiant Heat Pallet Barrier", "definition": "Heavy-duty reflective aluminum thermal barrier blankets placed over pallet loads to reflect radiant trailer ceiling heat."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Mandatory Nocturnal Linehaul", "text": "During declared Extreme Heat events, non-refrigerated trailers carrying veterinary nutrition must execute highway transit between 20:00 and 06:00. Daytime parking must utilize shaded rest facilities where available."},
            {"num": "4.2", "title": "Refrigeration Requirement for Clinical Diets", "text": "All therapeutic prescription diets (VET_DIET) and medicines must be transported in refrigerated trailers with cooling units operating continuously at 20.0°C (68.0°F) or below."},
            {"num": "4.3", "title": "Dock Door Exposure Limitation", "text": "Receiving docks in Phoenix, Tucson, and Las Vegas must complete pallet unloading and indoor air-conditioned staging within thirty (30) minutes of trailer door opening."}
        ],
        "financial": [
            {"item": "Thermal Spoilage Chargeback", "detail": "Carrier strictly liable for 100% cargo value if dry nutrition melts or spoils due to failure to utilize required nocturnal linehaul or thermal blankets."},
            {"item": "Tire Blowout Delay Relief", "detail": "Delays caused by extreme asphalt heat tire delamination granted a 4-hour grace buffer, provided driver replaces tire and resumes transit within 6 hours."},
            {"item": "Emergency Reefer Fuel Surcharge", "detail": "Approved $25.00 USD per day fuel allowance for continuous refrigeration unit operation during heat waves."}
        ],
        "exceptions": [
            {"condition": "Active Refrigerated Intermodal Rail", "detail": "Cargo moving via refrigerated well-car container rail across desert corridors is exempt from nocturnal scheduling."},
            {"condition": "Short Final-Mile Drayage (< 50 miles)", "detail": "Final-mile delivery from local climate-controlled cross-dock to clinic allowed during morning hours (06:00–10:00)."}
        ],
        "enforcement": [
            {"trigger": "NWS forecast predicts Phoenix corridor temp >= 42°C", "action": "Copilot checks dispatch schedule, reschedules linehaul departure for 20:00, and verifies reefer requirement in SAP."},
            {"trigger": "IoT temperature sensor inside trailer exceeds 40°C", "action": "Real-time thermal alert sent to driver and QA lead; delivery rerouted to emergency refrigerated cross-dock."}
        ]
    },

    {
        "category": "Regional Hazard Policies",
        "file_stem": "Pacific Northwest Atmospheric River & Mountain Pass Closure Protocol",
        "title": "Pacific Northwest Atmospheric River & Mountain Pass Closure Protocol",
        "header": {
            "Document ID": "WTH-SOP-2026-005-PNW",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Mountain Corridor Logistics, Pacific Northwest Safety, & Intermodal Ops",
            "Geographic Region": "Pacific Northwest (Washington, Oregon, Idaho - I-5, I-90, I-84 Mountain Corridors)",
            "Target SAP Tables / Fields": "VTTK (ROUTE), LIKP (VSTEL, VBELN), VBAK (KUNNR)"
        },
        "purpose": (
            "Governs freight navigation, chain-up safety mandates, rockslide diversions, and intermodal conversions across "
            "the Pacific Northwest mountain passes (Snoqualmie Pass, Stevens Pass, Siskiyou Pass, Columbia River Gorge) during "
            "severe winter atmospheric river rainfall and heavy Cascade mountain snowfall."
        ),
        "definitions": [
            {"term": "Atmospheric River Event", "definition": "A narrow corridor of concentrated moisture producing intense precipitation exceeding 75 mm (3 inches) in 24 hours, triggering mudslides and highway washouts."},
            {"term": "Mandatory Mountain Pass Closure", "definition": "Official State DOT closure of I-90 Snoqualmie or I-5 mountain passes due to avalanche control, mudslides, or multi-rig jackknifes."},
            {"term": "Columbia River Gorge Diversion", "definition": "Secondary southern detour utilizing Interstate 84 when northern Cascade mountain passes are impassable."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Mandatory Tire Chain Compliance", "text": "All motor carriers operating mountain passes between November 1 and April 1 must carry certified tire chains and comply with State DOT mandatory chain-up signage."},
            {"num": "4.2", "title": "Pass Closure Rerouting Mandate", "text": "If mountain pass closure is projected to exceed twelve (12) hours, carrier dispatch must immediately reroute freight via Interstate 84 or request intermodal rail conversion."},
            {"num": "4.3", "title": "Proactive 12-Hour Weather Notice", "text": "Carrier must transmit weather delay notification to Seattle, Tacoma, and Portland clinics at least twelve (12) hours prior to PDD to qualify for pass closure penalty waivers."}
        ],
        "financial": [
            {"item": "Mountain Pass Force Majeure Waiver", "detail": "100% waiver of SLA delay penalties for verifiable state DOT pass closures, conditioned on 12-hour advance notice."},
            {"item": "Detour Mileage Surcharge", "detail": "Shipper reimburses verified excess detour mileage (up to 250 miles at contractual fuel rate) for authorized southern highway diversions."},
            {"item": "Failure to Carry Chains Penalty", "detail": "$500.00 USD non-compliance fee assessed against carrier if driver is stranded without required snow chains."}
        ],
        "exceptions": [
            {"condition": "Intermodal Rail Conversion", "detail": "If freight is transferred to BNSF Northern Rail Corridor to bypass highway closures, customer SLA extended by 48 hours without penalty."},
            {"condition": "Coastal Highway Availability", "detail": "Shipments operating strictly on low-elevation coastal US-101 routes are exempt from mountain pass rules."}
        ],
        "enforcement": [
            {"trigger": "WSDOT announces Snoqualmie Pass closure > 8 hours", "action": "Copilot detects closure via DOT API feed, notifies impacted Seattle clinics, and updates SAP delivery schedule."},
            {"trigger": "Carrier driver stranded due to lack of snow chains", "action": "Penalty waiver denied; carrier assessed $500 fine and held 100% liable for resulting clinic delay penalties."}
        ]
    },

    # =========================================================================
    # CATEGORY 5: EXCEPTIONAL CLAUSES, LEGAL WAIVERS & AI GOVERNANCE
    # Target Directory: Exceptional Clause Policies/
    # =========================================================================
    {
        "category": "Exceptional Clause Policies",
        "file_stem": "Force Majeure Tripartite Legal Burden & Event Substantiation Protocol",
        "title": "Force Majeure Tripartite Legal Burden & Event Substantiation Protocol",
        "header": {
            "Document ID": "EXC-POL-2026-001-FM",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Corporate Legal Affairs, Global Supply Chain Compliance, & Contract Arbitration",
            "Contractual Authority": "Uniform Commercial Code (UCC) § 2-615 & ICC Force Majeure Clause 2020",
            "Target SAP Tables / Fields": "VBAK (VBELN, LIFSK), LIKP (WADAT, WBSTK), VTTK (TKNUM, STATUS)"
        },
        "purpose": (
            "Establishes a rigorous tripartite legal test and documentary burden of proof for any party invoking Force Majeure "
            "(Act of God) exemptions to evade contractual SLA delay penalties. Harmonizes disparate contract terms to eliminate "
            "informal, unsubstantiated carrier delay claims while upholding genuine disaster immunity."
        ),
        "definitions": [
            {"term": "Tripartite Force Majeure Standard", "definition": "The three mandatory legal criteria that must be simultaneously proven: (1) Beyond Reasonable Control, (2) Unforeseeability at Tender, and (3) Inability to Mitigate."},
            {"term": "Condition Precedent Notice", "definition": "Mandatory electronic transmission of delay warning no less than twelve (12) hours prior to original PDD expiration per SLA-LOG-VNS-0023."},
            {"term": "Formal Substantiation Dossier", "definition": "A verified documentary submission filed within seventy-two (72) hours of event cessation containing official meteorological, government, or police records."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Tripartite Legal Burden of Proof", "text": "A carrier or supplier claiming Force Majeure bears the full legal burden of proving: (a) The event was caused by external natural or sovereign forces beyond its control; (b) The event could not have been anticipated or avoided through commercially reasonable diligence; and (c) The party took all reasonable measures to mitigate or circumvent the delay."},
            {"num": "4.2", "title": "Two-Stage Notice Obligation", "text": "Immunity is strictly conditional upon: (Stage 1) Automated electronic notification sent >= 12 hours prior to PDD; and (Stage 2) Full evidentiary dossier submitted within 72 hours of event termination."},
            {"num": "4.3", "title": "Exclusions from Force Majeure", "text": "Ordinary commercial risks—including driver hours of service exhaustion, routine mechanical breakdown, normal seasonal rain/snow, labor turnover, or fuel price fluctuations—are EXPRESSLY EXCLUDED from Force Majeure relief."},
            {"num": "4.4", "title": "Harmonization & Precedence", "text": "This protocol takes legal precedence over all conflicting language in prior vendor agreements. Unconditional weather waivers without notice compliance are null and void."}
        ],
        "financial": [
            {"item": "Full Waiver of Contractual Penalties", "detail": "100% relief from daily delay penalties upon certified satisfaction of tripartite test and two-stage notice mandate."},
            {"item": "Forfeiture for Failure to Mitigate", "detail": "Total loss of immunity and reinstatement of 100% delay penalties if party failed to provide 12h notice or rejected viable reroute options."},
            {"item": "Fraudulent Claim Sanction", "detail": "$1,000.00 USD administrative penalty plus immediate suspension of carrier preferred tier status for falsified weather claims."}
        ],
        "exceptions": [
            {"condition": "Catastrophic Communication Infrastructure Blackout", "detail": "If regional cell towers and satellite networks are physically destroyed by disaster, the 12h electronic notice mandate is deferred until communications restore."},
            {"condition": "Direct Presidential / Governor Emergency Order", "detail": "Official federal/state executive orders mandating total highway confiscation or civil curfew constitute self-authenticating Force Majeure."}
        ],
        "enforcement": [
            {"trigger": "Carrier files Force Majeure claim in portal", "action": "Copilot cross-references NOAA weather radar, DOT road closure feeds, and ELD timestamps to audit tripartite criteria."},
            {"trigger": "Claim fails 12h notice or tripartite test", "action": "Copilot issues automated claim denial citing Section 4.1/4.2, reinstates SAP penalty debit deduction."}
        ]
    },

    {
        "category": "Exceptional Clause Policies",
        "file_stem": "Autonomous AI Financial Mitigation & Threshold Governance Delegation Matrix",
        "title": "Autonomous AI Financial Mitigation & Threshold Governance Delegation Matrix",
        "header": {
            "Document ID": "EXC-POL-2026-002-GOV",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Enterprise AI Governance, Internal Audit, Corporate Finance, & Supply Chain Operations",
            "Contractual Authority": "Corporate Financial Authority Delegation & AI Systems of Record Charter",
            "Target SAP Tables / Fields": "BKPF (BELNR, BUKRS), BSEG (WRBTR, SHKZG), VBAK (NETWR), LIKP (LIFSK)"
        },
        "purpose": (
            "Establishes the governance boundaries, financial authorization thresholds, human-in-the-loop escalation gates, "
            "and cryptographic audit trail standards for autonomous decision-making by the AI Logistics Copilot. Ensures algorithmic "
            "speed while maintaining rigorous internal financial controls complying with Sarbanes-Oxley (SOX) Section 404."
        ),
        "definitions": [
            {"term": "Autonomous Level 1 Action", "definition": "Low-risk financial or operational decisions (<= $500.00 USD) executed directly by the AI agent without human intervention."},
            {"term": "Level 2 Managerial Approval", "definition": "Medium-risk decisions ($500.01 to $2,500.00 USD) requiring one-click authorization via Microsoft Teams Adaptive Cards by the Supply Chain Operations Manager."},
            {"term": "Level 3 Executive Authorization", "definition": "High-risk decisions (> $2,500.00 USD) requiring dual digital authorization from the Regional Supply Chain Director and Legal Counsel."},
            {"term": "Immutable SHA-256 Decision Log", "definition": "Cryptographically hashed audit entry stored in SQLite agent_traces table verifying model inputs, reasoning, and execution timestamps."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Three-Tier Financial Delegation Matrix", "text": "All automated financial deductions, chargebacks, freight upgrade approvals, and penalty waivers must strictly adhere to the established three-tier authorization limits."},
            {"num": "4.2", "title": "Mandatory Human-in-the-Loop Threshold", "text": "Any single transaction exceeding $500.00 USD cannot be committed to SAP FI/CO without affirmative human digital sign-off. The Copilot is barred from auto-approving cumulative daily transactions exceeding $5,000.00 per vendor."},
            {"num": "4.3", "title": "SOX Compliance & Tamper-Evident Audit", "text": "Every automated and manual action must record: (1) Prompt & model version, (2) Tool call parameters, (3) Associated SAP document keys, and (4) SHA-256 integrity hash."},
            {"num": "4.4", "title": "Autonomous Safe-State Failsafe", "text": "In the event of network disconnection, LLM hallucinations, or database lockouts, the system must fail safe to Level 2 human manual review without executing unverified financial postings."}
        ],
        "financial": [
            {"item": "Level 1 Autonomous Ceiling", "detail": "Up to $500.00 USD per transaction (e.g. Standard SLA penalty deduction, $150 redelivery fee waiver, minor detour reimbursement)."},
            {"item": "Level 2 Managerial Ceiling", "detail": "$500.01 to $2,500.00 USD (e.g. Emergency air freight upgrade, multi-day delay penalty, high-value freight rerouting)."},
            {"item": "Level 3 Executive Floor", "detail": "Greater than $2,500.00 USD (e.g. Total batch condemnation, multi-truck embargo, broad Force Majeure declaration)."},
            {"item": "Annual AI Audit Reconciliation", "detail": "Quarterly internal audit sampling 100% of Level 1 autonomous actions for financial accuracy."}
        ],
        "exceptions": [
            {"condition": "Imminent Life-Safety Clinical Emergency", "detail": "When life-critical ICU animal medicine is stranded, Operations Manager can verbally authorize override up to $5,000, logged within 24 hours."},
            {"condition": "System Scheduled Maintenance", "detail": "Financial actions queued in memory during maintenance and batch-processed upon validation."}
        ],
        "enforcement": [
            {"trigger": "Mitigation recommendation <= $500.00", "action": "Copilot executes direct SAP posting, logs trace, and reports in daily executive JSON digest."},
            {"trigger": "Mitigation recommendation > $500.00", "action": "Copilot generates Microsoft Teams Adaptive Card to Operations Manager with approve/reject buttons; awaits response."}
        ]
    },

    {
        "category": "Exceptional Clause Policies",
        "file_stem": "Telematics Blackout, Jamming & Blind-Tracking Sanctions Policy",
        "title": "Telematics Blackout, Jamming & Blind-Tracking Sanctions Policy",
        "header": {
            "Document ID": "EXC-POL-2026-003-TELEM",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Asset Protection, Digital Supply Chain Security, & Logistics Legal",
            "Contractual Scope": "All Motor Carriers and Intermodal Logistics Providers",
            "Target SAP Tables / Fields": "LFA1 (LIFNR), VTTK (TKNUM), LIKP (VBELN), VBAK (KUNNR)"
        },
        "purpose": (
            "Enforces uninterrupted, real-time cellular and satellite IoT telematics visibility (project44, FourKites) for all "
            "commercial shipments carrying veterinary pharmaceuticals and clinical nutrition. Establishes severe commercial penalties "
            "and legal consequences for unannounced telematics blackouts, driver GPS tampering, or cargo abandonment."
        ),
        "definitions": [
            {"term": "Continuous Telematics Feed", "definition": "Automated cellular/satellite GPS location and temperature pings transmitted at intervals not exceeding fifteen (15) minutes during transit."},
            {"term": "Telematics Blackout", "definition": "An unexplained cessation of GPS signal or telematics pings exceeding four (4.0) continuous hours while freight is in transit on commercial corridors."},
            {"term": "Blind-Tracking Surcharge", "definition": "A punitive non-performance fee assessed against the carrier for operating in violation of the mandatory visibility charter."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Mandatory Visibility Charter", "text": "All contracted carriers must maintain active, certified API/EDI telematics integration with the enterprise tracking platform throughout linehaul transit."},
            {"num": "4.2", "title": "Four-Hour Blackout Breach", "text": "Any signal loss exceeding four (4.0) consecutive hours without prior notification constitutes an immediate material breach of contract."},
            {"num": "4.3", "title": "Nullification of Force Majeure Immunity", "text": "A carrier operating during a telematics blackout is legally barred from claiming weather-related Force Majeure exemptions. The burden of proof for cargo temperature and punctuality shifts entirely to the carrier."},
            {"num": "4.4", "title": "GPS Jamming Zero-Tolerance", "text": "Intentional driver use of illegal GPS jamming devices or deliberate ELD manipulation results in immediate permanent carrier debarment and referral to federal law enforcement."}
        ],
        "financial": [
            {"item": "Blind-Tracking Surcharge", "detail": "$200.00 USD flat fee per blackout occurrence exceeding 4.0 hours."},
            {"item": "Hourly Extended Blackout Fee", "detail": "$50.00 USD per additional hour past 4 hours until telematics signal is restored."},
            {"item": "Cargo Audit Inspection Fee", "detail": "If biological cargo arrives following blackout, mandatory $350.00 QA thermal assay charged to carrier."},
            {"item": "Permanent Debarment Clause", "detail": "Three (3) unexcused blackout violations within 90 days results in total contract cancellation."}
        ],
        "exceptions": [
            {"condition": "Verified National Cellular Carrier Network Outage", "detail": "Documented major carrier network failures verified by carrier service advisories excuse signal loss."},
            {"condition": "Remote Mountain Canyons (Documented Dead Zones)", "detail": "Established geographic dead zones (< 2 hours duration) pre-mapped in telemetry database are exempt from penalties."}
        ],
        "enforcement": [
            {"trigger": "Telematics feed silent for 4.0 hours", "action": "Copilot flags shipment as 'BLIND_TRACKING_VIOLATION', issues $200 penalty in SAP, and alerts Corporate Asset Protection."},
            {"trigger": "Signal restored", "action": "Carrier required to submit ELD driver log verifying route continuity and temperature integrity within 24 hours."}
        ]
    },

    {
        "category": "Exceptional Clause Policies",
        "file_stem": "Maritime Port Terminal Congestion & Intermodal Container Demurrage Protocol",
        "title": "Maritime Port Terminal Congestion & Intermodal Container Demurrage Protocol",
        "header": {
            "Document ID": "EXC-POL-2026-004-PORT",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "International Logistics, Ocean Freight Operations, & Trade Compliance",
            "Contractual Authority": "Ocean Shipping Reform Act (OSRA) & Federal Maritime Commission (FMC) Guidelines",
            "Target SAP Tables / Fields": "VTTK (TKNUM, TDLNR), LIKP (VBELN), MARA (MATKL = 'SURGICAL', 'VET_MED')"
        },
        "purpose": (
            "Governs international ocean container dwell times, railhead drayage bottlenecks, and demurrage dispute standards "
            "for imported raw materials, veterinary pharmaceuticals, and sterile surgical packaging arriving via US container ports "
            "(Port of Los Angeles/Long Beach, Port of New York/New Jersey, Port of Savannah, Port of Houston)."
        ),
        "definitions": [
            {"term": "Terminal Free Time", "definition": "A standard period of four (4) business days following ocean container discharge before terminal storage demurrage commences."},
            {"term": "Unjust Demurrage (OSRA Non-Compliance)", "definition": "Storage fees assessed during periods when the container was physically unavailable for pickup due to port labor strikes, gate closures, or chassis shortages."},
            {"term": "Off-Dock Depot Drayage Diversion", "definition": "Emergency transfer of containers from congested marine terminals to near-dock inland container yards (CY) to halt demurrage clocks."}
        ],
        "clauses": [
            {"num": "4.1", "title": "FMC Demurrage Invalidation Standard", "text": "Per Federal Maritime Commission rules, ocean terminal operators and drayage carriers are prohibited from billing demurrage if an appointment could not be secured or container was in a closed yard stack."},
            {"num": "4.2", "title": "Five-Day Dwell Action Threshold", "text": "If container dwell at marine terminal reaches five (5) calendar days, the Copilot automatically authorizes emergency off-dock drayage transfer to bypass terminal demurrage rates."},
            {"num": "4.3", "title": "Customs Hold Grace Protection", "text": "Delays caused by random US Customs & Border Protection (CBP) or FDA intensive agricultural exams are deemed sovereign interventions, granting 5-day penalty immunity to downstream clinic SLAs."}
        ],
        "financial": [
            {"item": "Off-Dock Drayage Diversion Subsidy", "detail": "Enterprise funds up to $650.00 USD per container for emergency inland drayage to preserve surgical supply pipelines."},
            {"item": "Illegal Demurrage Dispute Recovery", "detail": "All improper demurrage invoices disputed via FMC portal; disputed funds held in escrow pending resolution."},
            {"item": "Downstream Clinic SLA Extension", "detail": "SLA delivery dates for imported goods under verified port strike extended by up to seven (7) business days without penalty."}
        ],
        "exceptions": [
            {"condition": "Longshoremen Union Strike (ILA / ILWU)", "detail": "Official dockworker labor strikes shut down all demurrage accruals under OSRA Section 7 statutory protections."},
            {"condition": "Importer of Record Paperwork Delay", "detail": "If delay stems from enterprise customs broker paperwork error, ocean terminal demurrage is fully absorbed by enterprise."}
        ],
        "enforcement": [
            {"trigger": "Port strike or gate closure detected via news/RSS feed", "action": "Copilot flags all active ocean containers in transit, notifies manufacturing plants of potential raw material delays."},
            {"trigger": "Demurrage invoice received for strike period", "action": "Automatic generation of FMC OSRA formal dispute letter; invoice flagged 'DISPUTED_UNLAWFUL_DEMURRAGE'."}
        ]
    },

    {
        "category": "Exceptional Clause Policies",
        "file_stem": "Critical Clinical Stock-Out Fast-Track Allocation & Triage Protocol",
        "title": "Critical Clinical Stock-Out Fast-Track Allocation & Triage Protocol",
        "header": {
            "Document ID": "EXC-POL-2026-005-STCK",
            "Effective Date": "September 15, 2026",
            "Controlling Department": "Clinical Veterinary Affairs, Emergency Triage Operations, & Customer Success",
            "Material Classification": "Life-Critical Prescription Nutrition & Urgent Therapeutics (MARA-SPECIALTY_DIET_FLAG = 'TRUE')",
            "Target SAP Tables / Fields": "MARA (MATNR, MATKL), KNA1 (KUNNR), VBAK (VBELN, NETWR), LIPS (LFIMG)"
        },
        "purpose": (
            "Establishes emergency inventory borrow-and-transfer mechanisms, local clinical hotshot delivery channels, and "
            "priority triage protocols when catastrophic transit disruptions threaten to cause complete life-safety stock-outs "
            "of essential therapeutic diets (Gastrointestinal, Renal, Hypoallergenic) at critical animal trauma hospitals."
        ),
        "definitions": [
            {"term": "Imminent Clinical Stock-Out", "definition": "A condition where a Tier 1 or Tier 2 hospital has less than twenty-four (24) hours of life-critical patient nutrition remaining due to an en-route transit delay."},
            {"term": "Peer-Clinic Emergency Borrow", "definition": "The authorized transfer of sealed inventory from a nearby partner clinic within 50 miles to triage immediate animal patient needs."},
            {"term": "Hotshot Courier Fast-Track", "definition": "Direct point-to-point dedicated courier transit bypassing all commercial freight terminals to deliver emergency supplies."}
        ],
        "clauses": [
            {"num": "4.1", "title": "Clinical Stock-Out Declaration", "text": "A hospital veterinary director may declare an Imminent Stock-Out when verified patient diet inventory falls below 24 hours of clinical requirement and incoming delivery is delayed > 24 hours."},
            {"num": "4.2", "title": "Tripartite Triage Protocol", "text": "The enterprise executes three simultaneous fast-track options: (1) Emergency borrow from closest partner clinic within 50 miles; (2) Next-Flight-Out counter-to-counter air cargo; and (3) Hotshot courier van from nearest plant hub."},
            {"num": "4.3", "title": "Peer-Clinic Reimbursement Premium", "text": "Clinics providing emergency borrow stock receive an immediate credit memo equal to 110% of the invoice value, plus priority replenishment on the next morning delivery."}
        ],
        "financial": [
            {"item": "Emergency Borrow Transfer Subsidy", "detail": "100% of transfer courier fees and clinic compensation absorbed by enterprise emergency mitigation budget."},
            {"item": "110% Peer-Clinic Incentive Credit", "detail": "Loaning clinic credited 110% of standard order value in SAP FI/CO within 48 hours of inventory transfer."},
            {"item": "Carrier Liability Passthrough", "detail": "If emergency triage was caused by carrier unexcused default, carrier is billed up to $1,000.00 USD of hotshot mitigation costs."}
        ],
        "exceptions": [
            {"condition": "Patient Clinical Trial Non-Equivalence", "detail": "If patient is on double-blind clinical trial diet, peer-clinic borrow is prohibited; only factory-certified replacement allowed."},
            {"condition": "Open or Broken Inner Bag Packaging", "detail": "Only pristine, unopened, factory-sealed bags may be transferred between clinics under peer borrow protocol."}
        ],
        "enforcement": [
            {"trigger": "Hospital alerts Copilot to < 24h stock on specialty diet", "action": "QualityMitigation agent queries nearby clinic inventory in SAP KNA1/KNVV, identifies closest source, and drafts hotshot dispatch."},
            {"trigger": "Peer clinic confirms stock release", "action": "Copilot dispatches local medical courier, issues 110% credit memo to loaning clinic, and closes stock-out alert."}
        ]
    }
]


def generate_all_25_policy_docs():
    """Generates all 25 policy documents in both .docx and .md formats."""
    from modules.generate_policy_suite import build_docx, build_md, harmonize_existing_documents

    # 1. First harmonize existing documents
    harmonize_existing_documents()

    print("\n" + "="*80)
    print("📜 GENERATING 25 ENTERPRISE POLICY & SLA DOCUMENTS (.docx & .md)")
    print("="*80)

    generated_count = 0
    for idx, p_doc in enumerate(POLICY_DOCUMENTS, 1):
        target_dir = Path(f"d:/Progamming/O2C_AI/india_monitor_data/rag/documents/{p_doc['category']}")
        target_dir.mkdir(parents=True, exist_ok=True)

        import re
        safe_stem = re.sub(r'[<>:"/\\|?*]', '_', p_doc['file_stem'])
        docx_path = target_dir / f"{safe_stem}.docx"
        md_path = target_dir / f"{safe_stem}.md"

        # Generate DOCX
        build_docx(p_doc, docx_path)
        # Generate MD
        build_md(p_doc, md_path)

        generated_count += 1
        doc_id = p_doc['header'].get('Document ID', f'DOC-{idx:03d}')
        print(f"[{idx:02d}/25] {doc_id} | {p_doc['category'][:16]:16s} -> {p_doc['file_stem'][:45]}...")

    print("\n" + "="*80)
    print(f"✅ Successfully generated {generated_count} enterprise policy documents (50 files total: 25 .docx + 25 .md)!")
    print("="*80)


if __name__ == "__main__":
    generate_all_25_policy_docs()
