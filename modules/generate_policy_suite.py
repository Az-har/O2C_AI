"""
Enterprise Policy & SLA Suite Generator.
Generates 25 comprehensive, legally rigorous, and operationally sound policy documents
in both Markdown (.md) and Word (.docx) formats, and harmonizes existing SLA contradictions.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Windows encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

# Base directories
BASE_DIR = Path("d:/Progamming/O2C_AI/india_monitor_data/rag/documents")
CLINIC_DIR = BASE_DIR / "Clinic SLA's"
VENDOR_DIR = BASE_DIR / "Vendor Contract Docs"
PKG_DIR = BASE_DIR / "Packaging Policy Docs"
REGIONAL_DIR = BASE_DIR / "Regional Hazard Policies"
EXC_DIR = BASE_DIR / "Exceptional Clause Policies"

for d in [CLINIC_DIR, VENDOR_DIR, PKG_DIR, REGIONAL_DIR, EXC_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def build_docx(doc_dict: dict, file_path: Path):
    """Builds a beautifully styled Word document from structured document dictionary."""
    doc = Document()

    # Set Margins
    for sec in doc.sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.8)
        sec.right_margin = Inches(0.8)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run(doc_dict["title"].upper())
    r_title.bold = True
    r_title.font.size = Pt(16)
    r_title.font.color.rgb = RGBColor(16, 44, 87)  # Deep Navy

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE")
    r_sub.font.size = Pt(10)
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph()  # spacing

    # 1. Header Metadata Table
    h1 = doc.add_heading("1. Document Header & Scope", level=1)
    h1.runs[0].font.color.rgb = RGBColor(30, 58, 138)

    meta_table = doc.add_table(rows=len(doc_dict["header"]), cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.style = 'Table Grid'
    for i, (k, v) in enumerate(doc_dict["header"].items()):
        cell_k = meta_table.cell(i, 0)
        cell_v = meta_table.cell(i, 1)
        cell_k.text = k
        cell_v.text = str(v)
        cell_k.paragraphs[0].runs[0].bold = True
        cell_k.paragraphs[0].runs[0].font.size = Pt(9.5)
        cell_v.paragraphs[0].runs[0].font.size = Pt(9.5)
        cell_k.width = Inches(2.2)
        cell_v.width = Inches(4.5)

    doc.add_paragraph()

    # 2. Commercial Purpose & Operational Context
    h2 = doc.add_heading("2. Commercial Purpose & Operational Context", level=1)
    h2.runs[0].font.color.rgb = RGBColor(30, 58, 138)
    p2 = doc.add_paragraph(doc_dict["purpose"])
    p2.style.font.size = Pt(10)

    # 3. Key Definitions & Operational Thresholds
    h3 = doc.add_heading("3. Key Definitions & Operational Thresholds", level=1)
    h3.runs[0].font.color.rgb = RGBColor(30, 58, 138)
    for def_item in doc_dict["definitions"]:
        p_def = doc.add_paragraph()
        r_term = p_def.add_run(f"• {def_item['term']}: ")
        r_term.bold = True
        p_def.add_run(def_item['definition'])

    # 4. Core Binding SLA / Policy Clauses
    h4 = doc.add_heading("4. Core Binding SLA / Policy Clauses", level=1)
    h4.runs[0].font.color.rgb = RGBColor(30, 58, 138)
    for clause in doc_dict["clauses"]:
        p_cl = doc.add_paragraph()
        r_sec = p_cl.add_run(f"{clause['num']} {clause['title']}\n")
        r_sec.bold = True
        p_cl.add_run(clause['text'])

    # 5. Financial Matrices, Deductions & Liability Caps
    h5 = doc.add_heading("5. Financial Matrices, Penalties & Liability Caps", level=1)
    h5.runs[0].font.color.rgb = RGBColor(30, 58, 138)
    for fin in doc_dict["financial"]:
        p_fin = doc.add_paragraph()
        r_f = p_fin.add_run(f"• {fin['item']}: ")
        r_f.bold = True
        p_fin.add_run(fin['detail'])

    # 6. Exceptional Clauses, Waivers & Relief Criteria
    h6 = doc.add_heading("6. Exceptional Clauses & Relief Criteria", level=1)
    h6.runs[0].font.color.rgb = RGBColor(30, 58, 138)
    for exc in doc_dict["exceptions"]:
        p_exc = doc.add_paragraph()
        r_e = p_exc.add_run(f"• {exc['condition']}: ")
        r_e.bold = True
        p_exc.add_run(exc.get('relief', exc.get('detail', '')))

    # 7. Autonomous AI Enforcement & System of Record Actions
    h7 = doc.add_heading("7. Autonomous AI Enforcement & System of Record Actions", level=1)
    h7.runs[0].font.color.rgb = RGBColor(30, 58, 138)
    for act in doc_dict["enforcement"]:
        p_act = doc.add_paragraph()
        r_a = p_act.add_run(f"• {act['trigger']}: ")
        r_a.bold = True
        p_act.add_run(act['action'])

    # Save docx
    doc.save(file_path)


def build_md(doc_dict: dict, file_path: Path):
    """Builds clean, high-density Markdown version of document for fast RAG vectorization."""
    lines = []
    lines.append(f"# {doc_dict['title']}\n")
    lines.append("**ENTERPRISE SERVICE LEVEL AGREEMENT & STANDARD OPERATING PROCEDURE**\n")
    lines.append("---\n")

    lines.append("## 1. Document Header & Scope\n")
    lines.append("| Metadata Field | Parameter Value |")
    lines.append("|---|---|")
    for k, v in doc_dict["header"].items():
        lines.append(f"| **{k}** | {v} |")
    lines.append("")

    lines.append("## 2. Commercial Purpose & Operational Context\n")
    lines.append(f"{doc_dict['purpose']}\n")

    lines.append("## 3. Key Definitions & Operational Thresholds\n")
    for d in doc_dict["definitions"]:
        lines.append(f"- **{d['term']}**: {d['definition']}")
    lines.append("")

    lines.append("## 4. Core Binding SLA / Policy Clauses\n")
    for c in doc_dict["clauses"]:
        lines.append(f"### {c['num']} {c['title']}")
        lines.append(f"{c['text']}\n")

    lines.append("## 5. Financial Matrices, Penalties & Liability Caps\n")
    for f in doc_dict["financial"]:
        lines.append(f"- **{f['item']}**: {f['detail']}")
    lines.append("")

    lines.append("## 6. Exceptional Clauses & Relief Criteria\n")
    for e in doc_dict["exceptions"]:
        lines.append(f"- **{e['condition']}**: {e.get('relief', e.get('detail', ''))}")
    lines.append("")

    lines.append("## 7. Autonomous AI Enforcement & System of Record Actions\n")
    for a in doc_dict["enforcement"]:
        lines.append(f"- **{a['trigger']}**: {a['action']}")
    lines.append("")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def harmonize_existing_documents():
    """Resolves legal and operational contradictions in existing documents."""
    print("🔄 Harmonizing existing documents that contradict industry best practices...")

    # Contradiction 1: Severe Weather Liability Waiver & Force Majeure Declaration.docx
    # Must explicitly condition relief on the 12-hour proactive notification mandate
    target_f1 = VENDOR_DIR / "SEVERE WEATHER LIABILITY WAIVER & FORCE MAJEURE DECLARATION.docx"
    if target_f1.exists():
        try:
            doc1 = docx.Document(target_f1)
            # Add clarifying paragraph to Section 1 or 4
            p_add = doc1.add_paragraph()
            r_add = p_add.add_run("\n[HARMONIZATION AMENDMENT - CONDITION PRECEDENT COMPLIANCE]:\n"
                                  "Per UCC § 2-615 and ICC Force Majeure 2020 standards, any claim of severe weather "
                                  "or Act of God immunity is STRICTLY CONDITIONAL upon the carrier having transmitted "
                                  "electronic delay notification at least twelve (12) hours prior to the Promised Delivery Date (PDD) "
                                  "per SLA-LOG-VNS-0023. Failure to provide timely notice constitutes a failure to mitigate and forfeits all penalty waivers.")
            r_add.bold = True
            r_add.font.color.rgb = RGBColor(180, 0, 0)
            doc1.save(target_f1)
            print("   ✅ Harmonized: SEVERE WEATHER LIABILITY WAIVER & FORCE MAJEURE DECLARATION.docx")
        except Exception as e:
            print(f"   ⚠️ Could not harmonize doc1: {e}")

    # Contradiction 2: Platinum Tier Delivery & Delay Penalty Framework.docx
    # Must clarify zero grace period for AUART = RUSH orders
    target_f2 = CLINIC_DIR / "Platinum Tier Delivery & Delay Penalty Framework.docx"
    if target_f2.exists():
        try:
            doc2 = docx.Document(target_f2)
            p_add2 = doc2.add_paragraph()
            r_add2 = p_add2.add_run("\n[HARMONIZATION AMENDMENT - EXPEDITED RUSH EXCLUSION]:\n"
                                    "The 24-hour Grace Period outlined in Section 4.3 applies EXCLUSIVELY to Standard Sales Orders (AUART = 'OR'). "
                                    "For Expedited Rush Orders (AUART = 'RUSH'), the Grace Period is exactly ZERO (0) hours. Any delay beyond "
                                    "the established Promised Delivery Date immediately incurs the full $500.00/day Platinum delay penalty.")
            r_add2.bold = True
            r_add2.font.color.rgb = RGBColor(180, 0, 0)
            doc2.save(target_f2)
            print("   ✅ Harmonized: Platinum Tier Delivery & Delay Penalty Framework.docx")
        except Exception as e:
            print(f"   ⚠️ Could not harmonize doc2: {e}")


print("Enterprise Policy Suite module loaded.")
