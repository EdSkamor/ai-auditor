"""
Moduł przetwarzający Wstępne Procedury audytorskie
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Union
import pandas as pd

logger = logging.getLogger(__name__)

class FormulaEvaluator:
    """Klasa do ewaluacji formuł Excel"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.sheets = data.get('sheets', {})
    
    def _parse_cell_reference(self, cell_ref: str) -> tuple:
        """Parsuje referencję komórki (np. 'A1' -> (0, 0))"""
        if not cell_ref:
            return None, None
        
        # Usuń znaki $ (absolute reference)
        cell_ref = cell_ref.replace('$', '')
        
        # Parsuj kolumnę i wiersz
        match = re.match(r'([A-Z]+)(\d+)', cell_ref)
        if not match:
            return None, None
        
        col_str, row_str = match.groups()
        
        # Konwertuj kolumnę na liczbę
        col = 0
        for char in col_str:
            col = col * 26 + (ord(char) - ord('A') + 1)
        col -= 1  # 0-based indexing
        
        # Konwertuj wiersz na liczbę
        row = int(row_str) - 1  # 0-based indexing
        
        return row, col
    
    def _get_cell_value(self, sheet_name: str, row: int, col: int) -> Any:
        """Pobiera wartość komórki z arkusza"""
        if sheet_name not in self.sheets:
            return 0
        
        sheet = self.sheets[sheet_name]
        if row >= len(sheet['data']) or col >= len(sheet['data'][row]):
            return 0
        
        value = sheet['data'][row][str(col)]
        
        # Konwertuj na liczbę jeśli możliwe
        try:
            if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                return float(value)
            return value
        except:
            return 0
    
    def _evaluate_sum(self, args: List[str]) -> float:
        """Ewaluuje funkcję SUM"""
        total = 0
        for arg in args:
            if ':' in arg:  # Range (np. A1:A10)
                start, end = arg.split(':')
                start_row, start_col = self._parse_cell_reference(start)
                end_row, end_col = self._parse_cell_reference(end)
                
                if start_row is not None and end_row is not None:
                    for row in range(min(start_row, end_row), max(start_row, end_row) + 1):
                        for col in range(min(start_col, end_col), max(start_col, end_col) + 1):
                            # Domyślnie używamy pierwszego arkusza
                            sheet_name = list(self.sheets.keys())[0] if self.sheets else ''
                            total += self._get_cell_value(sheet_name, row, col)
            else:  # Pojedyncza komórka
                row, col = self._parse_cell_reference(arg)
                if row is not None and col is not None:
                    sheet_name = list(self.sheets.keys())[0] if self.sheets else ''
                    total += self._get_cell_value(sheet_name, row, col)
        return total
    
    def _evaluate_average(self, args: List[str]) -> float:
        """Ewaluuje funkcję AVERAGE"""
        values = []
        for arg in args:
            if ':' in arg:  # Range
                start, end = arg.split(':')
                start_row, start_col = self._parse_cell_reference(start)
                end_row, end_col = self._parse_cell_reference(end)
                
                if start_row is not None and end_row is not None:
                    for row in range(min(start_row, end_row), max(start_row, end_row) + 1):
                        for col in range(min(start_col, end_col), max(start_col, end_col) + 1):
                            sheet_name = list(self.sheets.keys())[0] if self.sheets else ''
                            values.append(self._get_cell_value(sheet_name, row, col))
            else:  # Pojedyncza komórka
                row, col = self._parse_cell_reference(arg)
                if row is not None and col is not None:
                    sheet_name = list(self.sheets.keys())[0] if self.sheets else ''
                    values.append(self._get_cell_value(sheet_name, row, col))
        
        return sum(values) / len(values) if values else 0
    
    def _evaluate_count(self, args: List[str]) -> int:
        """Ewaluuje funkcję COUNT/COUNTA"""
        count = 0
        for arg in args:
            if ':' in arg:  # Range
                start, end = arg.split(':')
                start_row, start_col = self._parse_cell_reference(start)
                end_row, end_col = self._parse_cell_reference(end)
                
                if start_row is not None and end_row is not None:
                    for row in range(min(start_row, end_row), max(start_row, end_row) + 1):
                        for col in range(min(start_col, end_col), max(start_col, end_col) + 1):
                            sheet_name = list(self.sheets.keys())[0] if self.sheets else ''
                            value = self._get_cell_value(sheet_name, row, col)
                            if value != 0 and value != '':
                                count += 1
            else:  # Pojedyncza komórka
                row, col = self._parse_cell_reference(arg)
                if row is not None and col is not None:
                    sheet_name = list(self.sheets.keys())[0] if self.sheets else ''
                    value = self._get_cell_value(sheet_name, row, col)
                    if value != 0 and value != '':
                        count += 1
        return count
    
    def _evaluate_if(self, args: List[str]) -> Any:
        """Ewaluuje funkcję IF"""
        if len(args) < 3:
            return 0
        
        condition = args[0]
        true_value = args[1]
        false_value = args[2]
        
        # Prosta ewaluacja warunku
        try:
            # Zamień referencje komórek na wartości
            for sheet_name, sheet in self.sheets.items():
                for row_idx, row_data in enumerate(sheet['data']):
                    for col_idx, value in row_data.items():
                        cell_ref = f"{chr(65 + int(col_idx))}{row_idx + 1}"
                        if cell_ref in condition:
                            condition = condition.replace(cell_ref, str(value))
            
            # Ewaluuj warunek
            if eval(condition):
                return true_value.strip('"') if isinstance(true_value, str) else true_value
            else:
                return false_value.strip('"') if isinstance(false_value, str) else false_value
        except:
            return false_value
    
    def evaluate_formula(self, formula: str) -> Any:
        """Ewaluuje formułę Excel"""
        if not formula:
            return formula
        if not formula.startswith('='):
            return formula
        
        # Usuń znak =
        formula = formula[1:]
        
        # Parsuj funkcję i argumenty
        match = re.match(r'(\w+)\((.*)\)', formula)
        if not match:
            return '=' + formula
        
        # Sprawdź czy to zagnieżdżona funkcja (ma więcej niż jeden poziom nawiasów)
        if formula.count('(') > 1:
            return '=' + formula
        
        func_name = match.group(1).upper()
        args_str = match.group(2)
        
        # Parsuj argumenty
        args = []
        current_arg = ""
        paren_count = 0
        
        for char in args_str:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                args.append(current_arg.strip())
                current_arg = ""
                continue
            current_arg += char
        
        if current_arg.strip():
            args.append(current_arg.strip())
        
        # Ewaluuj funkcję
        try:
            if func_name == 'SUM':
                return self._evaluate_sum(args)
            elif func_name == 'AVERAGE':
                return self._evaluate_average(args)
            elif func_name in ['COUNT', 'COUNTA']:
                return self._evaluate_count(args)
            elif func_name == 'IF':
                return self._evaluate_if(args)
            else:
                logger.warning(f"Unsupported function: {func_name}")
                return '=' + formula
        except Exception as e:
            logger.error(f"Error evaluating formula {formula}: {e}")
            return '=' + formula


def parse_wstepne(path: Path) -> Dict[str, Any]:
    """
    Ładuje JSON i zwraca strukturę Python
    
    Args:
        path: Ścieżka do pliku JSON
        
    Returns:
        Dict z danymi z pliku JSON
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {data['metadata']['sheets_count']} sheets from {path}")
        return data
    except Exception as e:
        logger.error(f"Error loading file {path}: {e}")
        raise


def eval_formulas(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parsuje i ewaluuje formuły dla dostępnych funkcji
    
    Args:
        data: Dane z pliku JSON
        
    Returns:
        Dict z wynikami ewaluacji formuł
    """
    evaluator = FormulaEvaluator(data)
    results = {
        'evaluated_sheets': {},
        'formula_errors': [],
        'total_formulas': 0,
        'successful_evaluations': 0
    }
    
    for sheet_name, sheet_data in data.get('sheets', {}).items():
        logger.info(f"Evaluating formulas in sheet: {sheet_name}")
        
        evaluated_sheet = {
            'name': sheet_name,
            'formulas': {},
            'evaluated_data': []
        }
        
        # Ewaluuj dane w arkuszu
        for row_idx, row_data in enumerate(sheet_data.get('data', [])):
            evaluated_row = {}
            for col_idx, value in row_data.items():
                if isinstance(value, str) and value.startswith('='):
                    # To jest formuła
                    results['total_formulas'] += 1
                    try:
                        evaluated_value = evaluator.evaluate_formula(value)
                        evaluated_row[col_idx] = evaluated_value
                        results['successful_evaluations'] += 1
                        
                        # Zapisz formułę i wynik
                        cell_ref = f"{chr(65 + int(col_idx))}{row_idx + 1}"
                        evaluated_sheet['formulas'][cell_ref] = {
                            'formula': value,
                            'result': evaluated_value
                        }
                    except Exception as e:
                        logger.error(f"Error evaluating formula {value} in {sheet_name}: {e}")
                        evaluated_row[col_idx] = value
                        results['formula_errors'].append({
                            'sheet': sheet_name,
                            'cell': f"{chr(65 + int(col_idx))}{row_idx + 1}",
                            'formula': value,
                            'error': str(e)
                        })
                else:
                    evaluated_row[col_idx] = value
            
            evaluated_sheet['evaluated_data'].append(evaluated_row)
        
        results['evaluated_sheets'][sheet_name] = evaluated_sheet
    
    logger.info(f"Evaluated {results['successful_evaluations']}/{results['total_formulas']} formulas")
    return results


def to_report(data: Dict[str, Any], results: Dict[str, Any]) -> Union[Dict[str, Any], pd.DataFrame]:
    """
    Zwraca zagregowane wyniki na arkusz
    
    Args:
        data: Oryginalne dane
        results: Wyniki ewaluacji formuł
        
    Returns:
        Dict lub DataFrame z raportem
    """
    report = {
        'metadata': data.get('metadata', {}),
        'summary': {
            'total_sheets': len(data.get('sheets', {})),
            'total_formulas': results.get('total_formulas', 0),
            'successful_evaluations': results.get('successful_evaluations', 0),
            'formula_errors': len(results.get('formula_errors', [])),
            'success_rate': 0
        },
        'sheets_summary': {},
        'formula_errors': results.get('formula_errors', [])
    }
    
    # Oblicz success rate
    if report['summary']['total_formulas'] > 0:
        report['summary']['success_rate'] = (
            report['summary']['successful_evaluations'] / 
            report['summary']['total_formulas'] * 100
        )
    
    # Podsumowanie dla każdego arkusza
    for sheet_name, sheet_results in results.get('evaluated_sheets', {}).items():
        formulas_count = len(sheet_results.get('formulas', {}))
        report['sheets_summary'][sheet_name] = {
            'formulas_count': formulas_count,
            'rows': len(sheet_results.get('evaluated_data', [])),
            'cols': len(sheet_results.get('evaluated_data', [0])) if sheet_results.get('evaluated_data') else 0
        }
    
    return report


def process_wstepne_procedury(json_path: str) -> Dict[str, Any]:
    """
    Główna funkcja przetwarzająca Wstępne Procedury
    
    Args:
        json_path: Ścieżka do pliku JSON
        
    Returns:
        Dict z wynikami przetwarzania
    """
    try:
        # 1. Załaduj dane
        data = parse_wstepne(Path(json_path))
        
        # 2. Ewaluuj formuły
        results = eval_formulas(data)
        
        # 3. Stwórz raport
        report = to_report(data, results)
        
        return {
            'status': 'success',
            'data': data,
            'results': results,
            'report': report
        }
    except Exception as e:
        logger.error(f"Error processing wstepne procedury: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }
