#!/usr/bin/env python3
"""
WSAD Test Script: Risk Table Generator Test
Tests the risk table generator functionality.
"""

import sys
import tempfile
from pathlib import Path
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.risk_table_generator import (
    RiskTableGenerator, RiskItem, RiskAssessment, 
    generate_sample_risk_assessment, generate_risk_assessment
)


def test_risk_table_generator_initialization():
    """Test risk table generator initialization."""
    print("🧪 Testing Risk Table Generator Initialization...")
    
    try:
        generator = RiskTableGenerator()
        assert generator is not None
        assert len(generator.risk_categories) == 5
        
        print("✅ Risk table generator initialized successfully")
        print(f"   Categories: {len(generator.risk_categories)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk table generator initialization failed: {e}")
        return False


def test_risk_categories():
    """Test risk categories."""
    print("🧪 Testing Risk Categories...")
    
    try:
        generator = RiskTableGenerator()
        
        # Test category structure
        for category_name, category in generator.risk_categories.items():
            assert category.name is not None
            assert category.description is not None
            assert 0 <= category.weight <= 1
            assert category.max_score > 0
            assert len(category.criteria) > 0
        
        print("✅ Risk categories structure valid")
        
        # Print categories
        for category_name, category in generator.risk_categories.items():
            print(f"   • {category.name}: {category.weight:.1%} weight")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk categories test failed: {e}")
        return False


def test_risk_score_calculation():
    """Test risk score calculation."""
    print("🧪 Testing Risk Score Calculation...")
    
    try:
        generator = RiskTableGenerator()
        
        # Test score calculation
        test_cases = [
            (1, 1, 1),    # Low impact, low probability
            (3, 3, 9),    # Medium impact, medium probability
            (5, 5, 25),   # High impact, high probability
            (4, 2, 8),    # High impact, low probability
            (2, 4, 8)     # Low impact, high probability
        ]
        
        for impact, probability, expected_score in test_cases:
            score = generator.calculate_risk_score(impact, probability)
            assert score == expected_score, f"Score calculation failed: {impact}×{probability} = {score}, expected {expected_score}"
        
        print("✅ Risk score calculation working")
        
        # Test risk levels
        level_tests = [
            (25, "WYSOKIE"),
            (20, "WYSOKIE"),
            (19, "ŚREDNIE"),
            (10, "ŚREDNIE"),
            (9, "NISKIE"),
            (1, "NISKIE")
        ]
        
        for score, expected_level in level_tests:
            level = generator.get_risk_level(score)
            assert level == expected_level, f"Risk level failed: {score} -> {level}, expected {expected_level}"
        
        print("✅ Risk level classification working")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk score calculation test failed: {e}")
        return False


def test_risk_item_creation():
    """Test risk item creation."""
    print("🧪 Testing Risk Item Creation...")
    
    try:
        # Create sample risk item
        risk_item = RiskItem(
            id="R001",
            category="financial",
            name="Test Risk",
            description="Test risk description",
            impact=4.0,
            probability=3.0,
            controls=["Control 1", "Control 2"],
            mitigation="Test mitigation",
            owner="Test Owner",
            due_date=datetime.now() + timedelta(days=30)
        )
        
        assert risk_item.id == "R001"
        assert risk_item.category == "financial"
        assert risk_item.name == "Test Risk"
        assert risk_item.impact == 4.0
        assert risk_item.probability == 3.0
        assert len(risk_item.controls) == 2
        assert risk_item.owner == "Test Owner"
        assert risk_item.due_date is not None
        
        print("✅ Risk item creation working")
        print(f"   ID: {risk_item.id}")
        print(f"   Name: {risk_item.name}")
        print(f"   Impact: {risk_item.impact}")
        print(f"   Probability: {risk_item.probability}")
        print(f"   Controls: {len(risk_item.controls)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk item creation test failed: {e}")
        return False


def test_risk_assessment_creation():
    """Test risk assessment creation."""
    print("🧪 Testing Risk Assessment Creation...")
    
    try:
        generator = RiskTableGenerator()
        
        # Create sample risk items
        risk_items = [
            RiskItem(
                id="R001",
                category="financial",
                name="Financial Risk 1",
                description="Test financial risk",
                impact=4.0,
                probability=3.0,
                controls=["Control 1"],
                mitigation="Test mitigation",
                owner="Finance Team"
            ),
            RiskItem(
                id="R002",
                category="operational",
                name="Operational Risk 1",
                description="Test operational risk",
                impact=3.0,
                probability=2.0,
                controls=["Control 2"],
                mitigation="Test mitigation 2",
                owner="Operations Team"
            )
        ]
        
        # Create assessment
        assessment = generator.create_risk_assessment(
            company_name="Test Company",
            assessor="Test Assessor",
            period_start=datetime.now() - timedelta(days=365),
            period_end=datetime.now(),
            risk_items=risk_items
        )
        
        assert assessment.company_name == "Test Company"
        assert assessment.assessor == "Test Assessor"
        assert assessment.total_risks == 2
        
        # Calculate expected values
        # R001: 4×3=12 (medium), R002: 3×2=6 (low)
        expected_high = 0
        expected_medium = 1
        expected_low = 1
        
        assert assessment.high_risks == expected_high
        assert assessment.medium_risks == expected_medium
        assert assessment.low_risks == expected_low
        assert assessment.overall_score > 0
        
        print("✅ Risk assessment creation working")
        print(f"   Company: {assessment.company_name}")
        print(f"   Total risks: {assessment.total_risks}")
        print(f"   High risks: {assessment.high_risks}")
        print(f"   Medium risks: {assessment.medium_risks}")
        print(f"   Low risks: {assessment.low_risks}")
        print(f"   Overall score: {assessment.overall_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk assessment creation test failed: {e}")
        return False


def test_sample_risks_generation():
    """Test sample risks generation."""
    print("🧪 Testing Sample Risks Generation...")
    
    try:
        generator = RiskTableGenerator()
        
        # Generate sample risks
        sample_risks = generator.generate_sample_risks("Test Company")
        
        assert len(sample_risks) > 0
        assert all(isinstance(risk, RiskItem) for risk in sample_risks)
        assert all(risk.id for risk in sample_risks)
        assert all(risk.name for risk in sample_risks)
        assert all(risk.category in generator.risk_categories for risk in sample_risks)
        
        print("✅ Sample risks generation working")
        print(f"   Generated {len(sample_risks)} sample risks")
        
        # Print sample risks
        for risk in sample_risks:
            score = generator.calculate_risk_score(risk.impact, risk.probability)
            level = generator.get_risk_level(score)
            print(f"   • {risk.id}: {risk.name} ({level})")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample risks generation test failed: {e}")
        return False


def test_excel_generation():
    """Test Excel workbook generation."""
    print("🧪 Testing Excel Workbook Generation...")
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            output_path = Path(tmp.name)
        
        try:
            # Generate sample risk assessment
            result_path = generate_sample_risk_assessment(
                company_name="Test Company",
                output_path=output_path
            )
            
            assert result_path.exists()
            assert result_path.suffix == '.xlsx'
            assert result_path.stat().st_size > 0
            
            print("✅ Excel workbook generation working")
            print(f"   Generated: {result_path}")
            print(f"   Size: {result_path.stat().st_size} bytes")
            
            return True
            
        finally:
            # Clean up
            if output_path.exists():
                output_path.unlink()
        
    except Exception as e:
        print(f"❌ Excel workbook generation test failed: {e}")
        return False


def test_risk_table_cli_integration():
    """Test risk table CLI integration."""
    print("🧪 Testing Risk Table CLI Integration...")
    
    try:
        from cli.generate_risk_table import GenerateRiskTableCLI
        
        # Test CLI initialization
        cli = GenerateRiskTableCLI()
        assert cli.name == "generate-risk-table"
        
        # Test argument parsing
        test_args = [
            "--data", "test_data.json",
            "--output", "test_output.xlsx",
            "--include-charts",
            "--color-code",
            "--dry-run"
        ]
        
        args = cli.parser.parse_args(test_args)
        assert str(args.data) == "test_data.json"
        assert str(args.output) == "test_output.xlsx"
        assert args.include_charts is True
        assert args.color_code is True
        
        print("✅ Risk table CLI integration working")
        return True
        
    except Exception as e:
        print(f"❌ Risk table CLI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_risk_assessment_formulas():
    """Test risk assessment formulas and calculations."""
    print("🧪 Testing Risk Assessment Formulas...")
    
    try:
        generator = RiskTableGenerator()
        
        # Create test risks with known values
        test_risks = [
            RiskItem(
                id="R001",
                category="financial",
                name="High Risk",
                description="High impact, high probability",
                impact=5.0,
                probability=4.0,
                controls=["Control 1"],
                mitigation="Mitigation 1",
                owner="Owner 1"
            ),
            RiskItem(
                id="R002",
                category="operational",
                name="Medium Risk",
                description="Medium impact, medium probability",
                impact=3.0,
                probability=3.0,
                controls=["Control 2"],
                mitigation="Mitigation 2",
                owner="Owner 2"
            ),
            RiskItem(
                id="R003",
                category="compliance",
                name="Low Risk",
                description="Low impact, low probability",
                impact=2.0,
                probability=2.0,
                controls=["Control 3"],
                mitigation="Mitigation 3",
                owner="Owner 3"
            )
        ]
        
        # Create assessment
        assessment = generator.create_risk_assessment(
            company_name="Formula Test Company",
            assessor="Formula Test Assessor",
            period_start=datetime.now() - timedelta(days=365),
            period_end=datetime.now(),
            risk_items=test_risks
        )
        
        # Verify calculations
        expected_scores = [20.0, 9.0, 4.0]  # 5×4, 3×3, 2×2
        expected_levels = ["WYSOKIE", "NISKIE", "NISKIE"]
        expected_high = 1
        expected_medium = 0
        expected_low = 2
        expected_overall = (20.0 + 9.0 + 4.0) / 3  # 11.0
        
        assert assessment.total_risks == 3
        assert assessment.high_risks == expected_high
        assert assessment.medium_risks == expected_medium
        assert assessment.low_risks == expected_low
        assert abs(assessment.overall_score - expected_overall) < 0.01
        
        print("✅ Risk assessment formulas working")
        print(f"   Expected overall score: {expected_overall}")
        print(f"   Actual overall score: {assessment.overall_score}")
        print(f"   High risks: {assessment.high_risks} (expected: {expected_high})")
        print(f"   Medium risks: {assessment.medium_risks} (expected: {expected_medium})")
        print(f"   Low risks: {assessment.low_risks} (expected: {expected_low})")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk assessment formulas test failed: {e}")
        return False


def main():
    """Run all risk table generator tests."""
    print("🚀 Starting Risk Table Generator Test Suite...")
    print("=" * 60)
    
    tests = [
        test_risk_table_generator_initialization,
        test_risk_categories,
        test_risk_score_calculation,
        test_risk_item_creation,
        test_risk_assessment_creation,
        test_sample_risks_generation,
        test_excel_generation,
        test_risk_table_cli_integration,
        test_risk_assessment_formulas
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Risk Table Generator Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All risk table generator tests passed!")
        return 0
    else:
        print("❌ Some risk table generator tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
