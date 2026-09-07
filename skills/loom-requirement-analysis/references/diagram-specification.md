# Diagram Specification Format

Machine-readable representation of requirement logic diagrams that can be consumed by the visual-explainer skill to generate optimized Mermaid diagrams.

## Purpose

- **Separation of concerns:** Requirement analysis focuses on extracting logic, visual-explainer focuses on rendering
- **Automatic diagram splitting:** Complex state machines or flows can be split into multiple digestible diagrams
- **Line crossing optimization:** Diagram generator can apply layout algorithms to minimize crossings
- **Consistency:** All requirement diagrams follow the same visual language

## Format: JSON Diagram Specification

```json
{
  "diagram_type": "flowchart | state_machine | sequence | data_flow",
  "title": "Diagram title for context",
  "description": "Brief description of what this diagram shows",
  "layout_direction": "TD | LR",
  "complexity": "simple | medium | complex",
  "should_split": true,
  "split_strategy": "by_subgraph | by_state_group | by_path",
  
  "nodes": [
    {
      "id": "A",
      "type": "input | output | internal | decision | process | state | event",
      "label": "Node display label",
      "sublabels": ["Additional line 1", "Additional line 2"],
      "metadata": {
        "source_ecu": "EBS",
        "bus": "J1939_1",
        "signal_name": "LongitudinalAcceleration",
        "data_type": "float",
        "unit": "m/s²",
        "range": "-12.5 to +13.0"
      },
      "group": "inputs",
      "style_class": "inputStyle",
      "importance": "primary | secondary"
    }
  ],
  
  "edges": [
    {
      "from": "A",
      "to": "B",
      "label": "True",
      "style": "solid | dashed | dotted",
      "importance": "primary | secondary",
      "description": "Optional context for what this edge represents"
    }
  ],
  
  "subgraphs": [
    {
      "id": "inputs",
      "label": "External Inputs (CAN)",
      "node_ids": ["A", "B", "C"],
      "style": {
        "border_color": "#34d399",
        "background": "#1a3a2e"
      }
    }
  ],
  
  "style_classes": {
    "inputStyle": {
      "fill": "#1a3a2e",
      "stroke": "#34d399",
      "stroke_width": "2px",
      "color": "#e8eef5"
    }
  },
  
  "layout_hints": {
    "node_order": ["A", "B", "C"],
    "minimize_crossings": true,
    "group_related": true,
    "separate_error_paths": true
  },
  
  "split_points": [
    {
      "reason": "complexity_threshold",
      "create_diagrams": [
        {
          "title": "Main Detection Flow",
          "include_node_ids": ["A", "B", "C", "D", "E"],
          "include_edge_ids": [0, 1, 2, 3]
        },
        {
          "title": "Reset and Error Handling",
          "include_node_ids": ["D", "E", "F", "I"],
          "include_edge_ids": [4, 5, 6]
        }
      ]
    }
  ]
}
```

## Diagram Types

### flowchart
Standard flowchart with rectangles, diamonds (decisions), and directed edges. Used for:
- Signal processing pipelines
- Event detection logic
- Multi-condition gates
- Data transformation flows

**Complexity metrics:**
- Simple: < 8 nodes
- Medium: 8-15 nodes
- Complex: > 15 nodes (should split)

**Split strategy:** `by_path` (separate main flow from error/reset paths)

### state_machine
State diagram with states and transitions. Used for:
- Requirement state machines
- Mode management logic
- Protocol implementations

**Complexity metrics:**
- Simple: < 6 states
- Medium: 6-12 states
- Complex: > 12 states (should split)

**Split strategy:** `by_state_group` (group related states, e.g., initialization states, operational states, error states)

### sequence
Sequence diagram showing interactions over time. Used for:
- Cross-requirement signal flow
- ECU communication patterns
- Temporal dependencies

**Complexity metrics:**
- Simple: < 4 participants, < 10 messages
- Medium: 4-6 participants, 10-20 messages
- Complex: > 6 participants or > 20 messages (should split)

**Split strategy:** `by_scenario` (split into multiple interaction scenarios)

### data_flow
Data flow diagram showing inputs, processes, and outputs. Used for:
- Cross-SWC signal dependencies
- System-level architecture
- Data transformation pipelines

**Complexity metrics:**
- Simple: < 10 nodes
- Medium: 10-20 nodes
- Complex: > 20 nodes (should split)

**Split strategy:** `by_subgraph` (separate input acquisition, processing logic, output distribution)

## Node Types

### input
External input signal (CAN, LIN, configuration parameter)
- **Metadata:** source_ecu, bus, signal_name, data_type, range
- **Style:** Green border (`#34d399`)
- **Shape:** Rectangle with rounded corners

### output
Output signal or result
- **Metadata:** destination_ecu, bus, signal_name
- **Style:** Red border (`#fb7185`)
- **Shape:** Rectangle with rounded corners

### internal
Internal signal or state variable
- **Metadata:** data_type, scope
- **Style:** Indigo border (`#818cf8`)
- **Shape:** Rectangle

### decision
Conditional branch point
- **Metadata:** condition_expression
- **Style:** Cyan border (`#1fb6d6`)
- **Shape:** Diamond (rhombus)

### process
Processing step or action
- **Metadata:** action_description
- **Style:** Cyan border (`#1fb6d6`)
- **Shape:** Rectangle

### state
State in a state machine
- **Metadata:** entry_actions, exit_actions
- **Style:** Cyan border (`#1fb6d6`)
- **Shape:** Rectangle with rounded corners

### event
Triggering event or condition
- **Metadata:** event_type, source
- **Style:** Amber border (`#fbbf24`)
- **Shape:** Oval

## Edge Styles

### solid
Main flow, primary path, expected/normal operation
- Used for: Happy path logic, primary signal flow

### dashed (`-.->`)
Secondary flow, error handling, reset conditions
- Used for: Exception paths, reset logic, fallback flows

### dotted (`-..->`)
Weak dependencies, optional paths
- Used for: Optional signals, conditional dependencies

## Layout Hints

### minimize_crossings
Apply algorithms to reduce line crossings:
1. Order nodes by processing sequence
2. Group fan-in/fan-out nodes
3. Place decision nodes strategically
4. Use dashed lines for secondary paths

### group_related
Keep related nodes physically close:
- Inputs together
- Decision chain sequential
- Outputs together

### separate_error_paths
Error/reset paths should branch off to the side rather than interleaving with main flow

## Automatic Splitting Rules

### When to split:
1. **Node count:** > 15 nodes in flowchart, > 12 states in state machine
2. **Edge count:** > 25 edges
3. **Subgraph isolation:** Subgraphs with minimal inter-connections can be separate diagrams
4. **Logical separation:** Main flow vs. error handling, initialization vs. operation
5. **Visual complexity:** More than 3 levels of nesting

### How to split:

**Option 1: By path**
- Diagram 1: Main flow (happy path)
- Diagram 2: Error handling and resets
- Diagram 3: Edge cases and special conditions

**Option 2: By subgraph**
- Diagram 1: Input acquisition and validation
- Diagram 2: Core processing logic
- Diagram 3: Output distribution and downstream

**Option 3: By state group**
- Diagram 1: Initialization states and transitions
- Diagram 2: Normal operation states
- Diagram 3: Error and recovery states

**Option 4: By scenario**
- Diagram 1: Nominal scenario
- Diagram 2: Scenario A (specific condition)
- Diagram 3: Scenario B (alternative condition)

### Transition nodes
When splitting, use "transition nodes" to show connections between diagrams:
```json
{
  "id": "TRANS_1",
  "type": "transition",
  "label": "→ See 'Error Handling' diagram",
  "target_diagram": "error_handling",
  "style_class": "transitionStyle"
}
```

## Example: Simple Diagram Spec

```json
{
  "diagram_type": "flowchart",
  "title": "Harsh Acceleration Event Detection",
  "description": "Shows how acceleration input is validated and events are detected",
  "layout_direction": "TD",
  "complexity": "medium",
  "should_split": false,
  
  "nodes": [
    {
      "id": "A",
      "type": "input",
      "label": "LongitudinalAcceleration",
      "sublabels": ["Source: EBS", "Bus: J1939_1::VDC2"],
      "group": "inputs",
      "style_class": "inputStyle",
      "importance": "primary"
    },
    {
      "id": "D",
      "type": "decision",
      "label": "Time Debounce Filter",
      "sublabels": ["AccTimeValidStatus"],
      "group": "detection",
      "style_class": "processStyle",
      "importance": "primary"
    },
    {
      "id": "H",
      "type": "process",
      "label": "Start HarshAccTimer",
      "sublabels": ["Set HarshAccCounterSts = True"],
      "group": "detection",
      "style_class": "processStyle",
      "importance": "primary"
    }
  ],
  
  "edges": [
    {
      "from": "A",
      "to": "D",
      "label": "",
      "style": "solid",
      "importance": "primary"
    },
    {
      "from": "D",
      "to": "H",
      "label": "True",
      "style": "solid",
      "importance": "primary"
    }
  ],
  
  "subgraphs": [
    {
      "id": "inputs",
      "label": "External Inputs (CAN)",
      "node_ids": ["A"],
      "style": {
        "border_color": "#34d399"
      }
    }
  ],
  
  "layout_hints": {
    "minimize_crossings": true,
    "group_related": true,
    "separate_error_paths": true
  }
}
```

## Integration with Requirement Analysis

When analyzing a requirement, the loom-requirement-analysis skill should:

1. **Extract logic structure** from requirement description
2. **Identify nodes:**
   - Inputs (signals from other ECUs/SWCs)
   - Decisions (conditional branches)
   - Processes (actions, timer starts, state changes)
   - Outputs (resulting signals)
3. **Map edges** between nodes based on logic flow
4. **Classify complexity** and determine if splitting is needed
5. **Generate diagram spec JSON** and save to file
6. **Pass spec to visual-explainer** for rendering

## File Naming Convention

```
{requirement_id}-{diagram_name}-spec.json
```

Examples:
- `req-5399-event-detection-spec.json`
- `req-5399-reset-logic-spec.json` (if split)
- `req-7712-aggregation-spec.json`

## Storage Location

Save diagram specs alongside HTML reports:
```
C:\work\vbc-cerebro\temp\
├── req-5399-event-detection-analysis.html
├── req-5399-event-detection-spec.json
└── req-5399-reset-logic-spec.json (if split)
```

This allows:
- Versioning of diagram logic separately from visual styling
- Regeneration of diagrams with updated styling
- Reuse of diagram specs across different output formats
- Comparison of requirement changes via spec diffs
