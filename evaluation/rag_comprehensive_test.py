#!/usr/bin/env python3
"""
RAG Comprehensive Testing & Evaluation

Runs comprehensive targeted test queries across all 78 document categories
and saves results to evaluation folder for performance & coverage analysis.

Usage:
    python evaluation/rag_comprehensive_test.py
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Configure UTF-8 encoding for Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# Databricks Workspace Path Support
DATABRICKS_PATH = Path("/Workspace/Users/ayyash.a@tcs.com/O2C_AI")
if DATABRICKS_PATH.exists() or "DATABRICKS_RUNTIME_VERSION" in os.environ:
    project_root = DATABRICKS_PATH
else:
    try:
        project_root = Path(__file__).parent.parent.resolve()
    except NameError:
        project_root = DATABRICKS_PATH

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from modules.config import DB_PATH
from modules.database_manager import DatabaseManager
from modules.rag_engine import RAGEngine
from modules.rag_evaluator import RAGEvaluator


class RAGComprehensiveTest:
    """Comprehensive RAG testing across all 78 document categories"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.rag = RAGEngine()
        self.output_dir = project_root / "evaluation"
        self.output_dir.mkdir(exist_ok=True)
        
    def run_comprehensive_tests(self, clear_old_test_data: bool = False):
        """Run all test queries and evaluate document retrieval coverage"""
        print("=" * 80)
        print("🧪 RAG COMPREHENSIVE TEST SUITE - 78 DOCUMENT CORPUS COVERAGE")
        print("=" * 80)
        
        # Initialize RAG
        print("\n🤖 Initializing RAG system...")
        if not self.rag.initialize(force_rebuild=False):
            print("❌ RAG initialization failed")
            return False
        print("✅ RAG system ready\n")

        if clear_old_test_data:
            with self.db.connection() as conn:
                conn.execute("DELETE FROM rag_analyses WHERE strike_title LIKE 'Test Query%'")
            print("🧹 Cleared old synthetic test queries from rag_analyses table")
        
        # Define comprehensive test queries covering all 78 documents
        test_queries = self._get_test_queries()
        
        print(f"📋 Running {len(test_queries)} targeted test queries across 6 document categories...\n")
        
        results = []
        for i, (category, query) in enumerate(test_queries, 1):
            result = self.rag.ask(query)
            
            # Save to database
            self.db.write_rag_analysis(
                news_id=None,
                strike_title=f"Test Query - {category}",
                question=query,
                answer=result['answer'],
                confidence=result['confidence'],
                sources=result['sources']
            )
            
            top_sources = [s['filename'] for s in result['sources'][:3]]
            results.append({
                'category': category,
                'query': query,
                'confidence': result['confidence'],
                'top_sources': top_sources,
                'answer_preview': result['answer'][:200]
            })
            
            print(f"[{i:2d}/{len(test_queries)}] {category:<16}: {query[:55]}...")
            print(f"     ✅ Conf: {result['confidence']:.3f} | Top: {', '.join(top_sources[:2])}")
        
        # Save detailed results
        self._save_test_results(results)
        
        # Run evaluation against 78 document corpus
        print("\n" + "=" * 80)
        print("📊 RUNNING RAG EVALUATION BENCHMARK")
        print("=" * 80)
        
        evaluator = RAGEvaluator(db_path=str(DB_PATH), total_docs_in_corpus=78)
        eval_results = evaluator.evaluate()
        evaluator.print_report(eval_results)
        
        # Save evaluation report
        eval_path = self.output_dir / "latest_eval_report.json"
        evaluator.save_report(eval_results, str(eval_path))
        print(f"\n💾 Evaluation report saved: {eval_path}")
        
        print("\n" + "=" * 80)
        print("✅ COMPREHENSIVE TEST SUITE COMPLETE")
        print("=" * 80)
        
        return True
    
    def _get_test_queries(self):
        """
        Targeted query suite specifically designed to cover all 78 documents
        across all 6 categories in the knowledge base.
        """
        return [
            # ── 1. Clinic SLAs (15 Docs) ──────────────────────────
            ("Clinic SLA", "What is the penalty for late delivery to a Platinum clinic past grace period?"),
            ("Clinic SLA", "What is the variable penalty percentage for Independent and Gold tier clinics?"),
            ("Clinic SLA", "What is the receiving window violation protocol when arriving after clinic closing hours?"),
            ("Clinic SLA", "When can a clinic execute an extreme delay order cancellation after 7 days?"),
            ("Clinic SLA", "What is the policy when an expedited rush order fails to deliver in 48 hours?"),
            ("Clinic SLA", "What are the rules for specialty prescription diet stock-out replacement via air courier?"),
            ("Clinic SLA", "What is the minimum shelf-life MHDRZ compliance requirement for short-dated product rejection?"),
            ("Clinic SLA", "When is an environmental exposure quarantine or QA hold required for moisture?"),
            ("Clinic SLA", "What conditions grant a severe meteorological exemption and Act of God penalty waiver?"),
            ("Clinic SLA", "What is the 12-hour advance weather notification mandate to claim Force Majeure?"),
            ("Clinic SLA", "When is a mandatory intermodal mode shift from road to rail enforced during blizzards?"),
            ("Clinic SLA", "How does carrier-at-fault delay liability passthrough work on customer invoices?"),
            ("Clinic SLA", "What is the emergency cross-docking protocol for trailer breakdown temperature integrity?"),
            ("Clinic SLA", "What is the copilot autonomous financial mitigation approval threshold of $500?"),
            ("Clinic SLA", "What is the executive escalation and manual director override protocol via MS Teams?"),

            # ── 2. Vendor Contract Docs (15 Docs) ───────────────────
            ("Vendor Contract", "What is the standard transit delay deduction and carrier performance benchmark?"),
            ("Vendor Contract", "What penalty is charged for carrier origin no-show or tender rejection TONU?"),
            ("Vendor Contract", "What are the consequences for high-value rush freight performance failure?"),
            ("Vendor Contract", "What is carrier reimbursement liability for medical diet stock-out emergency mitigation?"),
            ("Vendor Contract", "What is the mandate for catastrophic breakdown and 24-hour climate cross-docking?"),
            ("Vendor Contract", "What is carrier liability for trailer integrity breach and moisture pest exposure?"),
            ("Vendor Contract", "What are carrier liabilities for short-dated product delay and bio-secure destruction?"),
            ("Vendor Contract", "What are the terms of the severe weather liability waiver and 72-hour Force Majeure?"),
            ("Vendor Contract", "What is the penalty for telematics disconnect and blind-tracking GPS drop >12 hours?"),
            ("Vendor Contract", "What is the weather-mandated mode shift to rail and rate lock integrity rule?"),
            ("Vendor Contract", "What happens during after-hours arrival and carrier redelivery fee assumption?"),
            ("Vendor Contract", "What penalty applies for missing liftgate equipment at independent non-dock clinics?"),
            ("Vendor Contract", "What is carrier liability for dumped unattended freight without POD signature?"),
            ("Vendor Contract", "What are carrier responsibilities for rail yard demurrage and 48-hour free time?"),
            ("Vendor Contract", "What is the AI auto-deduction agreement and 14-day dispute portal timeline?"),

            # ── 3. Packaging & QA Policies (14 Docs) ────────────────
            ("Packaging Policy", "What are the QA rules for thermal degradation when temperatures exceed 100°F?"),
            ("Packaging Policy", "What is the inspection protocol for freezing temperatures and wet canned diet burst risk?"),
            ("Packaging Policy", "When is dry kibble condemned due to trailer leak moisture and mycotoxins?"),
            ("Packaging Policy", "What is the penalty for double-stacking crush damage violating LIPS weight rules?"),
            ("Packaging Policy", "When is black-light pest inspection required for LTL terminal dwell >72 hours?"),
            ("Packaging Policy", "What is the procedure for short-dated expiration breach below MARA shelf life?"),
            ("Packaging Policy", "What actions are mandated when a physical trailer security seal is broken or tampered?"),
            ("Packaging Policy", "How is chemical cross-contamination and solvent odor palatability failure handled?"),
            ("Packaging Policy", "What is the shake-test protocol for kibble pulverization and shock vibration?"),
            ("Packaging Policy", "Why is bottom layer dumped freight automatically condemned for ground exposure?"),
            ("Packaging Policy", "What checks are needed for rapid 40°F temperature swings and internal condensation?"),
            ("Packaging Policy", "How are punctured bags handled during emergency cross-dock forklift damage?"),
            ("Packaging Policy", "What is the bio-security consequence of unapproved transloading and lost custody?"),
            ("Packaging Policy", "What is the lab quarantine release protocol and bio-secure destruction mandate?"),

            # ── 4. History Resolution Logs (15 Docs: Tickets 1-15) ─
            ("History Ticket", "How was Ticket 1 INC-26-001 resolved for medical diet stock-out via emergency air freight?"),
            ("History Ticket", "How was Ticket 2 INC-26-002 handled for blizzard mode shift on I-80 with Swift carrier?"),
            ("History Ticket", "What was the resolution for Ticket 3 INC-26-003 missing liftgate at independent clinic?"),
            ("History Ticket", "How was Ticket 4 INC-26-004 telematics disconnect and $200 blind-tracking penalty applied?"),
            ("History Ticket", "What was the planner action for Ticket 5 INC-26-005 after-hours arrival overnight hold?"),
            ("History Ticket", "How was Ticket 6 INC-26-006 origin no-show and $350 TONU fee billed to carrier?"),
            ("History Ticket", "What was the resolution for Ticket 7 INC-26-007 dumped freight 150% chargeback?"),
            ("History Ticket", "How was Ticket 8 INC-26-008 rail yard demurrage dispute resolved?"),
            ("History Ticket", "What happened in Ticket 9 INC-26-009 short-dated product rejection and destruction?"),
            ("History Ticket", "How was Ticket 10 INC-26-010 hurricane Force Majeure 72-hour waiver verified via API?"),
            ("History Ticket", "What were the planner steps for Ticket 11 INC-26-011 Texas heatwave thermal QA hold?"),
            ("History Ticket", "How was Ticket 12 INC-26-012 broken trailer security seal embargoed?"),
            ("History Ticket", "What was the credit memo action for Ticket 13 INC-26-013 crushed double-stacked pallet?"),
            ("History Ticket", "How was Ticket 14 INC-26-014 rush freight failure zeroed out on carrier invoice?"),
            ("History Ticket", "What lab testing and compliance block occurred in Ticket 15 INC-26-015 chemical odor?"),

            # ── 5. Strike Intelligence Briefs (17 Docs) ─────────────
            ("Strike Intel", "What transportation disruptions and strikes affect freight in Delhi?"),
            ("Strike Intel", "What strike intelligence and route risks are documented for Mumbai?"),
            ("Strike Intel", "What disruption patterns affect railway logistics across India?"),
            ("Strike Intel", "What are the bus strike patterns and transit risks in India?"),
            ("Strike Intel", "What bandh and hartal disruption patterns should be anticipated?"),
            ("Strike Intel", "What strike intelligence exists for Chennai transport corridors?"),
            ("Strike Intel", "What auto rickshaw strike patterns affect local city deliveries?"),
            ("Strike Intel", "What taxi disruption patterns are documented in urban hubs?"),
            ("Strike Intel", "What truck and lorry strike risks affect highway freight?"),
            ("Strike Intel", "What general strike patterns impact supply chain logistics?"),
            ("Strike Intel", "What disruption intelligence is recorded for Bangalore logistics?"),
            ("Strike Intel", "What transportation strike patterns affect Hyderabad freight?"),
            ("Strike Intel", "What strike risks are documented for Kolkata deliveries?"),
            ("Strike Intel", "What disruption patterns affect Pune transport routes?"),
            ("Strike Intel", "What strike intelligence exists for Lucknow logistics corridors?"),
            ("Strike Intel", "What disruption patterns are monitored for Bhubaneswar freight?"),
            ("Strike Intel", "What national-level disruption intelligence guides supply chain rerouting?"),

            # ── 6. Weather Policy Protocols (2 Docs) ─────────────────
            ("Weather Protocol", "What is the Hyderabad severe weather protocol for heat and rain thresholds?"),
            ("Weather Protocol", "What is the Master Severe Weather Protocol for national Force Majeure eligibility?"),
        ]
    
    def _save_test_results(self, results):
        """Save detailed test results to evaluation folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = self.output_dir / f"test_results_{timestamp}.json"
        
        summary = {
            'timestamp': timestamp,
            'total_queries': len(results),
            'avg_confidence': sum(r['confidence'] for r in results) / len(results),
            'categories': {},
            'detailed_results': results
        }
        
        for result in results:
            cat = result['category']
            if cat not in summary['categories']:
                summary['categories'][cat] = {'count': 0, 'avg_confidence': 0, 'confidences': []}
            summary['categories'][cat]['count'] += 1
            summary['categories'][cat]['confidences'].append(result['confidence'])
        
        for cat in summary['categories']:
            confs = summary['categories'][cat]['confidences']
            summary['categories'][cat]['avg_confidence'] = sum(confs) / len(confs)
            del summary['categories'][cat]['confidences']
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Test results saved: {results_path}")
        print("\n📊 TEST SUMMARY BY CATEGORY:")
        for cat, stats in summary['categories'].items():
            print(f"   {cat:<18}: {stats['count']:2d} queries | Avg confidence: {stats['avg_confidence']:.3f}")


def main():
    tester = RAGComprehensiveTest()
    success = tester.run_comprehensive_tests(clear_old_test_data=True)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
