"""RAG Evaluation Module for O2C India Transport Strike Monitor

Provides comprehensive evaluation metrics for RAG system performance:
- Retrieval quality (confidence scores, source diversity)
- Question pattern analysis
- Consistency checks
- Document coverage
- Performance grading

Usage:
    from modules.rag_evaluator import RAGEvaluator
    
    evaluator = RAGEvaluator(db_path)
    metrics = evaluator.evaluate()
    evaluator.print_report(metrics)
    evaluator.save_report(metrics, output_path)
"""

import sqlite3
import pandas as pd
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import os


class RAGEvaluator:
    """Evaluates RAG system performance using production data"""
    
    def __init__(self, db_path: str, total_docs_in_corpus: int = 78):
        """Initialize evaluator
        
        Args:
            db_path: Path to SQLite database with rag_analyses table
            total_docs_in_corpus: Total number of documents in RAG corpus (78 docs across 6 categories)
        """
        self.db_path = str(db_path)
        self.total_docs = total_docs_in_corpus
        
    def load_data(self) -> pd.DataFrame:
        """Load RAG analyses from database"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM rag_analyses", conn)
        conn.close()
        return df
    
    def parse_sources(self, rag_df: pd.DataFrame) -> pd.DataFrame:
        """Parse sources JSON into structured dataframe"""
        source_data = []
        for _, row in rag_df.iterrows():
            try:
                sources = json.loads(row['sources'])
                for s in sources:
                    source_data.append({
                        'analysis_id': row['analysis_id'],
                        'question': row['question'],
                        'filename': s.get('filename', 'unknown'),
                        'category': s.get('category', 'unknown'),
                        'similarity': s.get('similarity', 0),
                        'chunk_id': s.get('chunk_id', 'unknown')
                    })
            except Exception as e:
                continue
        return pd.DataFrame(source_data)
    
    def calculate_retrieval_metrics(self, rag_df: pd.DataFrame, source_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate retrieval quality metrics"""
        metrics = {}
        
        # Confidence score statistics
        metrics['confidence'] = {
            'mean': float(rag_df['confidence'].mean()),
            'median': float(rag_df['confidence'].median()),
            'std': float(rag_df['confidence'].std()),
            'min': float(rag_df['confidence'].min()),
            'max': float(rag_df['confidence'].max()),
            'percentiles': {
                int(p): float(np.percentile(rag_df['confidence'], p))
                for p in [10, 25, 50, 75, 90, 95, 99]
            }
        }
        
        # Sources per query
        sources_per_query = source_df.groupby('analysis_id').size()
        metrics['sources_per_query'] = {
            'mean': float(sources_per_query.mean()),
            'median': float(sources_per_query.median()),
            'mode': float(sources_per_query.mode()[0]) if len(sources_per_query.mode()) > 0 else 5
        }
        
        # Document diversity
        unique_docs = source_df['filename'].nunique()
        metrics['document_diversity'] = {
            'unique_docs_retrieved': int(unique_docs),
            'total_docs_in_corpus': int(self.total_docs),
            'coverage_percentage': float(unique_docs / self.total_docs * 100),
            'top_docs': source_df['filename'].value_counts().head(10).to_dict()
        }
        
        # Category distribution
        metrics['category_distribution'] = source_df['category'].value_counts().to_dict()
        
        return metrics
    
    def calculate_question_metrics(self, rag_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze question patterns"""
        questions = rag_df['question'].value_counts()
        return {
            'total_unique_questions': int(len(questions)),
            'total_analyses': int(len(rag_df)),
            'top_questions': questions.head(5).to_dict()
        }
    
    def calculate_consistency_metrics(self, rag_df: pd.DataFrame, source_df: pd.DataFrame) -> Dict[str, Any]:
        """Check retrieval consistency for same questions"""
        questions = rag_df['question'].value_counts()
        consistency_results = []
        
        for question in questions.head(3).index:
            q_analyses = rag_df[rag_df['question'] == question]
            q_sources = source_df[source_df['analysis_id'].isin(q_analyses['analysis_id'])]
            
            top_docs_per_analysis = []
            for aid in q_analyses['analysis_id']:
                aid_sources = q_sources[q_sources['analysis_id'] == aid]
                if len(aid_sources) > 0:
                    top_docs_per_analysis.append(aid_sources.iloc[0]['filename'])
            
            if len(top_docs_per_analysis) > 0:
                most_common_top = pd.Series(top_docs_per_analysis).value_counts().iloc[0]
                consistency = most_common_top / len(top_docs_per_analysis) * 100
                consistency_results.append({
                    'question': question,
                    'times_asked': int(len(q_analyses)),
                    'consistency_percentage': float(consistency)
                })
        
        return {'consistency_checks': consistency_results}
    
    def calculate_quality_grade(self, rag_df: pd.DataFrame, coverage_pct: float) -> Dict[str, Any]:
        """Calculate overall quality assessment"""
        high_conf = int((rag_df['confidence'] >= 0.45).sum())
        med_conf = int(((rag_df['confidence'] >= 0.40) & (rag_df['confidence'] < 0.45)).sum())
        low_conf = int((rag_df['confidence'] < 0.40).sum())
        total = len(rag_df)
        
        # Determine grade
        avg_conf = rag_df['confidence'].mean()
        if avg_conf >= 0.45 and coverage_pct >= 60:
            grade = "A (Excellent)"
        elif avg_conf >= 0.40 and coverage_pct >= 50:
            grade = "B (Good)"
        elif avg_conf >= 0.35:
            grade = "C (Fair)"
        else:
            grade = "D (Needs Improvement)"
        
        return {
            'confidence_distribution': {
                'high': {'count': high_conf, 'percentage': high_conf/total*100},
                'medium': {'count': med_conf, 'percentage': med_conf/total*100},
                'low': {'count': low_conf, 'percentage': low_conf/total*100}
            },
            'overall_grade': grade,
            'avg_confidence': float(avg_conf),
            'coverage_percentage': float(coverage_pct)
        }
    
    def generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        avg_conf = metrics['quality']['avg_confidence']
        coverage = metrics['quality']['coverage_percentage']
        unique_docs = metrics['retrieval']['document_diversity']['unique_docs_retrieved']
        
        if avg_conf < 0.45:
            recommendations.append({
                'severity': 'warning',
                'issue': 'LOW CONFIDENCE',
                'description': f"Average similarity {avg_conf:.3f} suggests chunking strategy needs tuning",
                'actions': [
                    "Try smaller chunks (300 chars) or larger chunks (800 chars)",
                    "Experiment with overlap (current: 50, try: 100 or 150)",
                    "Consider semantic chunking based on sentence boundaries"
                ]
            })
        
        if coverage < 60:
            recommendations.append({
                'severity': 'critical',
                'issue': 'LOW COVERAGE',
                'description': f"Only {unique_docs}/{self.total_docs} documents being retrieved ({coverage:.1f}%)",
                'actions': [
                    "Audit unused documents - are they relevant to queries?",
                    "Check document preprocessing and chunking",
                    "Verify embeddings are generated for all documents",
                    "Review if corpus contains irrelevant documents"
                ]
            })
        
        if not recommendations:
            recommendations.append({
                'severity': 'info',
                'issue': 'SYSTEM PERFORMING WELL',
                'description': 'Consider these enhancements',
                'actions': [
                    "Add reranking layer for top-1 accuracy improvement",
                    "Implement hybrid search (BM25 + vector) for better recall",
                    "Add LLM generation for natural language answers",
                    "Set up automated evaluation tracking"
                ]
            })
        
        return recommendations
    
    def evaluate(self) -> Dict[str, Any]:
        """Run complete evaluation and return metrics"""
        # Load data
        rag_df = self.load_data()
        source_df = self.parse_sources(rag_df)
        
        # Calculate all metrics
        retrieval_metrics = self.calculate_retrieval_metrics(rag_df, source_df)
        question_metrics = self.calculate_question_metrics(rag_df)
        consistency_metrics = self.calculate_consistency_metrics(rag_df, source_df)
        
        coverage_pct = retrieval_metrics['document_diversity']['coverage_percentage']
        quality_metrics = self.calculate_quality_grade(rag_df, coverage_pct)
        
        # Generate recommendations
        recommendations = self.generate_recommendations({
            'retrieval': retrieval_metrics,
            'quality': quality_metrics
        })
        
        # Compile full report
        return {
            'metadata': {
                'evaluation_date': datetime.now().isoformat(),
                'total_analyses': int(len(rag_df)),
                'date_range': {
                    'start': str(rag_df['analyzed_at'].min()),
                    'end': str(rag_df['analyzed_at'].max())
                }
            },
            'retrieval': retrieval_metrics,
            'questions': question_metrics,
            'consistency': consistency_metrics,
            'quality': quality_metrics,
            'recommendations': recommendations
        }
    
    def print_report(self, metrics: Dict[str, Any]):
        """Print formatted evaluation report"""
        print("=" * 100)
        print("🎯 RAG EVALUATION REPORT - O2C INDIA TRANSPORT STRIKE MONITOR")
        print("=" * 100)
        print(f"Evaluation Date: {metrics['metadata']['evaluation_date']}")
        print(f"Total Analyses: {metrics['metadata']['total_analyses']}")
        print(f"Date Range: {metrics['metadata']['date_range']['start']} to {metrics['metadata']['date_range']['end']}")
        
        # Retrieval quality
        print("\n" + "=" * 100)
        print("1️⃣  RETRIEVAL QUALITY")
        print("=" * 100)
        conf = metrics['retrieval']['confidence']
        print(f"\nConfidence Scores: Mean={conf['mean']:.4f} | Median={conf['median']:.4f} | Std={conf['std']:.4f}")
        print(f"Range: [{conf['min']:.4f}, {conf['max']:.4f}]")
        
        div = metrics['retrieval']['document_diversity']
        print(f"\nDocument Coverage: {div['unique_docs_retrieved']}/{div['total_docs_in_corpus']} ({div['coverage_percentage']:.1f}%)")
        
        # Quality grade
        print("\n" + "=" * 100)
        print("2️⃣  OVERALL QUALITY")
        print("=" * 100)
        qual = metrics['quality']
        print(f"\n🏆 GRADE: {qual['overall_grade']}")
        print(f"   Average Confidence: {qual['avg_confidence']:.3f}")
        print(f"   Document Coverage: {qual['coverage_percentage']:.1f}%")
        
        conf_dist = qual['confidence_distribution']
        print(f"\n   High confidence (≥0.45): {conf_dist['high']['count']} ({conf_dist['high']['percentage']:.1f}%)")
        print(f"   Med confidence (0.40-0.45): {conf_dist['medium']['count']} ({conf_dist['medium']['percentage']:.1f}%)")
        print(f"   Low confidence (<0.40): {conf_dist['low']['count']} ({conf_dist['low']['percentage']:.1f}%)")
        
        # Recommendations
        print("\n" + "=" * 100)
        print("3️⃣  RECOMMENDATIONS")
        print("=" * 100)
        for rec in metrics['recommendations']:
            severity_icon = {'critical': '🔴', 'warning': '⚠️', 'info': 'ℹ️'}
            print(f"\n{severity_icon[rec['severity']]} {rec['issue']}")
            print(f"   {rec['description']}")
            for action in rec['actions']:
                print(f"   → {action}")
        
        print("\n" + "=" * 100)
    
    def save_report(self, metrics: Dict[str, Any], output_path: str):
        """Save metrics to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"\n✅ Evaluation report saved to: {output_path}")


if __name__ == "__main__":
    import os
    from pathlib import Path
    
    # Databricks workspace path
    DATABRICKS_PATH = Path("/Workspace/Users/ayyash.a@tcs.com/O2C_AI")
    if DATABRICKS_PATH.exists() or "DATABRICKS_RUNTIME_VERSION" in os.environ:
        db_path = str(DATABRICKS_PATH / "india_monitor_data" / "database" / "india_monitor.db")
        output_path = str(DATABRICKS_PATH / "evaluation" / "latest_eval_report.json")
    else:
        try:
            from .config import DB_PATH, BASE_DIR
        except ImportError:
            from config import DB_PATH, BASE_DIR
        db_path = str(DB_PATH)
        output_path = str(Path(BASE_DIR).parent / "evaluation" / "latest_eval_report.json")

    evaluator = RAGEvaluator(db_path=db_path, total_docs_in_corpus=78)
    
    print("Running RAG evaluation...\n")
    metrics = evaluator.evaluate()
    evaluator.print_report(metrics)
    evaluator.save_report(metrics, output_path)
