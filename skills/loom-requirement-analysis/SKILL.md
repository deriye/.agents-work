---
name: loom-requirement-analysis
description: "Deep analysis of SE-TOOL/SystemWeaver requirements and Software Components (SWCs) using Loom MCP tools. Use this skill when the user wants to: (1) analyze a requirement or SWC from SE-TOOL/SystemWeaver given an XID or swap:// URL, (2) understand what a requirement does for test case creation or development, (3) trace signal dependencies across SWCs, (4) identify ambiguities or gaps in requirement specifications, (5) get a full picture of a requirement including its inputs, outputs, boundary conditions, related requirements, and cross-SWC signal chains. Triggers on mentions of: requirement analysis, XID, swap:// URLs, SE-TOOL, SystemWeaver, SWC analysis, DOID parameters, test case derivation from requirements, signal tracing, requirement dependencies."
---

# Loom Requirement Analysis

Analyze SE-TOOL/SystemWeaver requirements and SWCs to produce comprehensive reports
for test case creation or development work.

## Analysis Workflow

1. **Resolve the input** (XID extraction, item type detection)
2. **Get baselines** (determine ECU and available baselines)
3. **Retrieve context** (get requirement tree with siblings and signals)
4. **Classify the item** (SWC pattern, requirement type)
5. **Analyze signals and FULLY RESOLVE internal signals** (THE CORE STEP)
6. **Trace dependencies** (cross-SWC signals, DOID parameters)
7. **Identify ambiguities** (gaps, unclear specs, assumptions)
8. **Generate report** (structured analysis with test case guidance)

## Step 1: Resolve Input to XID

Users may provide input in several forms. Extract the XID:

- **swap:// URL**: Extract XID from the path segment. Example: `swap://setoolvbc.srv.volvo.com:3001/x0400000000A03F2A` -> XID is `x0400000000A03F2A`
- **Direct XID**: Already in format `x` followed by uppercase hex, e.g. `x0400000000A03F2A`
- **Requirement name or keyword**: Use `loom_setool_system_weaver_search` with `item_type="requirement"` to find the XID
- **DOID code**: Use `loom_get_doid_parameter` to look up the parameter, which may reference requirement XIDs
- **Signal name**: Use `loom_setool_system_weaver_search` with `item_type="signal"` to find signal XIDs, then trace to owning requirements

## Step 2: Determine Item Type and Get Baselines

Call `loom_get_item_ecu_baselines(item_xid)` first. This always works regardless of item type.

The result returns baseline names (e.g. W0, V0, U0) mapped to ECU XIDs. Use the **first/latest** baseline (alphabetically last key) for subsequent queries.

**CRITICAL**: Items in SystemWeaver exist at different hierarchy levels:
- **Requirement-level items**: Retrievable via `loom_get_item_context_with_baseline`. Return full context with siblings, signals, parent info.
- **Container/SWC-level items**: Return "Requirement not found" from context tools. Parent nodes that contain requirements.

If `loom_get_item_context_with_baseline` returns "not found", the item is likely a container. In that case:
1. Search for child items using `loom_setool_system_weaver_search` with the SWC name
2. Ask the user to provide a specific child requirement XID
3. Note this limitation clearly in the report

**Baseline selection strategy**:
- Always try the latest baseline first
- If a baseline fails, fall back to the next most recent
- Different SWCs on the same ECU share baselines; SWCs on different ECUs have different baseline sets

## Step 3: Retrieve Full Context

Use `loom_get_item_context_with_baseline(requirement_xid, baseline)` with the latest baseline.

The context response contains:
- **main_item**: The target item with name, description, version, signals, parameters, vehicle_modes, cycle_time, end_user_functions
- **siblings**: Peer requirements under the same parent (the full SWC requirement set)

For each sibling requirement, note:
- XID, name, requirement ID, version
- Description (the actual requirement specification)
- Signals (with direction, computation type, database matches)
- Parameters (DOID references)
- Vehicle modes

**For large SWCs (>20 siblings)**: Do NOT try to analyze every requirement in detail. Instead:
1. Count total requirements
2. Categorize them by path/group (e.g., Function, Diagnostic, Production)
3. Identify repeated patterns
4. Deep-dive only on representative examples of each pattern type
5. Focus detailed analysis on the specific requirement the user asked about

## Step 4: Classify the Requirement Pattern

Requirements in Volvo SWCs follow common patterns. See `references/requirement-patterns.md` for the full catalog, including:

- Signal conversion/mapping (truth tables, enum mapping)
- Output handler (threshold comparison + presentation signals)
- Arbitration/priority logic (multi-source request merging)
- Data adaptation (unit conversion with overflow clamping)
- Configuration/settings management (defaults, fallbacks, persistence)
- Fault-to-DTC mapping (fault condition -> notification ID)
- Loss-of-communication detection (heartbeat/timeout monitoring)

## Step 5: Analyze Signals and FULLY RESOLVE Internal Signals

This is the most critical step. Every signal must be classified AND every internal signal
must be traced to its ultimate physical source/destination. The report MUST present the
complete signal picture -- not just "this is an internal signal" but WHERE it comes from
and WHERE it goes, including the requirements that produce/consume it.

### 5.1: Determine Actual Direction of Each Signal

**WARNING**: The `direction` field in SystemWeaver metadata is UNRELIABLE. All signals may
be marked "in" regardless of actual role. Determine true direction from:
1. The requirement description text ("shall be set to" = output, condition checks = input)
2. CAN database transmitter/receiver info (if the host ECU transmits it, it's an output)
3. Signal naming conventions: `PS_*` = presentation output, `Set*` = output, `Chg*` = change request input

### 5.2: Classify Each Signal

For every signal, classify it into one of:
- **Physical Input**: Has a good database match (score >= 80%), known transmitter ECU and bus
- **Physical Output**: Has a good database match where the host ECU is the transmitter
- **Internal Signal (same SWC)**: Marked `direction: "internal"`, or no database match AND found in sibling requirements of the same SWC
- **Internal Signal (cross-SWC)**: No database match, NOT found in siblings, likely produced/consumed by another SWC on the same ECU
- **Configuration Parameter**: Referenced via DOID code

### 5.3: FULLY RESOLVE Every Internal Signal

**This is mandatory. Do not skip this for any internal signal.**

An internal signal is a bridge between requirements. It hides the real physical signal chain.
The analysis MUST unwrap it to show the full picture.

#### Step A: Check Within the Same SWC (Sibling Scan)

When you have the context (Step 3), you already have ALL sibling requirements with their
signal lists. For each internal signal:

1. **Match by XID**: Scan ALL sibling requirements' signal lists for the same signal XID.
2. **Identify producer**: The requirement whose description says the signal "shall be set to"
   a value is the **producer**. The signal appears in its signal list.
3. **Identify consumer(s)**: Requirements that use the signal as a condition in their
   description are **consumers**. The signal appears in their signal list.
4. **Map the chain**: Document: `Producer Req -> [Internal Signal] -> Consumer Req(s)`
5. **Resolve to physical signals**: The producer requirement has its OWN inputs (which may
   be physical CAN/LIN signals). The consumer requirement has its OWN outputs (which may
   be physical CAN/LIN signals). These are the REAL endpoints of the chain.

**Example from SWSpeedControlConversion_Ctrl:**
```
Physical: SWSpdCtrlButtonsStatus6 (LIN from SWS6)
Physical: CruiseCtrlActive (CAN from VECU)
Physical: SWSpeedControlAdjustMode (internal, cross-SWC -- see below)
    |
    v
Req-2931 (Activate Downhill Cruise)
    |  writes: "Downhill Cruise Status Internal" (internal signal)
    v
Req-12983 (Downhill Cruise/Set Overspeed)
    |  reads: "Downhill Cruise Status Internal" + "SetOverspeedInternal"
    |  writes: CruiseEngineBrakeButton
    v
Physical: CruiseEngineBrakeButton (CAN to VECU via VP11_X_IC)
```

The report must show this FULL chain, not just "Downhill Cruise Status Internal is internal."

#### Step B: Check Across SWCs (Signal Search)

If the internal signal is NOT found in any sibling requirement, or if it has no database
match AND is used as an input to the current SWC:

1. **Search by name**: `loom_setool_system_weaver_search(query="<signal_name>", item_type="signal")`
2. **Analyze results**: The search returns all instances of the signal across SystemWeaver.
   - The base signal (no suffix) is the definition
   - Variants with `_I` suffix are **interface instantiations** used by different SWCs
   - Multiple results = the signal crosses SWC boundaries
3. **Try to find the producing requirement**: For each `_I` variant found, note its XID.
   Try `loom_get_requirement_context_from_latest_baseline` on the variant XIDs -- these
   will fail (signals are not requirements) BUT the search results give you the SWC
   ecosystem that uses this signal.
4. **Search for the signal name as a requirement**: Try
   `loom_setool_system_weaver_search(query="<signal_name>", item_type="requirement")` --
   sometimes the producing requirement is named after the signal it produces.

5. **Document what you find**: At minimum document:
   - The signal name and XID
   - How many SWCs reference it (count of search results)
   - Whether the producer could be identified or not
   - If not identified: mark as **[UNRESOLVED CROSS-SWC DEPENDENCY]** with the signal name,
     so test engineers know they must find and control the source

**Example of cross-SWC internal signal:**
```
Signal: SWSpeedControlAdjustMode (XID: x04000000001BC72B)
- database_match: null (no CAN/LIN mapping)
- Search returns 5 results: 1 base + 4 _I variants
- Used as input by Req-2006, Req-2007, Req-2008, Req-2931, Req-6792 in this SWC
- Producer: [UNRESOLVED] -- another SWC on IC3 produces this signal
- Test implication: Must stub/simulate this signal or have the producing SWC active
```

#### Step C: Resolve Signals Referenced in Text But Not in Signal List

Sometimes a requirement's description mentions a signal name that is NOT in its attached
signal list. This happens when the signal is managed at the SWC level. In this case:
1. Check if ANY sibling requirement has this signal in its list
2. If found, note which requirement owns it
3. If not found, search for it (Step B)

### 5.4: Build the Complete Signal Map

After resolving all signals, construct a complete map showing:

```
[Physical Inputs from external ECUs]
    |
    v
[Requirement A] --internal_signal_1--> [Requirement B] --internal_signal_2--> [Requirement C]
    |                                        |                                       |
    v                                        v                                       v
[Physical Outputs to external ECUs]   [Physical Outputs]                    [Physical Outputs]
```

For each internal signal in this map, document:
- Producer requirement (name, XID, Req-ID)
- Consumer requirement(s) (name, XID, Req-ID)
- The physical inputs that feed the producer
- The physical outputs produced by the consumer
- Whether the chain stays within one SWC or crosses SWC boundaries

This map is the CORE deliverable of the analysis. Everything else (ambiguities, test cases)
builds on this foundation.

### 5.5: Check Database Matches Quality

For physical signals, validate the database match:
- **100%**: Exact match -- trustworthy
- **80-99%**: High fuzzy match -- likely correct but verify the signal name mapping
- **65-80%**: Medium fuzzy -- may be correct, note uncertainty
- **<65%**: Low fuzzy -- likely a WRONG match (e.g., "EngTrueIdleSpeedFuel" matching "EngRatedSpeed" at 67%). Treat the CAN routing as UNKNOWN.

## Step 5.6: Detect CAN Loopback and Self-Referencing Signals

A signal classified as "input" may actually be a **loopback**: the SWC reading back its
own CAN output. Detect this by checking if the DB match transmitter is the same ECU the
SWC runs on.

**Example**: `HarshAcceleration` has direction="in" and DB match to
`Backbone2::IC3::Debug1_IC_BB2::HarshAcceleration_debug` -- IC3 is the transmitter.
This is NOT an external input. It's the SWC (or a sibling SWC on IC3) reading its own output.

Classify these as **LOOPBACK** signals, not physical inputs. Document:
- Which requirement produces the original output (e.g., PS_HarshAcceleration)
- Which requirement reads it back (e.g., Harsh Acceleration Counter reads HarshAcceleration)
- The CAN frame and bus carrying the loopback
- The timing implication: one CAN bus cycle of delay minimum

Also detect **self-referencing composite signals**: a signal that appears as BOTH input and
output on the SAME requirement. Example: PS_DriverCoachNotific is written by a requirement
AND read back as a condition in the same requirement's lookup table. Document the feedback
path and note the arbitration implications when multiple requirements share the signal.

## Step 5.7: Detect Implicit State Machines and Timer-Based Pipelines

After resolving all signals and their chains, look for these complex behavioral patterns:

### Requirement Pairs (Counter + Status)
If two requirements share 3+ internal signals (timer, status flag, counter), they form
a **pipeline pair**. The "Counter" requirement detects events and starts timers. The
"Status" requirement checks the timer and produces the output. Document:
- The pair relationship (which is Counter, which is Status)
- All shared internal signals with their roles (timer, flag, counter, cooldown)
- The implicit state machine: list all reachable states (combinations of flags/timers)
  with their meanings and all transitions between states

### Edge Detection
Look for conditions like "previous cycle value < threshold AND current cycle value >=
threshold". This means the requirement retains state from the previous execution cycle.
Document the edge detection condition and what triggers it.

### Timers with Abort Conditions
If a timer can be started AND reset/aborted by different conditions, document:
- What starts the timer
- What aborts/resets it
- What happens when it expires
- Whether abort is immediate or deferred

### Initialize Requirements
A requirement that resets ALL internal signals on a vehicle mode transition
(e.g., Cranking->Running) is an **initialization requirement**. It creates a dependency
on every other requirement in the SWC. Document which signals it resets and the trigger.

### Replicated Domains
If the same pattern (Counter+Status, or Queue+Output) is replicated across multiple
domains (e.g., 6 driving behavior domains), document:
- The common pattern
- Domain-specific variations (different thresholds, output levels, guard conditions)
- Whether the domains are truly independent or share any signals

## Step 6: Identify Dependencies and Related Requirements

### Within the Same SWC
- Internal signal chains discovered in Step 5 ARE the intra-SWC dependencies
- Requirements with overlapping input conditions but different output signals may have
  **implicit mutual exclusion** via gating conditions -- document these
- **Requirement pairs** (Pattern 7): Counter+Status pairs are tightly coupled
- **Initialize requirements**: Create fan-out dependencies to all other requirements
- **Shared output signals**: Multiple requirements writing the same output creates
  implicit coupling and potential arbitration issues

### Across SWCs (Multi-SWC Pipelines)
- Unresolved cross-SWC signals from Step 5.3B are the cross-SWC dependencies
- **Loopback signals** may indicate a multi-SWC pipeline on the same ECU: SWC A
  produces a CAN signal, SWC B on the same ECU reads it as input
- For each, note: signal name, number of SWC references found, whether producer was identified
- These affect test setup: the producing SWC must be active or the signal must be stubbed
- **Trace the full pipeline**: If SWC A -> CAN signal -> SWC B -> CAN signal -> SWC C,
  document the entire chain, not just the immediate neighbors

### DOID Parameters
- Some requirements are gated by DOID parameters (e.g., "ECU X, Installed = Installed")
- Look up DOIDs with `loom_get_doid_parameter` to understand the configuration dependency
- These affect whether a requirement is active in a given vehicle configuration

## Step 7: Identify Ambiguities

Systematically check for common issues (see `references/common-ambiguities.md` for the
full catalog of 22 ambiguity types). Key categories:

**Specification defects** (CRITICAL):
1. Missing comparison operators (`!=` stripped from text)
2. Duplicate XIDs for the same logical signal
3. Shared output signal without arbitration rule

**Signal classification issues** (HIGH):
4. Signal direction metadata unreliable (all marked "in")
5. CAN loopback signals misclassified as external inputs
6. Self-referencing composite signals (both input and output)
7. Fuzzy DB matches as noise (<65% = wrong match)

**Missing specifications** (HIGH):
8. Timer/threshold parameter values not specified
9. Missing error/NotAvailable handling
10. "Signal missing" without formal definition
11. Undefined default/initial values
12. Execution order not specified for multi-writer internal signals

**Behavioral complexity** (MEDIUM):
13. Implicit state machine without named states
14. Edge detection requiring cycle-to-cycle state retention
15. CAN bus round-trip delay affecting feedback loops

**Documentation gaps** (MEDIUM/LOW):
16. "Valid Signal Range" undefined
17. "Don't care" not formally defined
18. "Should" vs "Shall" mixed
19. Inconsistent enum naming
20. Empty descriptions, typos in signal names

**Mark each ambiguity clearly** with severity (CRITICAL / HIGH / MEDIUM / LOW) and
whether it blocks test case creation or is just a documentation gap.

## Step 8: Generate Diagram Specifications

Before generating the HTML report, create machine-readable diagram specifications that can be consumed by the visual-explainer skill. See `references/diagram-specification.md` for the complete format.

### 8.1: Extract Logic Structure

Analyze the requirement description to extract:
1. **Nodes**: Inputs, decisions, processes, outputs, states
2. **Edges**: Flow between nodes with conditions/labels
3. **Subgraphs**: Logical groupings (inputs, detection logic, outputs)
4. **Complexity**: Count nodes/edges to determine if splitting is needed

### 8.2: Create Diagram Spec JSON

Generate a JSON file following the diagram specification format:
- **Filename**: `{requirement_id}-{diagram_name}-spec.json` (e.g., `req-5399-event-detection-spec.json`)
- **Location**: Same directory as HTML report (`C:\work\vbc-cerebro\temp\`)
- **Content**: Complete diagram specification with nodes, edges, subgraphs, style classes, and layout hints

### 8.3: Determine if Splitting is Needed

Apply automatic splitting rules (see `diagram-specification.md`):
- **Flowchart**: Split if > 15 nodes or > 25 edges
- **State machine**: Split if > 12 states
- **Strategy**: Choose based on structure (by_path for main/error flows, by_subgraph for inputs/processing/outputs, by_state_group for state machines)

If splitting is needed, create multiple diagram spec files:
- `req-XXXX-main-flow-spec.json`
- `req-XXXX-error-handling-spec.json`
- `req-XXXX-state-transitions-spec.json`

### 8.4: Layout Optimization Hints

Include layout hints in the spec to minimize line crossings:
- **node_order**: Array of node IDs in processing sequence
- **minimize_crossings**: Boolean flag (always true)
- **separate_error_paths**: Use dashed lines for reset/error paths
- **group_related**: Keep related nodes physically close

## Step 9: Generate the Report

Use the report template from `references/report-template.md`. Adapt sections based on findings.

Key principles:
- **Be honest about unknowns**: If something cannot be determined, say so explicitly. Do NOT assume.
- **Mark assumptions**: Prefix with "[ASSUMPTION]"
- **Separate facts from interpretation**: Requirement text is fact. Analysis is interpretation.
- **The signal map from Step 5.4 is the core of the report**: Include it prominently.
- **For every internal signal**: Show the full chain (producer -> signal -> consumer) with
  the physical signals at each end. Never leave an internal signal as just "internal."
- **Include visual diagrams**: Load diagram spec JSON files and pass to visual-explainer skill for Mermaid rendering (DO NOT create ASCII art diagrams manually)

## Handling Special Cases

### Huge SWCs (>50 requirements)
1. Get the full context once (it may be >200KB of data)
2. Count and categorize all requirements by path
3. Identify repeated patterns
4. Note which requirements break the pattern (these need individual attention)
5. Still resolve ALL internal signals -- even in huge SWCs, the internal signal count
   is usually small compared to the requirement count

### Container XIDs That Cannot Be Resolved
1. Inform the user that the XID is a container/SWC-level item, not a requirement
2. Suggest they provide a child requirement XID instead
3. Try searching for related items by name fragments
4. The swap:// URL can be opened in the SE-Tool desktop client to browse children

### Cross-ECU Dependencies
When signals come from other ECUs (EMS, VECU, TECU, etc.), note:
- The bus and frame carrying the signal
- The transmitting ECU
- Whether the signal is standard J1939 or proprietary
- Test implications: these signals must be simulated or the source ECU must be present

### DOID Parameter Resolution
When a requirement references a DOID (e.g., P1Z8G):
1. Call `loom_get_doid_parameter(doid)` to get the parameter definition
2. Note the parameter name, value range, and default
3. Document whether it gates the requirement's activation
4. This affects vehicle variant testing (some features only active with certain hardware installed)
