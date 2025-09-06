# AI Auditor - Context for Cursor/AI Development

## Project Overview

AI Auditor is a **production-ready, commercial system** for invoice validation and audit support. It processes private financial data and must maintain the highest security and reliability standards.

## Critical Requirements

### 🔒 Security (Level 200)
- **On-premise only** - no cloud dependencies
- **Data never leaves the system** - all processing local
- **Input validation** - all files must be validated before processing
- **File size limits** - prevent DoS attacks
- **ZIP security** - prevent path traversal attacks
- **Memory limits** - prevent memory exhaustion
- **Error handling** - no sensitive data in error messages

### 🏗️ Architecture
```
ai-auditor/
├── core/                 # Core business logic
│   ├── pdf_indexer.py   # PDF processing & indexing
│   ├── pop_matcher.py   # POP matching with tie-breaker
│   ├── data_processing.py # Data ingestion & analysis
│   ├── export_final_xlsx.py # Excel report generation
│   └── run_audit.py     # Complete audit pipeline
├── cli/                  # Command-line interfaces
├── tests/               # Unit tests
├── scripts/             # WSAD test scripts
└── docs/                # Documentation
```

### 📋 Feature Catalog Status

#### ✅ Implemented (Production Ready)
1. **PDF Indexing** - Recursive PDF processing with security
2. **POP Matching** - Deterministic tie-breaker logic
3. **Data Processing** - Locale-safe amount parsing
4. **Excel Reports** - Professional formatting with formulas
5. **CLI Framework** - Consistent error handling
6. **WSAD Testing** - Comprehensive test suite

#### ⏳ In Progress
7. **Streamlit UI** - Minimalist web interface
8. **OCR Integration** - Tesseract/EasyOCR support
9. **KRS Integration** - Company data enrichment
10. **Risk Tables** - Excel risk assessment

#### 📋 Planned
11. **Documentation** - Sphinx docs
12. **CI/CD** - Automated testing
13. **Security Audit** - Penetration testing

## Development Rules

### Code Quality
- **Type hints required** - all functions must have type annotations
- **Error handling** - every function must handle exceptions
- **Logging** - comprehensive logging for debugging
- **Testing** - every feature must have tests
- **Documentation** - docstrings for all public functions

### Security Rules
- **Never log sensitive data** - no invoice numbers, amounts, or company names in logs
- **Validate all inputs** - file types, sizes, content
- **Use secure defaults** - fail closed, not open
- **Memory management** - process large files in chunks
- **Error messages** - generic messages for users, detailed for logs

### Performance Rules
- **Process in batches** - don't load everything into memory
- **Progress reporting** - show progress for long operations
- **Resource limits** - respect system resources
- **Caching** - cache expensive operations

## Testing Strategy

### WSAD+TEST Methodology
Each feature has its own test script in `scripts/`:
- `smoke_all.py` - Complete functionality test
- `smoke_perf_200.py` - Performance test (200 PDFs)
- `smoke_tiebreak_ab.py` - Tie-breaker A/B testing
- `test_validation_demo.py` - Demo validation test
- `test_validation_bulk.py` - Bulk validation test

### Test Categories
- **Unit Tests** - Individual function testing
- **Integration Tests** - End-to-end workflow testing
- **Performance Tests** - Load and stress testing
- **Security Tests** - Input validation and edge cases

## CLI Usage

### Validation Commands
```bash
# Demo validation
ai-auditor validate --demo --file invoice.pdf --pop-file pop.xlsx

# Bulk validation
ai-auditor validate --bulk --input-dir ./pdfs --pop-file pop.xlsx --output-dir ./results

# With tie-breaker settings
ai-auditor validate --bulk --input-dir ./pdfs --pop-file pop.xlsx \
  --tiebreak-weight-fname 0.7 --tiebreak-min-seller 0.4 --amount-tol 0.01
```

### Other Commands
```bash
# OCR sampling
ai-auditor ocr-sample --input invoice.pdf --sample-size 10

# Data enrichment
ai-auditor enrich-data --input companies.csv --krs --whitelist

# Risk table generation
ai-auditor generate-risk-table --data financial_data.xlsx --output risk_table.xlsx

# Documentation
ai-auditor build-docs --html --pdf --clean
```

## Error Handling

### Exit Codes
- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - File not found
- `4` - Permission denied
- `5` - Network error
- `6` - Processing error
- `7` - Validation error

### Logging Levels
- `DEBUG` - Detailed debugging information
- `INFO` - General information
- `WARNING` - Warning conditions
- `ERROR` - Error conditions
- `CRITICAL` - Critical errors

## Data Formats

### PDF Indexing Output
```csv
source_path,source_filename,invoice_id,issue_date,total_net,currency,seller_guess,error,confidence,processing_time
```

### POP Matching Output
```jsonl
{"source_filename": "invoice.pdf", "status": "znaleziono", "criteria": "numer", "confidence": 0.95, ...}
```

### Excel Report
- Executive Summary sheet
- Detailed Results sheet
- Top 50 Mismatches sheet
- Statistics & Analysis sheet

## Performance Targets

### Processing Speed
- **PDF Indexing**: >20 files/second
- **POP Matching**: >100 matches/second
- **Memory Usage**: <100MB for 1000 records
- **File Size Limit**: 50MB per PDF

### Reliability
- **Uptime**: 99.9%
- **Error Rate**: <0.1%
- **Data Integrity**: 100%

## Security Checklist

### Input Validation
- [ ] File type validation
- [ ] File size limits
- [ ] Path traversal prevention
- [ ] Malicious content detection

### Data Protection
- [ ] No sensitive data in logs
- [ ] Encrypted storage (if needed)
- [ ] Access control
- [ ] Audit trails

### Error Handling
- [ ] Generic error messages
- [ ] No stack traces to users
- [ ] Proper logging
- [ ] Graceful degradation

## Development Workflow

### Before Coding
1. Read this context file
2. Understand the feature requirements
3. Check existing tests
4. Plan error handling

### During Coding
1. Follow type hints
2. Add comprehensive error handling
3. Add logging
4. Write tests
5. Update documentation

### After Coding
1. Run all tests
2. Check security implications
3. Verify performance
4. Update this context if needed

## Common Patterns

### File Processing
```python
def process_file(file_path: Path) -> Result:
    try:
        # Validate file
        _validate_file_security(file_path)
        
        # Process file
        result = _process_content(file_path)
        
        # Log success (no sensitive data)
        logger.info(f"Processed file: {file_path.name}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to process {file_path.name}: {e}")
        raise FileProcessingError(f"Processing failed")
```

### Data Matching
```python
def match_invoice(invoice_data: Dict, pop_data: pd.DataFrame) -> MatchResult:
    try:
        # Validate inputs
        if not invoice_data or pop_data.empty:
            return MatchResult(status=MatchStatus.ERROR)
        
        # Perform matching
        result = _perform_matching(invoice_data, pop_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Matching failed: {e}")
        return MatchResult(status=MatchStatus.ERROR)
```

## Troubleshooting

### Common Issues
1. **Import errors** - Check Python path and dependencies
2. **File not found** - Verify file paths and permissions
3. **Memory errors** - Check file sizes and batch processing
4. **Performance issues** - Check system resources and optimization

### Debug Mode
```bash
ai-auditor validate --demo --file invoice.pdf --debug --verbose
```

### Log Analysis
```bash
# Check for errors
grep "ERROR" audit.log

# Check performance
grep "processing_time" audit.log | tail -10
```

## Contact & Support

- **Repository**: https://github.com/EdSkamor/ai-auditor
- **Documentation**: `docs/` directory
- **Tests**: `scripts/` directory
- **Issues**: GitHub Issues

---

**Remember**: This is a production system handling sensitive financial data. Security and reliability are paramount. When in doubt, fail safely and log everything.

