# MCP-Auditor Runbook

This runbook provides step-by-step instructions for using the MCP-Auditor system to perform comprehensive audit workflows.

## Quick Start

### 1. System Setup
```bash
# Ensure you're in the MCP-auditor branch
git checkout MCP-auditor

# Install MCP dependencies
pip install -r requirements.txt

# Start the web backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Configure Cursor with MCP servers
# Copy mcp/cursor-config.json to your Cursor settings
```

### 2. Data Preparation
```bash
# Organize your data in the project structure:
inputs/          # Input data files
pdfs/           # PDF documents to audit
populacja/      # POP (Population) data in Excel format
outputs/        # Generated reports and artifacts (auto-created)
logs/           # Audit logs and system logs (auto-created)
```

## Audit Workflows

### Full Audit Workflow

**Purpose**: Complete audit from data ingestion to final report generation

**Steps**:
1. **Data Discovery**
   - Use `mcp-files:list_dir` to explore input directories
   - Use `mcp-xlsx:preview_rows` to examine POP data
   - Use `mcp-pdf:pdf_meta` to check PDF metadata

2. **Data Processing**
   - Use `mcp-xlsx:index_pop` to index POP data
   - Use `mcp-pdf:extract_fields` to extract fields from PDFs
   - Use `mcp-matcher:match_pop_to_pdf` to match records

3. **Validation**
   - Use `mcp-validator:run_ruleset` to validate matched data
   - Use `mcp-validator:list_issues` to review validation results

4. **Risk Analysis**
   - Use `mcp-risk:compute_risk` to calculate risk scores
   - Use `mcp-risk:export_risk_table` to export risk analysis

5. **Report Generation**
   - Use `mcp-report:build_zip` to create evidence package
   - Use `mcp-report:render_excel_report` to generate Excel report

6. **Job Completion**
   - Use `mcp-webhook:complete_job` to finalize the audit

**Estimated Time**: 10-30 minutes depending on data size

### Quick Validation Workflow

**Purpose**: Fast validation of pre-matched data

**Steps**:
1. **Load Matched Data**
   - Use `mcp-files:read_text` to load existing match results
   - Use `mcp-validator:run_ruleset` with matched data

2. **Risk Assessment**
   - Use `mcp-risk:compute_risk` to calculate risk scores
   - Use `mcp-report:render_excel_report` for quick report

**Estimated Time**: 2-5 minutes

### Data Preview Workflow

**Purpose**: Preview and analyze data before full processing

**Steps**:
1. **Data Inspection**
   - Use `mcp-xlsx:preview_rows` to examine POP data
   - Use `mcp-pdf:pdf_meta` to check PDF properties
   - Use `mcp-xlsx:pop_schema_info` to validate data schema

2. **Quality Assessment**
   - Review data completeness and quality
   - Identify potential issues before processing

**Estimated Time**: 1-2 minutes

## Tool Usage Examples

### File Operations

#### List Directory Contents
```json
{
  "tool": "mcp-files:list_dir",
  "input": {
    "path": "pdfs/",
    "recursive": false,
    "filter": "*.pdf"
  }
}
```

#### Read Text File
```json
{
  "tool": "mcp-files:read_text",
  "input": {
    "path": "inputs/config.json",
    "encoding": "utf-8",
    "max_size": 1048576
  }
}
```

### Data Processing

#### Index POP Data
```json
{
  "tool": "mcp-xlsx:index_pop",
  "input": {
    "file_path": "populacja/data.xlsx",
    "sheet_name": "Sheet1",
    "header_row": 0
  }
}
```

#### Extract PDF Fields
```json
{
  "tool": "mcp-pdf:extract_fields",
  "input": {
    "file_path": "pdfs/invoice_001.pdf",
    "field_types": ["invoice_number", "amount", "date", "seller"],
    "ocr_quality": "balanced"
  }
}
```

### Matching and Validation

#### Match POP to PDF
```json
{
  "tool": "mcp-matcher:match_pop_to_pdf",
  "input": {
    "pop_file_path": "populacja/data.xlsx",
    "pdf_directory": "pdfs/",
    "matching_rules": {
      "primary_fields": ["invoice_number", "amount"],
      "fuzzy_threshold": 0.8,
      "amount_tolerance": 0.01
    }
  }
}
```

#### Run Validation Rules
```json
{
  "tool": "mcp-validator:run_ruleset",
  "input": {
    "matched_data": {...},
    "validation_mode": "full",
    "custom_rules": []
  }
}
```

### Risk Analysis

#### Compute Risk Scores
```json
{
  "tool": "mcp-risk:compute_risk",
  "input": {
    "validation_results": {...},
    "risk_weights": {
      "severity_weights": {
        "critical": 10.0,
        "high": 7.0,
        "medium": 4.0,
        "low": 1.0
      }
    }
  }
}
```

### Report Generation

#### Build Evidence Package
```json
{
  "tool": "mcp-report:build_zip",
  "input": {
    "audit_data": {...},
    "package_name": "audit_evidence_20240115",
    "include_artifacts": ["validation_table", "risk_table", "summary_report"]
  }
}
```

## Error Handling

### Common Error Scenarios

#### File Not Found
```json
{
  "error": "E_NOT_FOUND",
  "message": "File or directory not found",
  "solution": "Check file path and ensure file exists"
}
```

#### Permission Denied
```json
{
  "error": "E_ACCESS_DENIED",
  "message": "Access denied to requested path",
  "solution": "Check file permissions and directory whitelist"
}
```

#### Memory Limit Exceeded
```json
{
  "error": "E_MEMORY_LIMIT",
  "message": "File too large for processing",
  "solution": "Split large files or increase memory limits"
}
```

### Error Recovery

1. **Check Logs**: Use `mcp-auditlog:query_events` to review error details
2. **Verify Inputs**: Ensure all required files and parameters are correct
3. **Retry with Smaller Data**: Split large datasets into smaller chunks
4. **Check System Resources**: Ensure sufficient memory and disk space

## Performance Optimization

### Large Dataset Processing

1. **Batch Processing**: Process data in smaller batches
2. **Parallel Processing**: Use multiple MCP servers simultaneously
3. **Memory Management**: Monitor memory usage and adjust limits
4. **Caching**: Use file caching for repeated operations

### Monitoring Progress

1. **Use Progress Tracking**: Monitor job progress through webhook updates
2. **Check Logs**: Review audit logs for processing details
3. **Resource Monitoring**: Monitor CPU, memory, and disk usage

## Troubleshooting

### Common Issues

#### MCP Server Not Responding
- Check server status and logs
- Restart the MCP server
- Verify network connectivity

#### Tool Execution Fails
- Check input parameters
- Verify file permissions
- Review error messages in logs

#### Webhook Communication Issues
- Verify web backend is running
- Check authentication tokens
- Review network connectivity

### Debug Mode

Enable debug logging by setting environment variables:
```bash
export MCP_LOG_LEVEL=DEBUG
export AIAUDITOR_DEBUG=true
```

## Best Practices

### Data Organization
- Keep input data in designated directories
- Use consistent naming conventions
- Maintain data backups

### Security
- Never expose sensitive data in logs
- Use proper authentication tokens
- Follow access control policies

### Performance
- Process data in appropriate batch sizes
- Monitor system resources
- Use appropriate tool configurations

### Audit Trail
- Always review audit logs
- Document any manual interventions
- Maintain complete audit trail

## Support

For additional support:
- Check the audit logs using `mcp-auditlog:query_events`
- Review the rules dictionary for validation details
- Consult the domain mapping for tool capabilities
- Check system status and resource usage
