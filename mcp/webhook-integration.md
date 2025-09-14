# MCP Webhook Integration

This document describes the webhook integration between MCP servers and the web backend for job status management and real-time progress tracking.

## Architecture Overview

The webhook integration provides a lightweight communication layer between:
- **MCP Servers**: Tool execution and data processing
- **Web Backend**: Job queue and status management
- **Frontend**: Real-time progress display and artifact access

## Job Status Model

### Status Definitions
```json
{
  "PENDING": "Job created, waiting to start",
  "RUNNING": "Job in progress",
  "NEEDS_INPUT": "Job requires user input",
  "FAILED": "Job failed with error",
  "DONE": "Job completed successfully"
}
```

### Job Data Structure
```json
{
  "job_id": "string (UUID)",
  "status": "PENDING|RUNNING|NEEDS_INPUT|FAILED|DONE",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp",
  "input_data": {
    "pop_file_path": "string",
    "pdf_directory": "string",
    "validation_mode": "string",
    "custom_rules": "object"
  },
  "progress": {
    "current_step": "string",
    "total_steps": "integer",
    "completed_steps": "integer",
    "percentage": "number (0-100)",
    "estimated_remaining": "string"
  },
  "artifacts": [
    {
      "name": "string",
      "path": "string",
      "type": "string",
      "size": "integer",
      "download_url": "string"
    }
  ],
  "metadata": {
    "user_id": "string",
    "session_id": "string",
    "processing_time": "number",
    "error_message": "string"
  }
}
```

## Web Backend API Endpoints

### 1. Job Creation
```http
POST /api/jobs
Content-Type: application/json

{
  "input_data": {
    "pop_file_path": "populacja/data.xlsx",
    "pdf_directory": "pdfs/",
    "validation_mode": "full"
  },
  "metadata": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "created_at": "2024-01-15T10:30:00Z",
  "message": "Job created successfully"
}
```

### 2. Status Updates (Webhook)
```http
POST /api/jobs/{job_id}/status
Content-Type: application/json

{
  "status": "RUNNING",
  "progress": {
    "current_step": "PDF Processing",
    "total_steps": 5,
    "completed_steps": 2,
    "percentage": 40,
    "estimated_remaining": "5 minutes"
  },
  "message": "Processing PDF files..."
}
```

### 3. Job Retrieval
```http
GET /api/jobs/{job_id}
```

**Response:**
```json
{
  "job": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "RUNNING",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z",
    "input_data": {...},
    "progress": {...},
    "artifacts": [...],
    "metadata": {...}
  },
  "history": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "status": "PENDING",
      "message": "Job created",
      "step": "initialization"
    },
    {
      "timestamp": "2024-01-15T10:32:00Z",
      "status": "RUNNING",
      "message": "Processing POP data",
      "step": "pop_processing"
    }
  ]
}
```

### 4. Job Completion
```http
POST /api/jobs/{job_id}/complete
Content-Type: application/json

{
  "final_status": "DONE",
  "summary": {
    "total_records_processed": 1500,
    "validation_issues_found": 23,
    "high_risk_records": 5,
    "processing_time": 180.5,
    "artifacts_generated": 4
  },
  "final_artifacts": [
    {
      "name": "audit_report.xlsx",
      "path": "outputs/reports/audit_report_20240115.xlsx",
      "type": "excel_report",
      "size": 2048576,
      "description": "Comprehensive audit report"
    },
    {
      "name": "evidence_package.zip",
      "path": "outputs/evidence/evidence_20240115.zip",
      "type": "evidence_package",
      "size": 15728640,
      "description": "Complete evidence package"
    }
  ],
  "completion_message": "Audit completed successfully"
}
```

## MCP Webhook Implementation

### mcp-webhook Server Configuration
```json
{
  "server": "mcp-webhook",
  "webhook_endpoints": {
    "base_url": "http://localhost:8000/api",
    "status_update": "/jobs/{job_id}/status",
    "job_retrieve": "/jobs/{job_id}",
    "job_complete": "/jobs/{job_id}/complete"
  },
  "authentication": {
    "type": "bearer_token",
    "token": "mcp_webhook_token_12345"
  },
  "retry_policy": {
    "max_retries": 3,
    "backoff_factor": 2,
    "timeout": "30s"
  }
}
```

### Webhook Call Examples

#### 1. Push Status Update
```python
# From mcp-webhook server
def push_status(job_id, status, progress=None, message=None):
    payload = {
        "status": status,
        "progress": progress,
        "message": message
    }

    response = requests.post(
        f"{base_url}/jobs/{job_id}/status",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )

    return response.json()
```

#### 2. Pull Job Details
```python
# From mcp-webhook server
def pull_job(job_id, include_history=False):
    params = {"include_history": include_history}

    response = requests.get(
        f"{base_url}/jobs/{job_id}",
        params=params,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )

    return response.json()
```

#### 3. Complete Job
```python
# From mcp-webhook server
def complete_job(job_id, final_status, summary=None, artifacts=None):
    payload = {
        "final_status": final_status,
        "summary": summary,
        "final_artifacts": artifacts
    }

    response = requests.post(
        f"{base_url}/jobs/{job_id}/complete",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )

    return response.json()
```

## Error Handling

### Webhook Error Codes
```json
{
  "E_JOB_NOT_FOUND": "Job not found in backend",
  "E_WEBHOOK_FAILED": "Failed to communicate with web backend",
  "E_INVALID_STATUS": "Invalid job status provided",
  "E_NETWORK_ERROR": "Network communication error",
  "E_TIMEOUT": "Webhook request timed out",
  "E_AUTHENTICATION_FAILED": "Authentication with backend failed",
  "E_SERIALIZATION_ERROR": "Data serialization error"
}
```

### Retry Logic
```python
def webhook_with_retry(func, *args, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(backoff_factor ** attempt)
        except requests.HTTPError as e:
            if e.response.status_code >= 500:
                # Server error, retry
                if attempt == max_retries - 1:
                    raise e
                time.sleep(backoff_factor ** attempt)
            else:
                # Client error, don't retry
                raise e
```

## Security Considerations

### Authentication
- Bearer token authentication for all webhook calls
- Token rotation and expiration
- Rate limiting per token

### Data Protection
- Encrypt sensitive data in webhook payloads
- Validate webhook signatures
- Sanitize input data

### Audit Trail
- Log all webhook communications
- Track webhook success/failure rates
- Monitor for suspicious patterns

## Monitoring and Metrics

### Key Metrics
- Webhook success rate
- Average response time
- Error rate by endpoint
- Job completion time
- Artifact generation time

### Alerts
- Webhook failure rate > 5%
- Average response time > 10s
- Job stuck in RUNNING status > 1 hour
- Authentication failures

## Testing

### Unit Tests
- Webhook payload validation
- Error handling scenarios
- Retry logic verification

### Integration Tests
- End-to-end job workflow
- Webhook communication
- Artifact delivery

### Load Tests
- Concurrent job processing
- Webhook rate limiting
- Database performance under load
