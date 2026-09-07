# Common Ambiguities in Volvo SWC Requirements

Systematic catalog of ambiguity types found during requirement analysis.
Check each category when analyzing a requirement. Rate severity per finding.

## Severity Levels

- **CRITICAL**: Blocks test case creation or could lead to wrong implementation
- **HIGH**: Requires clarification for complete testing but partial testing possible
- **MEDIUM**: Documentation gap that should be fixed but workaround exists
- **LOW**: Minor inconsistency, unlikely to cause issues

## 1. Missing or Corrupted Comparison Operators

**Severity**: CRITICAL
**Description**: The `!=` (not-equal) operator is often stripped from requirement text, leaving conditions like `SignalA  ValueB` with no visible operator.
**How to detect**: Look for condition clauses where a signal name is followed by a space then a value with no operator between them.
**Impact**: Without knowing the operator, the condition logic is ambiguous. In most observed cases the intended operator is `!=` (not-equal), but this must be confirmed.
**Recommendation**: Check whether the condition makes logical sense with `!=`. If both `==` and `!=` could be valid interpretations, mark as CRITICAL unknown.

## 2. Unit Confusion in Descriptions

**Severity**: CRITICAL
**Description**: Requirement text states one unit (e.g., "seconds") but the signal computation defines a different unit (e.g., hours with resolution 0.05h). The multiplication factor in the requirement (e.g., *180) bridges the gap but the text is misleading.
**How to detect**: Compare the unit label in the requirement text against the computation type's resolution and physical unit. If they differ, the text is misleading.
**Impact**: A developer reading only the text (not the signal spec) may implement the wrong conversion.
**Recommendation**: Always cross-reference the signal computation type. Document the actual conversion: `raw * resolution * unit_factor`.

## 3. "Valid Signal Range" Referenced But Undefined

**Severity**: HIGH
**Description**: Requirements use phrases like "signal is within a Valid Signal Range" without defining what values constitute valid vs. invalid.
**How to detect**: Search for "valid signal range" or "valid range" in the requirement text and check if the range is defined (it usually is not).
**Impact**: Cannot determine which enum values to treat as valid for test cases.
**Recommendation**: Assume valid = all values except Error and NotAvailable, but mark this as [ASSUMPTION].

## 4. Signal Direction Metadata Unreliable

**Severity**: MEDIUM (for analysis), HIGH (for tool consumers)
**Description**: The `direction` field in SystemWeaver signal metadata may show "in" for all signals in a requirement/SWC, regardless of whether they are inputs, outputs, or internal.
**How to detect**: Check if all signals have the same direction. If all are "in" but the requirement clearly writes to some, the metadata is wrong.
**Impact**: Automated signal flow analysis based on metadata will be incorrect.
**Recommendation**: Determine actual direction from: (1) requirement text ("shall be set to" = output), (2) CAN DB transmitter/receiver roles, (3) naming conventions (PS_* = output, Chg* = input, Set* = output).

## 5. Fuzzy Database Matches Are Noise

**Severity**: MEDIUM
**Description**: Signal-to-CAN-database matching uses fuzzy string matching. Scores below ~80% typically match to completely unrelated signals (e.g., "EngTrueIdleSpeedFuel" matching "EngRatedSpeed" at 67%).
**How to detect**: Check the `match_score` in database_matches. Below 75-80% is usually a false positive.
**Impact**: Misleading information about signal routing if taken at face value.
**Recommendation**: Only trust exact matches (100%) or very high fuzzy matches (>90%). For lower scores, treat the CAN routing as UNKNOWN and note it explicitly.

## 6. Missing Error/NotAvailable Handling

**Severity**: HIGH
**Description**: Not all requirements specify what happens when input signals have Error or NotAvailable values. Some requirements handle these explicitly; others silently let them fall into "Otherwise" clauses.
**How to detect**: Check if the requirement has explicit conditions for Error/NotAvailable input values. Compare against sibling requirements that do handle them.
**Impact**: Inconsistent error propagation behavior. Test cases may miss fault scenarios.
**Recommendation**: If sibling requirements in the same SWC handle Error/NA explicitly, flag any requirement that does not as a potential gap. Test what actually happens with Error/NA inputs.

## 7. "Don't Care" in Truth Tables

**Severity**: MEDIUM
**Description**: Truth tables use "Don't care" for certain input columns, meaning any value is acceptable. However, "Don't care" is not a defined enum value.
**How to detect**: Look for "Don't care", "X", or "-" in truth table cells.
**Impact**: For test completeness, "Don't care" should be expanded to include all possible values including Error, NotAvailable, Spare, and signal-missing states.
**Recommendation**: In test cases, verify "Don't care" with at least: one normal value, Error, NotAvailable, and signal-missing.

## 8. "Signal Missing" Without Formal Definition

**Severity**: HIGH
**Description**: Requirements reference "signal missing" as a condition but do not define the timeout or mechanism for detecting signal loss.
**How to detect**: Search for "missing" or "signal missing" in requirement text and check for corresponding timeout parameters.
**Impact**: Cannot write accurate test cases for signal loss scenarios without knowing the timeout value.
**Recommendation**: Note as UNKNOWN. Check if there is a global signal-loss timeout configuration for the ECU. For CAN signals, the frame cycle time + a typical 3x tolerance is common but must not be assumed.

## 9. Undefined Default/Initial Values

**Severity**: HIGH
**Description**: Some requirements specify initial values at vehicle mode entry but others do not. For outputs that are read by other systems, the initial value before first computation matters.
**How to detect**: Check if the requirement specifies behavior for mode entry or first-cycle execution. If not, check the signal computation for a default value.
**Impact**: Undefined initial values can cause transient incorrect behavior during startup.
**Recommendation**: If other requirements in the SWC specify initial values but this one does not, flag as a gap. [ASSUMPTION] initial value is 0/Inactive/NoRequest unless stated otherwise.

## 10. Asymmetric Enable/Gate Conditions

**Severity**: MEDIUM
**Description**: Requirements in the same SWC may have different enable conditions without explanation (e.g., one needs a master + feature enable, another needs only the master enable).
**How to detect**: Compare the enable/gate conditions across all sibling requirements.
**Impact**: Testing must account for partial-enable scenarios. The asymmetry may be intentional (optional equipment gating) or an oversight.
**Recommendation**: Note the asymmetry. Check if the extra gate corresponds to optional equipment.

## 11. Missing Configuration Values

**Severity**: HIGH
**Description**: Thresholds, timeouts, and parameter values are referenced by name but no numeric value is provided in the requirement or signal definition.
**How to detect**: Look for parameter names like `TimeoutXxx`, `ThresholdXxx` in requirement text and check if a value is defined in the signal or parameter specs.
**Impact**: Cannot calculate boundary values for test cases without the actual configured value.
**Recommendation**: Look up via DOID if a DOID code is referenced. Otherwise note as UNKNOWN with the parameter name so the value can be obtained from the calibration/configuration team.

## 12. "Should" vs "Shall" Obligation Level

**Severity**: LOW
**Description**: Requirements mix "should" (recommendation) and "shall" (mandatory) language. In formal requirements engineering, "shall" = must implement, "should" = nice to have.
**How to detect**: Search for "should" in requirement text. If the SWC otherwise uses "shall", a "should" may be an error.
**Impact**: May affect test priority. A "should" requirement might be deprioritized or interpreted as optional.
**Recommendation**: Flag for review by requirements author. For test purposes, treat as "shall" unless explicitly told otherwise.

## 13. Inconsistent Enum Value Naming

**Severity**: MEDIUM
**Description**: The same logical value may have different names across requirements or between requirement text and signal enum definitions (e.g., "OverspeedMenu" in text vs "AdjustOverspeed" in enum definition).
**How to detect**: Compare value names used in requirement conditions against the signal's enum definition.
**Impact**: Mapping confusion during implementation. Test cases may use wrong values.
**Recommendation**: Document both names and note which is the canonical enum value from the signal definition.

## 14. Unexplained _Info Duplicate Signals

**Severity**: LOW
**Description**: Some output signals are duplicated with an `_Info` suffix carrying identical values. The purpose of the duplicate is not documented.
**How to detect**: Look for pairs of signals where one has `_Info` appended and both are set to the same value.
**Impact**: Minor -- both must be tested for equality, but the purpose is unclear.
**Recommendation**: Note as documentation gap. May serve different CAN routing or different consumers.

## 15. Empty or Placeholder Descriptions

**Severity**: MEDIUM
**Description**: SWC-level descriptions, signal descriptions, or computation descriptions may be empty or contain placeholder text like "TBD".
**How to detect**: Check description fields for empty strings, "TBD", or single-word placeholders.
**Impact**: Missing context for understanding purpose and constraints.
**Recommendation**: Flag for documentation update. Use the signal name and surrounding context to infer purpose.

## 16. Requirements Referencing Signals Not In Their Signal List

**Severity**: HIGH
**Description**: A requirement's text may reference signals that are not in its attached signal list. This occurs when the signal is managed at the SWC level rather than the requirement level, or when the signal attachment is simply missing.
**How to detect**: Parse signal names from the requirement text and compare against the attached signal list.
**Impact**: The signal may come from a different requirement or SWC, creating an undocumented dependency.
**Recommendation**: Search for the signal across the SWC's other requirements to find where it is attached.

## 17. CAN Bus Loopback / Self-Referencing Signals

**Severity**: HIGH
**Description**: A signal marked `direction="in"` has a CAN database match where the host ECU (e.g., IC3) is the TRANSMITTER. This means the SWC reads back its own CAN output. This is not an external input -- it is a feedback loop through the CAN bus. Alternatively, a signal may appear as both input and output on the same requirement (self-referencing composite signal like PS_DriverCoachNotific).
**How to detect**: For each "input" signal, check if the DB match transmitter is the same ECU the SWC runs on. Also check if a signal marked "out" is also used as an input condition in the requirement description.
**Impact**: Creates temporal dependency on CAN bus cycle time. Test setup must account for the round-trip delay. The signal is NOT independent of the SWC -- it is produced by the SWC or a sibling SWC on the same ECU.
**Recommendation**: Document the feedback path explicitly. Note the CAN frame and cycle time. Mark the signal as LOOPBACK in the signal classification, not as a physical input. For test cases, verify behavior across CAN cycle boundaries.

## 18. Duplicate XIDs for Logically Same Signal

**Severity**: CRITICAL
**Description**: The same logical signal (e.g., "Internal Harsh Braking Counter") appears with DIFFERENT XIDs in different requirements. This raises the question of whether the requirements are operating on the same data or on independent copies.
**How to detect**: Compare signal NAMES across sibling requirements. If the same name appears with different XIDs, flag it.
**Impact**: If the XIDs represent different signals, the counter in the Status requirement may not be the same counter reset by the Initialize requirement, breaking the system.
**Recommendation**: Flag as CRITICAL for review. Verify in SE-Tool desktop client whether these are aliases for the same physical memory or separate instances.

## 19. Multi-Requirement Read-Write on Same Internal Signal

**Severity**: HIGH
**Description**: An internal signal is written by more than one requirement (e.g., TimeSinceLastAccEvent is incremented by the Counter requirement, reset by the Status requirement, AND reset by the Initialize requirement). The execution order of requirements within a cycle determines the final value.
**How to detect**: For each internal signal, list ALL requirements that WRITE to it (not just read). If more than one writes, flag it.
**Impact**: Behavior depends on requirement execution order within the SWC's cycle. If Counter runs before Status, the timer increments then gets reset. If Status runs first, the reset happens then the timer increments. This may or may not be specified.
**Recommendation**: Document all writers and note the execution order dependency. If execution order is not specified, mark as a potential race condition.

## 20. Implicit State Machine Without Named States

**Severity**: MEDIUM
**Description**: The requirement does not define named states, but the combination of boolean flags, timer values, and counter values creates implicit states (e.g., IDLE when CounterSts=FALSE and Timer=0, CONFIRMING when CounterSts=TRUE and Timer>0). The state is distributed across multiple internal signals rather than encoded in a single state variable.
**How to detect**: Look for requirements with multiple boolean flags, timers, and conditional logic that branches based on combinations of these flags. If you can construct a state table from the combinations, it's an implicit state machine.
**Impact**: Testing requires understanding the full state space (all combinations of flags/timers). The number of implicit states grows combinatorially with the number of flags/timers. Some combinations may be unreachable but this is not documented.
**Recommendation**: Reconstruct the implicit state machine. List all reachable states, all transitions with their trigger conditions, and all outputs per state. Flag any state combinations that appear unreachable but are not explicitly excluded.

## 21. Shared Output Signal Without Arbitration Rule

**Severity**: CRITICAL
**Description**: Multiple requirements within the same SWC all write to the same output signal (e.g., PS_DriverCoachNotific written by 6 requirements). No arbitration rule specifies which requirement wins when multiple fire simultaneously.
**How to detect**: Check if any output signal XID appears in the signal lists of multiple sibling requirements.
**Impact**: Undefined behavior when multiple events occur simultaneously. The physical CAN signal can only carry one value per cycle.
**Recommendation**: Flag as CRITICAL. Test with simultaneous events to observe actual behavior. Document the gap for the requirements author.

## 22. Timer/Queue Parameter Values Not Specified

**Severity**: HIGH
**Description**: Timer limits (e.g., TimeInHAccQueueMax, EventTimeThresholdAcc) and queue timeout values are referenced as internal signals but have no description, no unit, no default value, and no DOID reference. They are configurable parameters imported from some external source (e.g., Back Office) but their actual values are opaque.
**How to detect**: Internal signals with names like *TimerLimit, *Max, *Threshold, *QueueMax that have null computation specs and null descriptions.
**Impact**: Cannot calculate boundary values for test cases. Cannot verify timer accuracy without knowing the expected duration.
**Recommendation**: Document the parameter name and request the value from the calibration/configuration team. For test cases, note the parameter as a test prerequisite.
