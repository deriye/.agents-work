# Requirement Patterns in Volvo SWCs

Catalog of patterns observed across SE-TOOL/SystemWeaver Software Components.
Identifying the pattern helps focus analysis and test case strategy.

## Pattern 1: Signal Conversion / Mapping (Truth Table)

**Example SWC**: SWSpeedControlConversion_Ctrl
**Characteristics**:
- One multiplexed input signal demultiplexed into multiple discrete outputs
- Each requirement handles a subset of input enum values
- Conditional gating by secondary signals (mode, state, enable)
- Explicit Error/NotAvailable pass-through on every requirement
- "Otherwise" default clause on every requirement
- Requirements are mutually exclusive in output signals

**Test approach**: Truth table coverage. Primary axis = input enum values, secondary axes = gating signals. Test every cell combination plus Error/NA propagation.

**Watch for**:
- Missing `!=` operators in condition text (common rendering issue)
- Overlapping input handling between requirements (e.g., Increase/Decrease handled by two reqs with complementary gating)
- Internal signal chains between requirements (one writes an internal signal, another reads it)

## Pattern 2: Output Handler (Threshold + Presentation)

**Example SWC**: AuxiliaryBrakes_OHdlr
**Characteristics**:
- CAN bus input signals compared against thresholds
- Output is a `PS_*` (Presentation Signal) consumed by display layer
- Enable gates control activation (master enable + optional feature enable)
- Timer-based delayed transitions (icon remove timeout)
- Initial values specified at vehicle mode entry
- Signal-missing -> NotAvailable handling

**Test approach**: Boundary value testing at threshold. Timer accuracy verification. Enable gate combinations. Initial value at mode transitions. Signal loss/timeout scenarios.

**Watch for**:
- Missing threshold values (configuration parameters with no documented default)
- Missing timeout values (timer parameters undefined)
- Asymmetric enable conditions across requirements (some need extra gates)
- Counterintuitive threshold direction (negative braking torque = more braking)
- Undefined behavior when enable is Inactive

## Pattern 3: Arbitration / Priority Logic

**Example SWC**: TrafficSituationControl
**Characteristics**:
- Multiple input sources (physical request + GUI request)
- Priority-based merging: primary input wins, secondary is fallback
- Purely combinational logic (no state, no timers)
- Often single-requirement SWCs
- Small signal count (2-3 inputs, 1 output)

**Test approach**: Full truth table with all input combinations. Focus on priority override verification. "Don't care" cells must be tested with all possible values. Signal-missing path validation.

**Watch for**:
- All signals marked direction="in" even though one is the output
- Input signals with no exact CAN DB match (may be internal/application-layer)
- Empty SWC description
- No explicit Error/NotAvailable handling (falls into "any other value" bucket)

## Pattern 4: Data Adaptation / Unit Conversion

**Example SWC**: EngineDataConversion_Ctrl
**Characteristics**:
- Raw J1939 CAN signals converted to different resolution/unit
- Clamp-or-NotAvailable pattern: pass through if within range, else NotAvailable
- Resolution narrowing (coarser input -> finer output)
- Some outputs duplicated with `_Info` suffix (purpose unclear)
- Flat hierarchy, uniform structure

**Test approach**: Boundary value at overflow point (calculate exact raw value where multiplication exceeds target max). Conversion accuracy verification. Zero-value test. `_Info` signal consistency check.

**Watch for**:
- Misleading unit labels (input described in seconds but computation says hours)
- The multiplication factor (e.g., *180) hiding a unit conversion (raw * resolution_factor * unit_conversion)
- `_Info` signals with no documented purpose
- No error/timeout/initialization behavior specified
- Output signals with no CAN DB match (may be internal to ECU)

## Pattern 5: Configuration / Settings Management

**Example SWC**: CommonHmiSettings_B2
**Characteristics**:
- Internal configuration parameters (defaults for units, language, display modes)
- Fallback logic (what to use when no stored value exists)
- Personal vs global settings distinction
- Vehicle-variant overrides (e.g., LNG vehicles remap units)
- Active across many vehicle modes (including living, accessory)
- Configuration parameters referenced by DOID codes

**Test approach**: Default value verification (gap: many defaults undocumented). Fallback trigger scenarios (new driver card, no stored value). Language fallback chain. Personal vs global persistence across driver changes. Vehicle-variant overrides (LNG mode).

**Watch for**:
- Missing output signals (settings "communicated" but no output signals defined)
- Incomplete default value specifications
- Empty signal descriptions
- "Should" vs "Shall" obligation level
- Informal DOID references in text (not linked in parameters field)
- Language enum discrepancies between DOID definitions and signal enums

## Pattern 6: Fault-to-DTC Mapping

**Example SWC**: DWMDTCMonitor_B2_Mgr (145 requirements)
**Characteristics**:
- Massive requirement count but highly repetitive
- Most requirements: IF fault_condition THEN set NPPId = specific_ID
- Central output signal (DWMDTCStatChange) shared by majority of requirements
- Dual-path pattern: Diagnostic path (sets fault status) + Function path (triggers display)
- Parameter-gated by "ECU Installed" DOIDs
- Feedback queue requirements aggregate all fault signals
- Grace period / startup logic

**Test approach**: For individual fault-to-DTC: inject specific fault, verify correct NPPId. For the aggregate queue: inject multiple simultaneous faults, verify cycling. For loss-of-comm: simulate ECU communication loss, verify detection after grace period. Parameter gating: verify no detection when ECU not configured as installed.

**Watch for**:
- Requirements with only Diagnostic path but no Function path (or vice versa)
- The feedback queue requirements are structurally different from the rest (aggregation vs. simple mapping)
- Grace period timing before fault detection activates
- Different timeout values for "slower ECUs"

## Pattern 7: Timer-Based Pipeline with Implicit State Machine

**Example SWC**: DriverCoaching_Ctrl (13 requirements)
**Characteristics**:
- Requirement PAIRS working in tandem: a "Counter" requirement detects events,
  a "Status" requirement confirms and produces output
- Edge detection: rising/falling edge on physical signal crossing a threshold
  (previous cycle vs current cycle comparison)
- Cooldown timer: minimum time between events (prevents rapid re-triggering)
- Confirmation timer: event must be sustained for a duration to count
- Abort conditions: if the event condition drops during confirmation, the timer
  resets and the event is discarded
- Multiple internal signals shared between the pair: timer value, counter status
  flag, cooldown timer, event counter
- An Initialize requirement resets ALL counters/timers on vehicle mode transition
- CAN bus feedback loop: the SWC reads back its own physical output signal (e.g.,
  PS_HarshAcceleration) to trigger cooldown reset -- creating temporal CAN dependency

**Implicit states** (no named states in the spec, but the combination of flags/timers
creates these):
- IDLE: CounterSts=FALSE, Timer=0, CooldownValid=TRUE -- waiting for threshold crossing
- COOLDOWN: CounterSts=FALSE, Timer=0, CooldownValid=FALSE -- too soon after last event
- CONFIRMING: CounterSts=TRUE, Timer running -- threshold crossed, awaiting confirmation
- CONFIRMED: Timer >= Limit (momentary) -- event counted, transitions to COOLDOWN
- ABORTED: Timer reset, CounterSts=FALSE -- conditions not sustained during confirmation

**Internal signal chain** (CRITICAL to resolve):
```
Physical Inputs (acceleration, speed, brake pedal, etc.)
  |
  v
Counter Requirement:
  writes: HarshAccTimer (timer), HarshAccCounterSts (boolean flag),
          TimeSinceLastAccEvent (cooldown), AccTimeValidStatus (derived flag)
  |
  v (internal signals bridge the two requirements)
  |
Status Requirement:
  reads: HarshAccTimer, HarshAccCounterSts
  writes: Internal Harsh Acceleration Counter (running total)
  writes: PS_HarshAcceleration (physical CAN output)
  |
  v
CAN Bus Output -> Loopback Read -> Resets TimeSinceLastAccEvent (feedback)
```

**Multiple internal signals per chain**: Unlike simple patterns where one internal signal
bridges two requirements, this pattern has 3-5 internal signals between the pair. EACH
must be traced: timer, counter status flag, cooldown timer, event counter, validity flag.

**Pattern is replicated across domains**: The same Counter+Status pair pattern repeats
for each domain (acceleration, braking, cornering, speeding, coasting, EcoRoll) with
domain-specific variations (2-level vs 3-level output, different guard conditions).

**Test approach**:
- State transition coverage: test all implicit state transitions
  (IDLE->CONFIRMING->CONFIRMED, IDLE->CONFIRMING->ABORTED, CONFIRMED->COOLDOWN->IDLE)
- Edge detection: verify exact cycle where threshold crossing is detected
- Timer boundary: test at exactly TimerLimit-1 cycle (not yet), TimerLimit (fires),
  TimerLimit+1 (already fired)
- Cooldown accuracy: verify minimum time between events
- Abort scenarios: drop below threshold at various points during confirmation timer
- Guard condition combinations: cruise control active during detection, invalid signals
- Counter rollover: what happens at max counter value?
- Initialization: verify all counters/timers reset on Cranking->Running transition
- Feedback loop timing: verify CAN round-trip latency for loopback signals
- Multiple simultaneous events across domains: all 6 domains detecting events at once

**Watch for**:
- Duplicate XIDs for what should be the same internal counter signal (e.g., Internal
  Harsh Braking Counter appears with 2 different XIDs in different requirements)
- Loopback signals: direction="in" but CAN DB shows the host ECU as transmitter --
  this means the SWC reads its own output, NOT an external signal
- Missing signal in requirement text: EngineSpeed listed as signal but not referenced
  in description
- Asymmetric output levels: some domains binary (Active/Inactive), others multi-level
  (NoWarning/Moderate/Critical) -- different toast parameter structures
- Initialize requirement touches ALL domains: single point of failure for all counters

## Pattern 8: Workload-Gated Event Queue (HMI Presentation Layer)

**Example SWC**: DriverCoaching *_to_HMI requirements (6 requirements under parent x04000000008D1972)
**Characteristics**:
- Sits DOWNSTREAM of an event-detection SWC (Pattern 7), consuming its output signals
- Three-stage pipeline per domain: Input Decode -> Workload-Gated Queue -> Output Hold
- Stage 1 (Input Decode): Priority-based lookup table mapping event signal + active
  notification ID -> internal state variable
- Stage 2 (Workload Gate): If driver workload is high (CurrentWorkload.TotalValue < 9),
  events are QUEUED with a timeout timer. If workload is low (>= 9), events pass through
  immediately. When workload drops and event is still valid (timer not expired), event is
  released from queue.
- Stage 3 (Output Hold): Once output goes active, it holds for exactly 500ms then resets
- Each requirement has its OWN isolated set of internal signals (no cross-requirement
  internal chains within this SWC)
- Self-referencing composite signal: PS_DriverCoachNotific is BOTH input and output
  on every requirement (feedback loop for notification arbitration)
- Notification IDs per event type (e.g., HarshAcc=21, HarshBrk=22/23, etc.)

**Multi-SWC pipeline** (CRITICAL to document):
```
DriverCoaching_Ctrl (Pattern 7)
  produces: HarshAcceleration, HarshBraking, etc. (CAN bus)
      |
      v
*_to_HMI SWC (Pattern 8)
  consumes: HarshAcceleration, HarshBraking, etc.
  consumes: CurrentWorkload (from workload manager SWC -- separate)
  produces: PS_HarshAcceleration, PS_HarshBraking, etc. (to HMI display)
  produces: PS_DriverCoachNotific (shared notification bus, self-referenced)
```

**Test approach**:
- Workload threshold boundary: events at exactly TotalValue=8 (queued) vs 9 (immediate)
- Queue timeout: event queued, workload stays high, timer expires -> event discarded
- Queue release: event queued, workload drops before timeout -> event released
- 500ms output hold accuracy: verify hold duration, verify reset after hold
- Hold + re-trigger: new event during 500ms hold period
- Workload transition during pipeline: workload changes mid-processing
- Multiple simultaneous events: two domains fire at same time, verify PS_DriverCoachNotific
  arbitration (SPEC GAP: no arbitration rule defined)
- Change detection (Coasting/EcoRoll only): same severity repeated -> must NOT re-trigger
- Notification ID correctness: verify correct ID per event type and severity
- End-to-end with upstream SWC: harsh event detection -> CAN output -> HMI queue -> display

**Watch for**:
- Missing comparison operator in workload check (common spec defect)
- PS_DriverCoachNotific arbitration gap: all 6 requirements write to it, no priority rule
- Timer units not specified (ms? seconds? cycles?)
- Self-referencing signal: PS_DriverCoachNotific as both input and output -- is this
  CAN loopback or internal routing?
- "Set to last valid value" with no defined initial value
- Typos in signal names (e.g., "PreviousInternalCoastinEv" missing 'g')

## Pattern 9: Multi-SWC Pipeline System

**Not a single-SWC pattern** but a system-level pattern where multiple SWCs form a
processing chain. Each SWC follows one of the above patterns but they connect via
CAN bus signals.

**Example**: DriverCoaching system
```
SWC 1: DriverCoaching_Ctrl (Pattern 7 - event detection)
  -> CAN bus signals (HarshAcceleration, HarshBraking, etc.)
SWC 2: *_to_HMI (Pattern 8 - workload-gated presentation)
  -> CAN bus signals (PS_HarshAcceleration, PS_DriverCoachNotific)
SWC 3: [Unknown display SWC] consumes PS_* signals
```

**How to detect**: When analyzing an SWC, if its input signals are NOT from external
ECUs but rather from the SAME ECU (IC3 transmitting and IC3 receiving on the same
CAN frame), this indicates an intra-ECU multi-SWC pipeline. The signals travel through
the CAN bus as physical signals but logically they're SWC-to-SWC communication.

**Analysis approach**:
1. Identify the full pipeline by tracing signals upstream and downstream
2. Analyze each SWC in the pipeline independently
3. Document the CAN bus interface between SWCs as the pipeline boundary
4. Note timing implications: CAN bus round-trip adds latency between SWCs
5. Note that testing one SWC in isolation requires stubbing the upstream/downstream

## Pattern Recognition Checklist

When analyzing a new requirement, check:
1. Does it have a truth table or if/then/else mapping? -> Pattern 1 or 3
2. Does it compare against a threshold? -> Pattern 2
3. Does it multiply/convert units with overflow clamping? -> Pattern 4
4. Does it manage stored settings with defaults/fallbacks? -> Pattern 5
5. Does it set an NPPId or DTC? -> Pattern 6
6. Does it have timers, edge detection, cooldown, confirmation? -> Pattern 7
7. Does it have workload gating, event queuing, output hold? -> Pattern 8
8. Do its inputs come from the SAME ECU it runs on? -> Pattern 9 (pipeline)
9. Is the SWC name suffixed with `_Ctrl`? -> Usually Pattern 1, 4, or 7
10. Is the SWC name suffixed with `_OHdlr`? -> Usually Pattern 2
11. Is the SWC name suffixed with `_Mgr`? -> Usually Pattern 5 or 6
12. Does the SWC have Counter/Status requirement PAIRS? -> Pattern 7
13. Does the SWC name contain "HMI" or "to HMI"? -> Pattern 8
14. Are there 3+ internal signals between two requirements? -> Pattern 7 (pipeline pair)
