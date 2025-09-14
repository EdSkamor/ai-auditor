# MCP-Auditor Rules Dictionary

This dictionary provides detailed descriptions of all validation rules available in the MCP-Auditor system, organized by category and severity.

## Rule Categories

### 1. Invoice Rules (`invoice_rules`)

#### Duplicate Numbers (`duplicate_numbers`)
- **ID**: `INV_DUP_001`
- **Severity**: High
- **Description**: Detects duplicate invoice numbers within the dataset
- **Example**: Two invoices with number "FV/2024/001"
- **Action**: Flag for manual review

#### Suspicious Endings (`suspicious_endings`)
- **ID**: `INV_SUS_002`
- **Severity**: Medium
- **Description**: Identifies invoices with suspicious number endings
- **Patterns**: `.99`, `.00`, `.01`
- **Example**: Invoice number "FV/2024/001.99"
- **Action**: Review for potential manipulation

#### Serial Invoices (`serial_invoices`)
- **ID**: `INV_SER_003`
- **Severity**: Medium
- **Description**: Flags excessive consecutive invoices on the same day
- **Threshold**: More than 5 consecutive invoices
- **Example**: 6 invoices issued on 2024-01-15
- **Action**: Verify business justification

#### Amount Mismatch (`amount_mismatch`)
- **ID**: `INV_AMT_004`
- **Severity**: High
- **Description**: Detects discrepancies between net, VAT, and gross amounts
- **Calculation**: `gross = net + VAT`
- **Tolerance**: 0.01 PLN
- **Action**: Recalculate and verify

#### Currency Check (`currency_check`)
- **ID**: `INV_CUR_005`
- **Severity**: Medium
- **Description**: Validates supported currencies
- **Allowed**: PLN, EUR, USD
- **Action**: Convert or reject unsupported currencies

### 2. KSeF Rules (`ksef_rules`)

#### UUID Check (`uuid_check`)
- **ID**: `KSEF_UUID_001`
- **Severity**: High
- **Description**: Validates KSeF UUID format and uniqueness
- **Format**: Standard UUID v4
- **Action**: Verify with KSeF system

#### Offline Invoices (`offline_invoices`)
- **ID**: `KSEF_OFF_002`
- **Severity**: Medium
- **Description**: Flags invoices not submitted to KSeF
- **Indicator**: Missing KSeF UUID
- **Action**: Verify offline status justification

#### Corrections (`corrections`)
- **ID**: `KSEF_COR_003`
- **Severity**: High
- **Description**: Identifies correcting invoices
- **Indicator**: Correction flag or reference to original
- **Action**: Verify original invoice and correction reason

#### Correction Notes (`correction_notes`)
- **ID**: `KSEF_NOTE_004`
- **Severity**: High
- **Description**: Flags correction notes
- **Indicator**: Note type in KSeF
- **Action**: Verify correction documentation

### 3. Contractor Rules (`contractor_rules`)

#### NIP Validation (`nip_validation`)
- **ID**: `CON_NIP_001`
- **Severity**: High
- **Description**: Validates Polish NIP (Tax ID) format and checksum
- **Format**: 10 digits with checksum validation
- **Action**: Verify with official NIP database

#### IBAN Validation (`iban_validation`)
- **ID**: `CON_IBAN_002`
- **Severity**: High
- **Description**: Validates IBAN format and checksum
- **Format**: Country code + 2 check digits + account number
- **Action**: Verify with bank system

#### Duplicate IBAN (`duplicate_iban`)
- **ID**: `CON_IBAN_DUP_003`
- **Severity**: Medium
- **Description**: Detects same IBAN used by different contractors
- **Action**: Verify contractor identity

#### VAT Whitelist (`vat_whitelist`)
- **ID**: `CON_VAT_004`
- **Severity**: High
- **Description**: Checks contractor against VAT whitelist
- **Source**: Official VAT whitelist API
- **Action**: Verify contractor registration status

#### VIES Check (`vies_check`)
- **ID**: `CON_VIES_005`
- **Severity**: Medium
- **Description**: Validates EU contractor VAT numbers
- **Source**: VIES system
- **Action**: Verify EU contractor status

### 4. Date Rules (`date_rules`)

#### Weekend Check (`weekend_check`)
- **ID**: `DATE_WEEK_001`
- **Severity**: Low
- **Description**: Flags documents issued on weekends
- **Days**: Saturday, Sunday
- **Action**: Verify business justification

#### Holiday Check (`holiday_check`)
- **ID**: `DATE_HOL_002`
- **Severity**: Low
- **Description**: Flags documents issued on holidays
- **Source**: Polish holiday calendar
- **Action**: Verify business justification

#### Future Date (`future_date`)
- **ID**: `DATE_FUT_003`
- **Severity**: Medium
- **Description**: Detects documents with future dates
- **Tolerance**: 0 days
- **Action**: Verify date accuracy

#### Old Date (`old_date`)
- **ID**: `DATE_OLD_004`
- **Severity**: Medium
- **Description**: Flags very old documents
- **Threshold**: More than 365 days old
- **Action**: Verify document relevance

### 5. Time Rules (`time_rules`)

#### Unusual Hours (`unusual_hours`)
- **ID**: `TIME_UNUS_001`
- **Severity**: Low
- **Description**: Flags documents issued outside business hours
- **Hours**: 08:00 - 18:00
- **Action**: Verify business justification

### 6. Sampling Rules (`sampling_rules`)

#### Sample Method (`method`)
- **ID**: `SAMP_METH_001`
- **Severity**: Info
- **Description**: Defines sampling methodology
- **Options**: random, stratified, mus
- **Default**: random

#### Sample Size (`sample_size`)
- **ID**: `SAMP_SIZE_002`
- **Severity**: Info
- **Description**: Defines sample size for audit
- **Default**: 100 records
- **Action**: Adjust based on population size

#### Stratification (`stratification`)
- **ID**: `SAMP_STRAT_003`
- **Severity**: Info
- **Description**: Defines stratification criteria
- **Fields**: amount, contractor
- **Bins**: 5
- **Action**: Ensure representative sampling

## Rule Configuration

### Enabling/Disabling Rules
```yaml
# In rules.yaml
invoice_rules:
  duplicate_numbers:
    enabled: true
    severity: "high"
  suspicious_endings:
    enabled: false  # Disable this rule
```

### Custom Rule Parameters
```yaml
# Customize rule behavior
tolerances:
  amount:
    max_difference: 0.01  # 1 grosz tolerance
  date:
    max_days_difference: 1  # 1 day tolerance
```

### Rule Severity Levels
- **Critical**: System errors, data corruption
- **High**: Business rule violations, compliance issues
- **Medium**: Potential issues, best practice violations
- **Low**: Informational, minor deviations
- **Info**: Configuration, methodology

## Rule Execution

### Validation Modes
1. **Full Audit**: All rules enabled
2. **Preselection**: High-severity rules only
3. **Revalidation**: Specific rule sets for follow-up

### Rule Dependencies
Some rules depend on others:
- `amount_mismatch` requires `currency_check`
- `vat_whitelist` requires `nip_validation`
- `vies_check` requires EU contractor identification

### Performance Considerations
- High-severity rules run first
- Expensive rules (API calls) run last
- Rules can be parallelized where possible
- Caching reduces repeated API calls

## Custom Rule Development

### Rule Template
```python
def custom_rule(record, context):
    """
    Custom validation rule template

    Args:
        record: Data record to validate
        context: Validation context and configuration

    Returns:
        dict: Rule result with severity and message
    """
    result = {
        "rule_id": "CUSTOM_001",
        "severity": "medium",
        "passed": True,
        "message": "",
        "details": {}
    }

    # Rule logic here
    if condition:
        result["passed"] = False
        result["message"] = "Rule violation description"
        result["details"] = {"field": "value"}

    return result
```

### Rule Registration
```yaml
# In rules.yaml
custom_rules:
  custom_001:
    enabled: true
    severity: "medium"
    description: "Custom business rule"
    parameters:
      threshold: 1000
      field: "amount"
```

## Rule Testing

### Test Data Requirements
- Valid records (should pass)
- Invalid records (should fail)
- Edge cases (boundary conditions)
- Error conditions (malformed data)

### Test Execution
```bash
# Run rule tests
python -m pytest tests/test_rules.py -v

# Test specific rule
python -m pytest tests/test_rules.py::test_duplicate_numbers -v
```

### Rule Coverage
- All rules must have test cases
- Test both positive and negative scenarios
- Verify error handling
- Check performance impact

## Rule Maintenance

### Regular Updates
- Review rule effectiveness monthly
- Update thresholds based on experience
- Add new rules for emerging issues
- Deprecate obsolete rules

### Performance Monitoring
- Track rule execution times
- Monitor false positive rates
- Optimize slow rules
- Balance accuracy vs. performance

### Documentation Updates
- Update rule descriptions
- Add new examples
- Document configuration changes
- Maintain change log
