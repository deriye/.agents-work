---
name: paqr-framework-docs
description: This is full documentation of PAQR python framework used to write IC3/GFX tests for CANoe environment. The python tests are used to generate XML test cases that are executed in CANoe for automotive instrument cluster testing.
---

# PAQR Test Writer Skill

Write valid, correct, and functional PAQR test cases for automotive instrument cluster testing in CANoe environment.

## Overview

PAQR is a Python-to-XML test framework: Python Test Code → TestCase API → XML Generation → CANoe Test Execution. Tests verify signal routing between CAN bus, LIN bus, and presentation signals (PS) on the instrument cluster display.

## Critical Rules

1. **Class must be named `Test`** inheriting from the correct base class
2. **Complete metadata dict required** with all fields (see template)
3. **Both `IC3_Parameters` and `GFX_Parameters`** must be defined (can be empty `{}`)
4. **Signal format uses `::` separators** — CAN: `"Network::ECU::Message::Signal"`, LIN: `"LINBus::Node::Message::Signal"`, PS: `"PS_SignalName"`
5. **Use `IntEnum` classes instead of magic numbers** — Define `IntEnum` for signal values (e.g., `PedalTestOrders`, `InactiveActive`) and pass members directly. `IntEnum` inherits from `int` so no `.value` needed.
6. **Set input signals before checking outputs**
7. **Include delays** for signal propagation where needed

## Base Class Selection

| Test Type | Base Class | When to Use |
|-----------|------------|-------------|
| Gateway/Signal routing | `GWTest` | CAN→PS, LIN→PS signal translation (90% of tests) |
| DTC testing | `DTCTest` | Diagnostic trouble codes |
| Generic/Custom | `TestCase` | Custom test types not covered above |

**Import:** `from vbc_paqr.framework.python2xml.TestCase import GWTest, VehicleMode`

## Reference Documentation

Read these bundled references for detailed information:

- **[api_reference.md](references/api_reference.md)** — Complete API: all methods, signatures, parameters, enums, and constants
- **[quick_start.md](references/quick_start.md)** — Test types, testing patterns, running tests via CLI
- **[test_patterns.md](references/test_patterns.md)** — Real-world patterns from stable tests (DTC groups, nested loops, LIN, timing, multi-param)

## Template

Use `assets/test_template.py` as starting point. Minimal structure:

```python
from pathlib import Path
from vbc_paqr.framework.python2xml.TestCase import GWTest

class Test(GWTest):
    metadata = {
        "metadata_version": "2.0",
        "tags": [],
        "testcase_name": "Test Name",
        "req_title": "Requirement Title",
        "req_xid": "x04000000001234AB",
        "req_id": "Req-1234",
        "req_version": "1",
        "manual_test_case_xids": [],
        "is_stable": True,
        "reason_not_stable": "",
        "comments": ""
    }
    
    title = "Test Title"
    IC3_Parameters = {}
    GFX_Parameters = {}
    
    def run(self):
        # Test logic here
        pass
```

## Framework Limitations

1. **Type System** — Limited type hints, runtime validation
2. **Menu Paths** — Hardcoded validation for menu navigation
3. **DID Mappings** — Diagnostic identifiers are hardcoded
4. **Signal Validation** — PS signals validated against APX files at runtime
5. **Enum Usage** — Use `IntEnum` (from `enum` stdlib) for signal values. `IntEnum` members are ints and work directly with `set_can_signal`/`check_PS_signal` without `.value`

## Framework Locations

- Main API: `C:\work\vbc_ic_paqr\src\vbc_paqr\framework\python2xml\TestCase.py`
- Framework modules: `C:\work\vbc_ic_paqr\src\vbc_paqr\framework\python2xml\`
- XML generator: `C:\work\vbc_ic_paqr\src\vbc_paqr\cli_controller\cli_generate.py`
- Test examples: `C:\work\vbc_ic_test_cases\testprocedures\ic by SWC\`
