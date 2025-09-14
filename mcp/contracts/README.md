# MCP-Auditor Contracts

This directory contains the Model Context Protocol (MCP) contracts for the AI-Auditor system. Each contract defines the tools and resources available in a specific MCP server, organized by domain.

## Architecture Overview

The AI-Auditor system is organized into 9 specialized MCP servers:

1. **mcp-files** - File system access and management
2. **mcp-xlsx** - Excel/POP data processing and validation
3. **mcp-pdf** - PDF parsing, OCR, and field extraction
4. **mcp-matcher** - XLSX↔PDF matching and tie-breaking
5. **mcp-validator** - Business rule validation and compliance
6. **mcp-risk** - Risk scoring and deviation analysis
7. **mcp-report** - Report generation and artifact management
8. **mcp-auditlog** - Audit trail and event logging
9. **mcp-webhook** - Job status management and web integration

## Contract Structure

Each contract file defines:

- **Purpose**: 1-2 sentence description of the server's role
- **Tools**: Available functions with input/output specifications
- **Resources**: Data sources and file access patterns
- **Error Codes**: Standardized error handling
- **Limits**: Security and performance constraints
- **Security**: Access controls and whitelisted operations

## Security Model

- **Whitelist Directories**: Only specific project directories are accessible
- **Write Restrictions**: Limited to `outputs/` directory for artifacts
- **Audit Trail**: All operations logged to `mcp-auditlog`
- **Resource Limits**: File size, processing time, and memory constraints
- **Isolation**: Sensitive data (OCR, SFTP) isolated in protected resources

## Integration Points

- **Host (Cursor)**: Provides the reasoning engine and tool orchestration
- **Backend Web**: Lightweight job queue and status management
- **Local AI**: Model inference for complex reasoning tasks
- **File System**: Structured access to project directories

## Usage

These contracts serve as the interface specification between:
- The local AI model (reasoning engine)
- MCP servers (tool/data bus)
- The web backend (job management)
- The file system (data persistence)

Each tool call is designed to be atomic, traceable, and secure within the audit context.
