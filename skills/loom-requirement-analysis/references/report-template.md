# Report Template for Requirement Analysis

Adapt this template based on findings. Not all sections apply to every analysis.

## Template

```
# Requirement Analysis: [SWC Name or Requirement Name]

## Item Identity

| Field | Value |
|-------|-------|
| **Name** | [name] |
| **XID** | [xid] |
| **Type** | [SWC / Requirement / Container] |
| **Version** | [version] |
| **Baseline** | [baseline used] |
| **ECU** | [ECU name and XID] |
| **Cycle Time** | [e.g., 20 ms] |
| **Vehicle Modes** | [list of active modes] |
| **End-User Function** | [function name and ID] |
| **Pattern** | [Signal Conversion / Output Handler / Arbitration / etc.] |

## Purpose

[1-3 sentences: What does this SWC/requirement do? What is its role in the vehicle architecture?]

## Requirement Summary

[For SWC-level analysis: table of all child requirements with XID, name, one-line summary]
[For single requirement: detailed description of what the requirement specifies]

## Signal Inventory

### Input Signals
| Signal | XID | Source ECU | Bus | Frame | DB Match Quality |
|--------|-----|-----------|-----|-------|-----------------|
[rows]

### Output Signals
| Signal | XID | Destination ECU | Bus | Frame | DB Match Quality |
|--------|-----|----------------|-----|-------|-----------------|
[rows]

### Internal Signals -- FULLY RESOLVED

For EACH internal signal, show the complete chain from physical source to physical destination.
Do NOT just list the internal signal -- unwrap it.

| Internal Signal | XID | Producer Req | Consumer Req(s) | Resolution Status |
|-----------------|-----|-------------|-----------------|-------------------|
[rows -- one per internal signal]

For each internal signal listed above, provide a resolution block:

#### [Internal Signal Name] (XID: ...)

**Resolution**: [RESOLVED / PARTIALLY RESOLVED / UNRESOLVED]

**Producer**: Req-XXXX ([name], XID: ...) in [same SWC / other SWC name]
- Physical inputs to producer: [list the CAN/LIN signals that feed the producer requirement]
- Logic: [how does the producer compute this internal signal from its physical inputs?]

**Consumer(s)**: Req-YYYY ([name], XID: ...) in [same SWC / other SWC name]
- Physical outputs from consumer: [list the CAN/LIN signals the consumer produces]
- Logic: [how does the consumer use this internal signal to compute its physical outputs?]

**Full chain**:
```
[Physical Input Signal] (from [ECU] via [Bus])
    -> Req-XXXX ([producer name])
    -> [Internal Signal Name]
    -> Req-YYYY ([consumer name])
    -> [Physical Output Signal] (to [ECU] via [Bus])
```

**If UNRESOLVED**: State exactly what is unknown:
- "Producer not found: searched N results for signal name, found M _I variants but
  could not identify which SWC/requirement sets this signal"
- "Test implication: this signal must be stubbed/simulated; the producing SWC is unknown"

### Configuration Parameters (DOIDs)
| DOID | Name | Value Range | Default | Purpose |
|------|------|-------------|---------|---------|
[rows]

## Complete Signal Flow Map

This is the CORE deliverable. Show the full data flow including ALL resolved internal
signal chains. Use ASCII art:

```
[External ECU] --physical_signal--> [Req-A] --internal_signal--> [Req-B] --physical_signal--> [External ECU]
                                        ^                            ^
                                        |                            |
                            [External ECU] --physical_signal    [External ECU] --physical_signal
```

Include:
- Every physical input with its source ECU and bus
- Every internal signal chain with producer and consumer requirements
- Every physical output with its destination ECU and bus
- Cross-SWC internal signals marked with [CROSS-SWC] or [UNRESOLVED]

## Detailed Requirement Analysis

[For each requirement or for the target requirement:]

### [Req-XXXX: Name]

**Logic**: [Describe what the requirement does in clear technical language]

**Conditions/Truth Table**:
[Reconstruct the truth table or condition chain]

**Boundary Conditions**:
- [List specific threshold values, overflow points, timing constraints]

**Dependencies**:
- Depends on: [list signals/requirements this depends on]
- Depended on by: [list signals/requirements that depend on this]

## Cross-SWC Dependencies

| Signal | This SWC Role | Other SWC/ECU | Relationship |
|--------|--------------|---------------|--------------|
[rows showing signals that cross SWC boundaries]

## Ambiguities and Issues

### CRITICAL
- [List CRITICAL ambiguities that block test creation or correct implementation]

### HIGH
- [List HIGH severity ambiguities requiring clarification]

### MEDIUM
- [List MEDIUM severity documentation gaps]

### LOW
- [List LOW severity minor inconsistencies]

## Test Case Guidance

### Test Categories
1. **Nominal / Positive Path**: [describe what to test]
2. **Boundary Values**: [specific boundary calculations]
3. **Error Propagation**: [Error/NotAvailable input handling]
4. **Signal Loss**: [missing signal / timeout scenarios]
5. **Enable Gate Combinations**: [enable/disable permutations]
6. **Vehicle Mode**: [mode transitions, initial values]
7. **Timing**: [cycle time, timeout, delay verification]
8. **Configuration Variants**: [DOID parameter variations]

### Specific Test Cases
| TC# | Precondition | Input | Expected Output | Category |
|-----|-------------|-------|-----------------|----------|
[key test cases derived from the analysis]

### Test Setup Requirements
- [List required ECU simulators, CAN bus setup, internal signal stubs]
- [List configuration prerequisites (DOIDs, vehicle variant)]
- [List any dependencies on other SWCs being active]

## Unknowns and Open Questions

[Numbered list of things that could NOT be determined from the available data.
Each item should state what is unknown and why it matters.
Do NOT fill these with assumptions -- leave them as genuine open questions.]
```

## Adaptation Notes

- **For single requirement analysis**: Collapse the "Requirement Summary" section and expand "Detailed Requirement Analysis"
- **For huge SWCs (>50 reqs)**: Add a "Pattern Distribution" section showing how many requirements follow each pattern, and only detail representative examples
- **For container XIDs that cannot be resolved**: Replace most sections with an explanation of the limitation and what information could be obtained vs. what requires SE-Tool desktop client access
- **For cross-SWC dependency tracing**: Add a "Dependency Chain" section showing the full signal path across multiple SWCs
