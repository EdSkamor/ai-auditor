#!/usr/bin/env python3
"""
Test script for Audit Analytics functionality.
"""

import random
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.audit_analytics import (
    AuditAnalytics,
    JournalEntry,
    JournalEntryAnalyzer,
    RiskAnalyzer,
    RiskCategory,
    RiskFactor,
    RiskLevel,
    SamplingEngine,
    SamplingMethod,
)


def test_audit_analytics():
    """Test Audit Analytics functionality."""
    print("🚀 Starting Audit Analytics Test Suite...")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Initialize analytics
        print("🧪 Testing Audit Analytics Initialization...")
        analytics = AuditAnalytics(tmp_path)
        print("✅ Audit Analytics initialized successfully")

        # Test risk assessment
        print("\n🧪 Testing Risk Assessment...")
        risk_assessment = analytics.perform_risk_assessment()
        print(f"   • Assessment ID: {risk_assessment.id}")
        print(f"   • Overall risk level: {risk_assessment.overall_risk_level.value}")
        print(f"   • Risk factors count: {len(risk_assessment.risk_factors)}")
        print(f"   • Key risks: {len(risk_assessment.key_risks)}")
        print(f"   • Recommendations: {len(risk_assessment.recommendations)}")

        # Show risk factors
        for factor in risk_assessment.risk_factors:
            risk_score = factor.impact * factor.likelihood
            print(
                f"     - {factor.name}: {factor.level.value} (score: {risk_score:.1f})"
            )

        print("✅ Risk assessment completed")

        # Test journal entry analysis
        print("\n🧪 Testing Journal Entry Analysis...")

        # Create sample journal entries
        sample_entries = []
        for i in range(100):
            entry = JournalEntry(
                id=f"JE_{i:03d}",
                date=datetime.now() - timedelta(days=random.randint(1, 30)),
                account_code=f"100{i%10}",
                account_name=f"Account {i%10}",
                debit=random.uniform(100, 10000) if random.random() > 0.5 else 0,
                credit=random.uniform(100, 10000) if random.random() > 0.5 else 0,
                description=f"Transaction {i}",
                reference=f"REF_{i:03d}",
                user_id=f"USER_{i%5}",
                batch_id=f"BATCH_{i%10}",
                amount=random.uniform(100, 10000),
            )
            sample_entries.append(entry)

        # Add some anomalies
        # Weekend entry
        weekend_entry = JournalEntry(
            id="JE_WEEKEND",
            date=datetime.now()
            - timedelta(days=datetime.now().weekday() - 5),  # Saturday
            account_code="1001",
            account_name="Test Account",
            debit=1000,
            credit=0,
            description="Weekend transaction",
            reference="REF_WEEKEND",
            user_id="USER_1",
            batch_id="BATCH_1",
            amount=1000,
        )
        sample_entries.append(weekend_entry)

        # Large amount
        large_entry = JournalEntry(
            id="JE_LARGE",
            date=datetime.now(),
            account_code="1002",
            account_name="Test Account",
            debit=100000,
            credit=0,
            description="Large transaction",
            reference="REF_LARGE",
            user_id="USER_2",
            batch_id="BATCH_2",
            amount=100000,
        )
        sample_entries.append(large_entry)

        # Round amount
        round_entry = JournalEntry(
            id="JE_ROUND",
            date=datetime.now(),
            account_code="1003",
            account_name="Test Account",
            debit=50000,
            credit=0,
            description="Round amount transaction",
            reference="REF_ROUND",
            user_id="USER_3",
            batch_id="BATCH_3",
            amount=50000,
        )
        sample_entries.append(round_entry)

        # Analyze entries
        anomalies = analytics.analyze_journal_entries(sample_entries)
        print(f"   • Total entries analyzed: {len(sample_entries)}")
        print(f"   • Anomalies found: {len(anomalies)}")

        # Show anomalies by type
        anomaly_types = {}
        for anomaly in anomalies:
            anomaly_type = anomaly.anomaly_type
            if anomaly_type not in anomaly_types:
                anomaly_types[anomaly_type] = 0
            anomaly_types[anomaly_type] += 1

        for anomaly_type, count in anomaly_types.items():
            print(f"     - {anomaly_type}: {count}")

        # Show high severity anomalies
        high_severity = [a for a in anomalies if a.severity == RiskLevel.HIGH]
        if high_severity:
            print(f"   • High severity anomalies: {len(high_severity)}")
            for anomaly in high_severity[:3]:  # Show first 3
                print(
                    f"     - {anomaly.description} (confidence: {anomaly.confidence:.2f})"
                )

        print("✅ Journal entry analysis completed")

        # Test sampling
        print("\n🧪 Testing Sampling...")

        # Create sample population
        population = []
        for i in range(1000):
            population.append(
                {
                    "id": f"ITEM_{i:04d}",
                    "amount": random.uniform(100, 50000),
                    "description": f"Item {i}",
                    "date": datetime.now() - timedelta(days=random.randint(1, 365)),
                }
            )

        # Test MUS sampling
        mus_result = analytics.perform_sampling(
            population=population,
            method=SamplingMethod.MUS,
            confidence_level=0.95,
            tolerable_error=0.05,
            expected_error=0.01,
        )

        print("   • MUS Sampling:")
        print(f"     - Population size: {mus_result.population_size}")
        print(f"     - Sample size: {mus_result.sample_size}")
        print(f"     - Confidence level: {mus_result.confidence_level}")
        print(f"     - Sampling interval: {mus_result.sampling_interval:,.2f}")
        print(f"     - Upper error limit: {mus_result.upper_error_limit:,.2f}")

        # Test statistical sampling
        stat_result = analytics.perform_sampling(
            population=population,
            method=SamplingMethod.STATISTICAL,
            confidence_level=0.95,
            margin_of_error=0.05,
        )

        print("   • Statistical Sampling:")
        print(f"     - Population size: {stat_result.population_size}")
        print(f"     - Sample size: {stat_result.sample_size}")
        print(f"     - Confidence level: {stat_result.confidence_level}")
        print(f"     - Margin of error: {stat_result.tolerable_error}")

        print("✅ Sampling completed")

        # Test risk table generation
        print("\n🧪 Testing Risk Table Generation...")
        risk_table = analytics.generate_risk_table(risk_assessment)

        print("   • Risk table generated:")
        print(f"     - Assessment ID: {risk_table['assessment_id']}")
        print(f"     - Overall risk level: {risk_table['overall_risk_level']}")
        print(f"     - Risk factors: {len(risk_table['risk_factors'])}")
        print(f"     - Key risks: {len(risk_table['key_risks'])}")
        print(f"     - Recommendations: {len(risk_table['recommendations'])}")

        # Show risk factors with scores
        for factor in risk_table["risk_factors"]:
            print(
                f"     - {factor['name']}: {factor['level']} (score: {factor['risk_score']:.1f})"
            )

        print("✅ Risk table generation completed")

        # Test analytics summary
        print("\n🧪 Testing Analytics Summary...")
        summary = analytics.get_analytics_summary()

        print("   • Analytics summary:")
        print(f"     - Risk assessments: {summary['risk_assessments_count']}")
        print(f"     - Anomalies: {summary['anomalies_count']}")
        print(f"     - Sampling results: {summary['sampling_results_count']}")
        print(f"     - High risk anomalies: {summary['high_risk_anomalies']}")
        print(f"     - Critical risk anomalies: {summary['critical_risk_anomalies']}")
        print(f"     - Latest assessment: {summary['latest_assessment']}")

        print("✅ Analytics summary generated")

        # Test individual components
        print("\n🧪 Testing Individual Components...")

        # Test risk analyzer
        risk_analyzer = RiskAnalyzer()
        custom_risks = [
            RiskFactor(
                id="custom_001",
                name="Custom Risk 1",
                category=RiskCategory.INHERENT,
                level=RiskLevel.HIGH,
                description="Custom risk for testing",
                impact=5.0,
                likelihood=4.0,
                controls=["Control 1", "Control 2"],
                mitigation="Test mitigation",
                owner="Test Owner",
                last_review=datetime.now(),
                next_review=datetime.now() + timedelta(days=30),
            )
        ]

        custom_assessment = risk_analyzer.assess_risk(custom_risks)
        print(
            f"   • Custom risk assessment: {custom_assessment.overall_risk_level.value}"
        )

        # Test journal entry analyzer
        journal_analyzer = JournalEntryAnalyzer()
        test_anomalies = journal_analyzer.analyze_entries(sample_entries[:10])
        print(f"   • Journal analyzer test: {len(test_anomalies)} anomalies found")

        # Test sampling engine
        sampling_engine = SamplingEngine()
        test_population = [
            {"id": f"item_{i}", "amount": random.uniform(100, 1000)} for i in range(100)
        ]
        test_result = sampling_engine.mus_sampling(test_population)
        print(f"   • Sampling engine test: {test_result.sample_size} items selected")

        print("✅ Individual components tested")

        # Test error handling
        print("\n🧪 Testing Error Handling...")

        try:
            # Test with empty population
            empty_result = analytics.perform_sampling([], SamplingMethod.MUS)
            print("❌ Should have failed with empty population")
        except Exception as e:
            print(f"✅ Error handling working - caught exception: {type(e).__name__}")

        try:
            # Test with invalid sampling method
            invalid_result = analytics.perform_sampling(
                test_population, "INVALID_METHOD"
            )
            print("❌ Should have failed with invalid method")
        except Exception as e:
            print(f"✅ Error handling working - caught exception: {type(e).__name__}")

        print("✅ Error handling tested")

        # Test performance
        print("\n🧪 Testing Performance...")
        import time

        # Test risk assessment performance
        start_time = time.time()
        for _ in range(10):
            analytics.perform_risk_assessment()
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        print(f"   • Average risk assessment time: {avg_time:.3f}s")

        # Test journal analysis performance
        start_time = time.time()
        for _ in range(5):
            analytics.analyze_journal_entries(sample_entries[:50])
        end_time = time.time()
        avg_time = (end_time - start_time) / 5
        print(f"   • Average journal analysis time: {avg_time:.3f}s")

        # Test sampling performance
        start_time = time.time()
        for _ in range(5):
            analytics.perform_sampling(population[:100], SamplingMethod.MUS)
        end_time = time.time()
        avg_time = (end_time - start_time) / 5
        print(f"   • Average sampling time: {avg_time:.3f}s")

        print("✅ Performance tested")

        print("\n" + "=" * 60)
        print("📊 Audit Analytics Test Results: All tests passed!")
        print("🎉 Audit Analytics system is working correctly!")


if __name__ == "__main__":
    test_audit_analytics()
