"""
Production Risk Table Generator for AI Auditor.
Generates complex Excel risk workbooks with formulas and calculations.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

try:
    import pandas as pd
    import xlsxwriter
    from xlsxwriter.utility import xl_rowcol_to_cell
    HAS_EXCEL = True
except ImportError:
    HAS_EXCEL = False
    # Mock xlsxwriter for type hints
    class MockXlsxWriter:
        class Workbook:
            pass
        class utility:
            def xl_rowcol_to_cell(self, row, col):
                pass
    xlsxwriter = MockXlsxWriter()

from .exceptions import FileProcessingError, ValidationError


@dataclass
class RiskCategory:
    """Risk category definition."""
    name: str
    description: str
    weight: float
    max_score: float
    criteria: List[Dict[str, Any]]


@dataclass
class RiskItem:
    """Individual risk item."""
    id: str
    category: str
    name: str
    description: str
    impact: float  # 1-5 scale
    probability: float  # 1-5 scale
    controls: List[str]
    mitigation: str
    owner: str
    due_date: Optional[datetime] = None


@dataclass
class RiskAssessment:
    """Complete risk assessment."""
    company_name: str
    assessment_date: datetime
    assessor: str
    period_start: datetime
    period_end: datetime
    total_risks: int
    high_risks: int
    medium_risks: int
    low_risks: int
    overall_score: float
    risk_items: List[RiskItem]


class RiskTableGenerator:
    """Production risk table generator with Excel formulas."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Risk categories with Polish descriptions
        self.risk_categories = {
            'financial': RiskCategory(
                name="Ryzyko Finansowe",
                description="Ryzyka związane z finansami i płynnością",
                weight=0.3,
                max_score=100,
                criteria=[
                    {"name": "Płynność finansowa", "weight": 0.4},
                    {"name": "Zadłużenie", "weight": 0.3},
                    {"name": "Rentowność", "weight": 0.3}
                ]
            ),
            'operational': RiskCategory(
                name="Ryzyko Operacyjne",
                description="Ryzyka związane z działalnością operacyjną",
                weight=0.25,
                max_score=100,
                criteria=[
                    {"name": "Procesy biznesowe", "weight": 0.4},
                    {"name": "Zasoby ludzkie", "weight": 0.3},
                    {"name": "Technologia", "weight": 0.3}
                ]
            ),
            'compliance': RiskCategory(
                name="Ryzyko Zgodności",
                description="Ryzyka związane z zgodnością z przepisami",
                weight=0.2,
                max_score=100,
                criteria=[
                    {"name": "Zgodność podatkowa", "weight": 0.4},
                    {"name": "Zgodność z KRS", "weight": 0.3},
                    {"name": "Zgodność z VAT", "weight": 0.3}
                ]
            ),
            'market': RiskCategory(
                name="Ryzyko Rynkowe",
                description="Ryzyka związane z rynkiem i konkurencją",
                weight= 0.15,
                max_score=100,
                criteria=[
                    {"name": "Konkurencja", "weight": 0.4},
                    {"name": "Zmiany rynkowe", "weight": 0.3},
                    {"name": "Klienci", "weight": 0.3}
                ]
            ),
            'reputation': RiskCategory(
                name="Ryzyko Reputacji",
                description="Ryzyka związane z reputacją firmy",
                weight=0.1,
                max_score=100,
                criteria=[
                    {"name": "Wizerunek publiczny", "weight": 0.5},
                    {"name": "Relacje z klientami", "weight": 0.5}
                ]
            )
        }
    
    def calculate_risk_score(self, impact: float, probability: float) -> float:
        """Calculate risk score from impact and probability."""
        return impact * probability
    
    def get_risk_level(self, score: float) -> str:
        """Get risk level based on score."""
        if score >= 20:
            return "WYSOKIE"
        elif score >= 10:
            return "ŚREDNIE"
        else:
            return "NISKIE"
    
    def get_risk_color(self, level: str) -> str:
        """Get color code for risk level."""
        colors = {
            "WYSOKIE": "#FF6B6B",  # Red
            "ŚREDNIE": "#FFE66D",  # Yellow
            "NISKIE": "#4ECDC4"    # Green
        }
        return colors.get(level, "#CCCCCC")
    
    def create_risk_assessment(self, 
                             company_name: str,
                             assessor: str,
                             period_start: datetime,
                             period_end: datetime,
                             risk_items: List[RiskItem]) -> RiskAssessment:
        """Create a complete risk assessment."""
        
        # Calculate statistics
        total_risks = len(risk_items)
        high_risks = len([r for r in risk_items if self.get_risk_level(self.calculate_risk_score(r.impact, r.probability)) == "WYSOKIE"])
        medium_risks = len([r for r in risk_items if self.get_risk_level(self.calculate_risk_score(r.impact, r.probability)) == "ŚREDNIE"])
        low_risks = len([r for r in risk_items if self.get_risk_level(self.calculate_risk_score(r.impact, r.probability)) == "NISKIE"])
        
        # Calculate overall score
        if total_risks > 0:
            total_score = sum(self.calculate_risk_score(r.impact, r.probability) for r in risk_items)
            overall_score = total_score / total_risks
        else:
            overall_score = 0.0
        
        return RiskAssessment(
            company_name=company_name,
            assessment_date=datetime.now(),
            assessor=assessor,
            period_start=period_start,
            period_end=period_end,
            total_risks=total_risks,
            high_risks=high_risks,
            medium_risks=medium_risks,
            low_risks=low_risks,
            overall_score=overall_score,
            risk_items=risk_items
        )
    
    def generate_excel_workbook(self, 
                              assessment: RiskAssessment, 
                              output_path: Path) -> Path:
        """Generate Excel workbook with risk tables and formulas."""
        
        if not HAS_EXCEL:
            raise FileProcessingError("Excel libraries not available")
        
        try:
            # Create workbook
            workbook = xlsxwriter.Workbook(str(output_path))
            
            # Define formats
            formats = self._create_formats(workbook)
            
            # Create worksheets
            self._create_summary_sheet(workbook, assessment, formats)
            self._create_risk_matrix_sheet(workbook, assessment, formats)
            self._create_detailed_risks_sheet(workbook, assessment, formats)
            self._create_categories_sheet(workbook, assessment, formats)
            self._create_mitigation_plan_sheet(workbook, assessment, formats)
            self._create_assumptions_sheet(workbook, assessment, formats)
            
            # Close workbook
            workbook.close()
            
            self.logger.info(f"Risk assessment workbook created: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to create Excel workbook: {e}")
            raise FileProcessingError(f"Excel workbook creation failed: {e}")
    
    def _create_formats(self, workbook: xlsxwriter.Workbook) -> Dict[str, Any]:
        """Create Excel formats."""
        return {
            'header': workbook.add_format({
                'bold': True,
                'font_size': 14,
                'bg_color': '#1f4e79',
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            }),
            'subheader': workbook.add_format({
                'bold': True,
                'font_size': 12,
                'bg_color': '#2e6da4',
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            }),
            'high_risk': workbook.add_format({
                'bg_color': '#FF6B6B',
                'font_color': 'white',
                'bold': True,
                'align': 'center',
                'border': 1
            }),
            'medium_risk': workbook.add_format({
                'bg_color': '#FFE66D',
                'font_color': 'black',
                'bold': True,
                'align': 'center',
                'border': 1
            }),
            'low_risk': workbook.add_format({
                'bg_color': '#4ECDC4',
                'font_color': 'white',
                'bold': True,
                'align': 'center',
                'border': 1
            }),
            'border': workbook.add_format({'border': 1}),
            'bold': workbook.add_format({'bold': True}),
            'number': workbook.add_format({'num_format': '0.00', 'border': 1}),
            'percent': workbook.add_format({'num_format': '0.00%', 'border': 1}),
            'date': workbook.add_format({'num_format': 'dd/mm/yyyy', 'border': 1})
        }
    
    def _create_summary_sheet(self, 
                            workbook: xlsxwriter.Workbook, 
                            assessment: RiskAssessment, 
                            formats: Dict[str, Any]):
        """Create summary sheet."""
        worksheet = workbook.add_worksheet('Podsumowanie')
        
        # Title
        worksheet.merge_range('A1:H1', 'RAPORT OCENY RYZYKA', formats['header'])
        
        # Company info
        row = 3
        worksheet.write(f'A{row}', 'Nazwa firmy:', formats['bold'])
        worksheet.write(f'B{row}', assessment.company_name, formats['border'])
        row += 1
        
        worksheet.write(f'A{row}', 'Data oceny:', formats['bold'])
        worksheet.write(f'B{row}', assessment.assessment_date, formats['date'])
        row += 1
        
        worksheet.write(f'A{row}', 'Oceniający:', formats['bold'])
        worksheet.write(f'B{row}', assessment.assessor, formats['border'])
        row += 1
        
        worksheet.write(f'A{row}', 'Okres:', formats['bold'])
        worksheet.write(f'B{row}', f"{assessment.period_start.strftime('%d.%m.%Y')} - {assessment.period_end.strftime('%d.%m.%Y')}", formats['border'])
        row += 2
        
        # Risk summary
        worksheet.merge_range(f'A{row}:H{row}', 'PODSUMOWANIE RYZYK', formats['subheader'])
        row += 1
        
        # Risk statistics
        worksheet.write(f'A{row}', 'Całkowita liczba ryzyk:', formats['bold'])
        worksheet.write(f'B{row}', assessment.total_risks, formats['number'])
        row += 1
        
        worksheet.write(f'A{row}', 'Ryzyka wysokie:', formats['bold'])
        worksheet.write(f'B{row}', assessment.high_risks, formats['high_risk'])
        row += 1
        
        worksheet.write(f'A{row}', 'Ryzyka średnie:', formats['bold'])
        worksheet.write(f'B{row}', assessment.medium_risks, formats['medium_risk'])
        row += 1
        
        worksheet.write(f'A{row}', 'Ryzyka niskie:', formats['bold'])
        worksheet.write(f'B{row}', assessment.low_risks, formats['low_risk'])
        row += 1
        
        worksheet.write(f'A{row}', 'Średni wynik ryzyka:', formats['bold'])
        worksheet.write(f'B{row}', assessment.overall_score, formats['number'])
        row += 2
        
        # Risk distribution chart data
        worksheet.write(f'A{row}', 'Kategoria', formats['bold'])
        worksheet.write(f'B{row}', 'Liczba ryzyk', formats['bold'])
        worksheet.write(f'C{row}', 'Średni wynik', formats['bold'])
        row += 1
        
        for category_name, category in self.risk_categories.items():
            category_risks = [r for r in assessment.risk_items if r.category == category_name]
            if category_risks:
                avg_score = sum(self.calculate_risk_score(r.impact, r.probability) for r in category_risks) / len(category_risks)
                worksheet.write(f'A{row}', category.name, formats['border'])
                worksheet.write(f'B{row}', len(category_risks), formats['number'])
                worksheet.write(f'C{row}', avg_score, formats['number'])
            else:
                worksheet.write(f'A{row}', category.name, formats['border'])
                worksheet.write(f'B{row}', 0, formats['number'])
                worksheet.write(f'C{row}', 0, formats['number'])
            row += 1
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
    
    def _create_risk_matrix_sheet(self, 
                                workbook: xlsxwriter.Workbook, 
                                assessment: RiskAssessment, 
                                formats: Dict[str, Any]):
        """Create risk matrix sheet."""
        worksheet = workbook.add_worksheet('Macierz Ryzyka')
        
        # Title
        worksheet.merge_range('A1:F1', 'MACIERZ RYZYKA', formats['header'])
        
        # Matrix header
        row = 3
        worksheet.write(f'A{row}', 'Ryzyko', formats['subheader'])
        worksheet.write(f'B{row}', 'Kategoria', formats['subheader'])
        worksheet.write(f'C{row}', 'Wpływ', formats['subheader'])
        worksheet.write(f'D{row}', 'Prawdopodobieństwo', formats['subheader'])
        worksheet.write(f'E{row}', 'Wynik', formats['subheader'])
        worksheet.write(f'F{row}', 'Poziom', formats['subheader'])
        row += 1
        
        # Risk items
        for risk in assessment.risk_items:
            score = self.calculate_risk_score(risk.impact, risk.probability)
            level = self.get_risk_level(score)
            
            # Get format based on risk level
            level_format = formats.get(f'{level.lower()}_risk', formats['border'])
            
            worksheet.write(f'A{row}', risk.name, formats['border'])
            worksheet.write(f'B{row}', self.risk_categories[risk.category].name, formats['border'])
            worksheet.write(f'C{row}', risk.impact, formats['number'])
            worksheet.write(f'D{row}', risk.probability, formats['number'])
            worksheet.write(f'E{row}', score, formats['number'])
            worksheet.write(f'F{row}', level, level_format)
            row += 1
        
        # Set column widths
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 10)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 12)
    
    def _create_detailed_risks_sheet(self, 
                                   workbook: xlsxwriter.Workbook, 
                                   assessment: RiskAssessment, 
                                   formats: Dict[str, Any]):
        """Create detailed risks sheet."""
        worksheet = workbook.add_worksheet('Szczegóły Ryzyk')
        
        # Title
        worksheet.merge_range('A1:H1', 'SZCZEGÓŁOWA OCENA RYZYK', formats['header'])
        
        # Header
        row = 3
        headers = ['ID', 'Nazwa', 'Kategoria', 'Opis', 'Kontrole', 'Łagodzenie', 'Właściciel', 'Termin']
        for i, header in enumerate(headers):
            worksheet.write(row, i, header, formats['subheader'])
        row += 1
        
        # Risk details
        for risk in assessment.risk_items:
            worksheet.write(f'A{row}', risk.id, formats['border'])
            worksheet.write(f'B{row}', risk.name, formats['border'])
            worksheet.write(f'C{row}', self.risk_categories[risk.category].name, formats['border'])
            worksheet.write(f'D{row}', risk.description, formats['border'])
            worksheet.write(f'E{row}', '; '.join(risk.controls), formats['border'])
            worksheet.write(f'F{row}', risk.mitigation, formats['border'])
            worksheet.write(f'G{row}', risk.owner, formats['border'])
            if risk.due_date:
                worksheet.write(f'H{row}', risk.due_date, formats['date'])
            else:
                worksheet.write(f'H{row}', 'Brak', formats['border'])
            row += 1
        
        # Set column widths
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 40)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 30)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 12)
    
    def _create_categories_sheet(self, 
                               workbook: xlsxwriter.Workbook, 
                               assessment: RiskAssessment, 
                               formats: Dict[str, Any]):
        """Create categories analysis sheet."""
        worksheet = workbook.add_worksheet('Kategorie Ryzyk')
        
        # Title
        worksheet.merge_range('A1:E1', 'ANALIZA KATEGORII RYZYK', formats['header'])
        
        # Header
        row = 3
        headers = ['Kategoria', 'Waga', 'Liczba ryzyk', 'Średni wynik', 'Maksymalny wynik']
        for i, header in enumerate(headers):
            worksheet.write(row, i, header, formats['subheader'])
        row += 1
        
        # Category analysis
        for category_name, category in self.risk_categories.items():
            category_risks = [r for r in assessment.risk_items if r.category == category_name]
            
            if category_risks:
                avg_score = sum(self.calculate_risk_score(r.impact, r.probability) for r in category_risks) / len(category_risks)
                max_score = max(self.calculate_risk_score(r.impact, r.probability) for r in category_risks)
            else:
                avg_score = 0
                max_score = 0
            
            worksheet.write(f'A{row}', category.name, formats['border'])
            worksheet.write(f'B{row}', category.weight, formats['percent'])
            worksheet.write(f'C{row}', len(category_risks), formats['number'])
            worksheet.write(f'D{row}', avg_score, formats['number'])
            worksheet.write(f'E{row}', max_score, formats['number'])
            row += 1
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 12)
        worksheet.set_column('D:D', 12)
        worksheet.set_column('E:E', 12)
    
    def _create_mitigation_plan_sheet(self, 
                                    workbook: xlsxwriter.Workbook, 
                                    assessment: RiskAssessment, 
                                    formats: Dict[str, Any]):
        """Create mitigation plan sheet."""
        worksheet = workbook.add_worksheet('Plan Łagodzenia')
        
        # Title
        worksheet.merge_range('A1:F1', 'PLAN ŁAGODZENIA RYZYK', formats['header'])
        
        # Header
        row = 3
        headers = ['Ryzyko', 'Poziom', 'Działania', 'Odpowiedzialny', 'Termin', 'Status']
        for i, header in enumerate(headers):
            worksheet.write(row, i, header, formats['subheader'])
        row += 1
        
        # Mitigation plan
        for risk in assessment.risk_items:
            score = self.calculate_risk_score(risk.impact, risk.probability)
            level = self.get_risk_level(score)
            
            # Get format based on risk level
            level_format = formats.get(f'{level.lower()}_risk', formats['border'])
            
            worksheet.write(f'A{row}', risk.name, formats['border'])
            worksheet.write(f'B{row}', level, level_format)
            worksheet.write(f'C{row}', risk.mitigation, formats['border'])
            worksheet.write(f'D{row}', risk.owner, formats['border'])
            if risk.due_date:
                worksheet.write(f'E{row}', risk.due_date, formats['date'])
            else:
                worksheet.write(f'E{row}', 'Brak', formats['border'])
            worksheet.write(f'F{row}', 'Planowane', formats['border'])
            row += 1
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 12)
        worksheet.set_column('C:C', 40)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 12)
        worksheet.set_column('F:F', 12)
    
    def _create_assumptions_sheet(self, 
                                workbook: xlsxwriter.Workbook, 
                                assessment: RiskAssessment, 
                                formats: Dict[str, Any]):
        """Create assumptions and methodology sheet."""
        worksheet = workbook.add_worksheet('Założenia')
        
        # Title
        worksheet.merge_range('A1:B1', 'ZAŁOŻENIA I METODOLOGIA', formats['header'])
        
        # Content
        row = 3
        assumptions = [
            ("Metodologia oceny:", "Ocena ryzyka oparta na macierzy wpływu i prawdopodobieństwa"),
            ("Skala wpływu:", "1-5 (1=niskie, 5=bardzo wysokie)"),
            ("Skala prawdopodobieństwa:", "1-5 (1=niskie, 5=bardzo wysokie)"),
            ("Wynik ryzyka:", "Wpływ × Prawdopodobieństwo"),
            ("Poziomy ryzyka:", "Wysokie: ≥20, Średnie: 10-19, Niskie: <10"),
            ("", ""),
            ("Kategorie ryzyk:", ""),
            ("• Ryzyko Finansowe", "Waga: 30%"),
            ("• Ryzyko Operacyjne", "Waga: 25%"),
            ("• Ryzyko Zgodności", "Waga: 20%"),
            ("• Ryzyko Rynkowe", "Waga: 15%"),
            ("• Ryzyko Reputacji", "Waga: 10%"),
            ("", ""),
            ("Data generowania:", assessment.assessment_date.strftime('%d.%m.%Y %H:%M')),
            ("Oceniający:", assessment.assessor),
            ("Okres oceny:", f"{assessment.period_start.strftime('%d.%m.%Y')} - {assessment.period_end.strftime('%d.%m.%Y')}")
        ]
        
        for assumption, description in assumptions:
            if assumption:
                worksheet.write(f'A{row}', assumption, formats['bold'])
            worksheet.write(f'B{row}', description, formats['border'])
            row += 1
        
        # Set column widths
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 50)
    
    def generate_sample_risks(self, company_name: str) -> List[RiskItem]:
        """Generate sample risk items for testing."""
        sample_risks = [
            RiskItem(
                id="R001",
                category="financial",
                name="Niewypłacalność klientów",
                description="Ryzyko braku płatności od klientów może prowadzić do problemów z płynnością finansową",
                impact=4.0,
                probability=3.0,
                controls=["Weryfikacja klientów", "Limity kredytowe", "Ubezpieczenie należności"],
                mitigation="Wprowadzenie systemu weryfikacji klientów i ubezpieczenia należności",
                owner="Dział Finansowy",
                due_date=datetime.now() + timedelta(days=30)
            ),
            RiskItem(
                id="R002",
                category="compliance",
                name="Niezgodność z przepisami VAT",
                description="Ryzyko błędów w rozliczeniach VAT może prowadzić do kar finansowych",
                impact=5.0,
                probability=2.0,
                controls=["Audyty wewnętrzne", "Szkolenia", "Automatyzacja procesów"],
                mitigation="Wprowadzenie systemu automatycznego rozliczania VAT",
                owner="Dział Księgowości",
                due_date=datetime.now() + timedelta(days=60)
            ),
            RiskItem(
                id="R003",
                category="operational",
                name="Awaria systemu IT",
                description="Ryzyko awarii systemów informatycznych może zakłócić działalność",
                impact=4.0,
                probability=2.0,
                controls=["Backup", "Redundancja", "Monitoring"],
                mitigation="Wprowadzenie systemu backup i redundancji",
                owner="Dział IT",
                due_date=datetime.now() + timedelta(days=45)
            ),
            RiskItem(
                id="R004",
                category="market",
                name="Spadek popytu",
                description="Ryzyko spadku popytu na produkty/usługi firmy",
                impact=3.0,
                probability=3.0,
                controls=["Dywersyfikacja", "Analiza rynku", "Innowacje"],
                mitigation="Dywersyfikacja portfolio produktów",
                owner="Dział Marketingu",
                due_date=datetime.now() + timedelta(days=90)
            ),
            RiskItem(
                id="R005",
                category="reputation",
                name="Negatywne opinie klientów",
                description="Ryzyko negatywnych opinii może wpłynąć na reputację firmy",
                impact=3.0,
                probability=2.0,
                controls=["Monitoring opinii", "Szybka reakcja", "Jakość usług"],
                mitigation="Wprowadzenie systemu monitoringu opinii",
                owner="Dział Obsługi Klienta",
                due_date=datetime.now() + timedelta(days=30)
            )
        ]
        
        return sample_risks


# Global instance
_risk_generator = RiskTableGenerator()


def generate_risk_assessment(company_name: str,
                           assessor: str,
                           period_start: datetime,
                           period_end: datetime,
                           risk_items: List[RiskItem],
                           output_path: Path) -> Path:
    """Convenience function to generate risk assessment."""
    generator = RiskTableGenerator()
    assessment = generator.create_risk_assessment(
        company_name, assessor, period_start, period_end, risk_items
    )
    return generator.generate_excel_workbook(assessment, output_path)


def generate_sample_risk_assessment(company_name: str, output_path: Path) -> Path:
    """Generate sample risk assessment for testing."""
    generator = RiskTableGenerator()
    risk_items = generator.generate_sample_risks(company_name)
    
    assessment = generator.create_risk_assessment(
        company_name=company_name,
        assessor="System AI Auditor",
        period_start=datetime.now() - timedelta(days=365),
        period_end=datetime.now(),
        risk_items=risk_items
    )
    
    return generator.generate_excel_workbook(assessment, output_path)
