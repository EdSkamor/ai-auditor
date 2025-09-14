# MCP-Auditor Domain Mapping

This document maps existing AI-Auditor capabilities from `core/`, `cli/`, and `web/` modules to the new MCP server architecture.

## Overview

The AI-Auditor system is being reorganized into 9 specialized MCP servers, each handling a specific domain of functionality. This mapping ensures that all existing capabilities are preserved while providing a cleaner, more modular architecture.

## Server Mappings

### 1. mcp-files
**Purpose**: File system access and management

**Maps from**:
- `core/data_processing.py` - File reading/writing utilities
- `cli/base.py` - File path handling
- `web/` - File upload/download functionality

**Key Capabilities**:
- Directory listing and file statistics
- Text file reading with encoding support
- Artifact writing to outputs/ directory
- File metadata extraction

**Tools**:
- `list_dir` - List directory contents
- `stat_path` - Get file/directory information
- `read_text` - Read text files
- `write_artifact` - Write to outputs/ directory

### 2. mcp-xlsx
**Purpose**: Excel/POP data processing and validation

**Maps from**:
- `core/data_processing.py` - Excel file processing
- `core/pop_matcher.py` - POP data handling
- `cli/validate.py` - Excel validation logic

**Key Capabilities**:
- POP data indexing and analysis
- Sheet reading with pagination
- Data schema validation
- Sample data preview

**Tools**:
- `index_pop` - Index and analyze POP data
- `read_sheet` - Read specific sheet data
- `preview_rows` - Preview data samples
- `pop_schema_info` - Analyze data schema

### 3. mcp-pdf
**Purpose**: PDF parsing, OCR, and field extraction

**Maps from**:
- `core/ocr_processor.py` - OCR processing
- `core/pdf_indexer.py` - PDF indexing
- `core/ocr_etl.py` - OCR data extraction
- `cli/ocr_sample.py` - OCR sampling

**Key Capabilities**:
- Structured field extraction from PDFs
- OCR quality assessment
- PDF metadata extraction
- Multi-page document processing

**Tools**:
- `extract_fields` - Extract structured fields
- `ocr_page_sample` - OCR quality sampling
- `pdf_meta` - Extract PDF metadata

### 4. mcp-matcher
**Purpose**: XLSX↔PDF matching and tie-breaking

**Maps from**:
- `core/pop_matcher.py` - POP-PDF matching
- `core/fuzzy_match.py` - Fuzzy matching algorithms
- `core/run_audit.py` - Matching orchestration

**Key Capabilities**:
- Deterministic matching algorithms
- Tie-breaking logic with configurable weights
- Fuzzy matching with similarity thresholds
- Match confidence scoring

**Tools**:
- `match_pop_to_pdf` - Match POP records to PDFs
- `tiebreak_summary` - Analyze tie-breaking results

### 5. mcp-validator
**Purpose**: Business rule validation and compliance

**Maps from**:
- `core/rules.py` - Business rule engine
- `core/payment_validation.py` - Payment validation
- `core/compliance_security.py` - Compliance checks
- `rules.yaml` - Rule configuration

**Key Capabilities**:
- Configurable rule execution
- Multiple validation modes (full, preselection, revalidation)
- Issue categorization and severity
- Export validation results

**Tools**:
- `run_ruleset` - Execute validation rules
- `list_issues` - Filter and list issues
- `export_validation_table` - Export results

### 6. mcp-risk
**Purpose**: Risk scoring and deviation analysis

**Maps from**:
- `core/risk_table_generator.py` - Risk calculation
- `core/audit_analytics.py` - Analytics and scoring
- `cli/generate_risk_table.py` - Risk table generation

**Key Capabilities**:
- Multi-factor risk scoring
- Configurable risk weights
- Risk level categorization
- Risk report generation

**Tools**:
- `compute_risk` - Calculate risk scores
- `export_risk_table` - Export risk analysis

### 7. mcp-report
**Purpose**: Report generation and artifact management

**Maps from**:
- `core/export_final_xlsx.py` - Excel report generation
- `core/evidence_zip.py` - Evidence packaging
- `core/run_audit.py` - Report orchestration
- `cli/build_docs.py` - Documentation generation

**Key Capabilities**:
- Professional Excel report generation
- Evidence package creation (ZIP)
- Artifact management and listing
- Multiple report templates

**Tools**:
- `build_zip` - Create evidence packages
- `render_excel_report` - Generate Excel reports
- `list_artifacts` - List available artifacts

### 8. mcp-auditlog
**Purpose**: Audit trail and event logging

**Maps from**:
- `core/run_audit.py` - Audit logging
- `web/` - Web request logging
- `cli/` - CLI operation logging

**Key Capabilities**:
- Structured event logging
- Audit trail maintenance
- Performance metrics collection
- Event querying and filtering

**Tools**:
- `append_event` - Log audit events
- `query_events` - Query audit logs

### 9. mcp-webhook
**Purpose**: Job status management and web integration

**Maps from**:
- `web/` - Web backend integration
- `server.py` - API endpoints
- `app/main.py` - Web application logic

**Key Capabilities**:
- Job status communication
- Real-time progress updates
- Web backend integration
- Artifact delivery

**Tools**:
- `push_status` - Update job status
- `pull_job` - Retrieve job details
- `complete_job` - Mark job completion

## Data Flow Mapping

### Input Data Sources
- **POP Data**: `populacja/` → mcp-xlsx
- **PDF Documents**: `pdfs/` → mcp-pdf
- **Configuration**: `rules.yaml` → mcp-validator

### Processing Pipeline
1. **Data Ingestion**: mcp-files, mcp-xlsx, mcp-pdf
2. **Data Matching**: mcp-matcher
3. **Validation**: mcp-validator
4. **Risk Analysis**: mcp-risk
5. **Report Generation**: mcp-report
6. **Status Updates**: mcp-webhook
7. **Audit Logging**: mcp-auditlog (throughout)

### Output Artifacts
- **Reports**: `outputs/reports/` ← mcp-report
- **Tables**: `outputs/tables/` ← mcp-validator, mcp-risk
- **Evidence**: `outputs/evidence/` ← mcp-report
- **Logs**: `logs/audit/` ← mcp-auditlog

## Migration Strategy

### Phase 1: Contract Definition ✅
- Define MCP server contracts
- Establish security policies
- Map existing capabilities

### Phase 2: Server Implementation
- Implement each MCP server
- Port existing functionality
- Maintain backward compatibility

### Phase 3: Integration
- Update web backend for MCP integration
- Configure Cursor for MCP servers
- Test end-to-end workflows

### Phase 4: Documentation
- Create user runbooks
- Document rule dictionary
- Provide migration guides

## Backward Compatibility

All existing CLI commands and web interfaces will continue to work during the transition. The MCP architecture provides a new layer of functionality while preserving existing APIs and workflows.

## Benefits of MCP Architecture

1. **Modularity**: Each server handles a specific domain
2. **Scalability**: Servers can be scaled independently
3. **Maintainability**: Clear separation of concerns
4. **Extensibility**: Easy to add new capabilities
5. **Security**: Granular access controls per server
6. **Auditability**: Comprehensive logging and monitoring
