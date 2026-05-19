# Summary Report

I built this report from the processed process records so the analysis is tied back to source IDs.

- Total records: 300

## Category Counts
- Battery Process Optimization: 50
- Materials Characterization: 50
- Manufacturing QA: 50
- Equipment Maintenance: 50
- Failure Analysis: 50
- Validation Testing: 50

## Record Type Counts
- experiment_note: 50
- qa_record: 50
- maintenance_log: 50
- failure_report: 50
- validation_summary: 50
- parameter_change: 50

## Top Failure Modes
- coating uniformity drift: 38
- thermal cycling impedance drift: 38
- increased defect rate: 38
- calibration offset: 38
- material batch inconsistency: 37
- sensor anomaly: 37
- yield loss: 37
- validation threshold miss: 37

## Validation Pass/Fail Distribution
- failed: 88
- warning: 71
- passed: 141

## Recurring Risks
- medium: 206
- high: 35
- low: 59

## Operational Insights
- Calibration drift, sensor anomalies, and equipment checks show up often enough that I would review maintenance cadence before changing process limits.
- Batch consistency and thermal cycling records give useful evidence for separating materials issues from process parameter issues.
- Failed validation records are most useful when paired with severity and root-cause hints because they show where to investigate first.

## Example Cited Records
- PKAI-0001: Battery Process Optimization experiment note 1 (process_notes/battery_process_optimization/experiment_note_0001.md)
- PKAI-0002: Materials Characterization qa record 2 (process_notes/materials_characterization/qa_record_0002.md)
- PKAI-0003: Manufacturing QA maintenance log 3 (process_notes/manufacturing_qa/maintenance_log_0003.md)
- PKAI-0004: Equipment Maintenance failure report 4 (process_notes/equipment_maintenance/failure_report_0004.md)
- PKAI-0005: Failure Analysis validation summary 5 (process_notes/failure_analysis/validation_summary_0005.md)
- PKAI-0006: Validation Testing parameter change 6 (process_notes/validation_testing/parameter_change_0006.md)
