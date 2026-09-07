# PAQR Quick Start Guide

Common test types, testing patterns, running tests, and troubleshooting.
For API details see `api_reference.md`. For the test template see `assets/test_template.py`.

---

## Common Test Types

### Simple Gateway Test (CAN → PS)

```python
from vbc_paqr.framework.python2xml.TestCase import GWTest

class Test(GWTest):
    metadata = { ... }
    title = "Engine Speed Indication"
    IC3_Parameters = {}
    GFX_Parameters = {}
    
    def run(self):
        for rpm in [0, 500, 1000, 1500, 2000]:
            self.set_can_signal("J1939_1::EMS::EEC1::EngineSpeed", rpm)
            self.check_PS_signal("PS_EngineSpeed", rpm)
```

### Gateway Test with Helper Method

```python
class Test(GWTest):
    metadata = { ... }
    title = "Overload Indication"
    IC3_Parameters = {}
    GFX_Parameters = {}
    
    def run(self):
        for i in range(4):
            self.GW_Can_to_PS(
                "Backbone2::BBM::BBM_BB2_07P::OverloadIndication",
                "PS_OverloadIndication",
                i, i
            )
```

### DTC Test

```python
from vbc_paqr.framework.python2xml.TestCase import DTCTest

class Test(DTCTest):
    metadata = { ... }
    title = "Engine Malfunction DTC"
    IC3_Parameters = {}
    GFX_Parameters = {}
    
    def run(self):
        self.set_dtc("7A000CC2", "2")
        self.delay(1000)
        self.check_PS_DWMDTCStatChange(8112, 1)
        
        self.clear_dtc("7A000CC2")
        self.delay(5000)
        self.check_PS_DWMDTCStatChange(8112, 0)
```

### Multi-Vehicle Mode Test

Runs the same test logic in each specified vehicle mode.

```python
from vbc_paqr.framework.python2xml.TestCase import GWTest, VehicleMode

class Test(GWTest):
    metadata = { ... }
    title = "Speed Warning in All Modes"
    IC3_Parameters = {}
    GFX_Parameters = {}
    vehiclemodes = [VehicleMode.PreRunning, VehicleMode.Cranking, VehicleMode.Running]
    
    def run(self):
        for speed in [0, 50, 100, 150]:
            self.set_can_signal(
                "J1939_1::VECU::CCVS::WheelBasedVehicleSpeed", speed
            )
            if speed > 120:
                self.check_PS_signal("PS_SpeedWarning", 1)
            else:
                self.check_PS_signal("PS_SpeedWarning", 0)
```

### Multi-Parameter Test

Runs once per parameter configuration. Framework handles parameter setting automatically.

```python
class Test(GWTest):
    metadata = { ... }
    title = "Fuel Level with Different Sensor Types"
    
    IC3GFX_multiparam = [
        {"title": "Standard Sensor", "IC3": {"P1PQ9": 0}, "GFX": {}},
        {"title": "High-Precision Sensor", "IC3": {"P1PQ9": 1}, "GFX": {}}
    ]
    
    def run(self):
        for level in [0, 25, 50, 75, 100]:
            self.set_can_signal("Backbone2::BBM::BBM_BB2_01P::FuelLevel", level)
            self.check_PS_signal("PS_FuelLevel", level)
```

---

## Testing Patterns

### Iterative Value Testing
```python
def run(self):
    for value in [0, 1, 2, 3]:
        self.set_can_signal("signal_name", value)
        self.check_PS_signal("ps_signal", expected_value)
```

### Conditional Assertions
```python
def run(self):
    for speed in [0, 50, 100]:
        self.set_can_signal("speed_signal", speed)
        if speed == 0:
            self.check_PS_signal("moving", 0)
        else:
            self.check_PS_signal("moving", 1)
```

### Multiple Signal Combinations
```python
def run(self):
    for signal_a in [0, 1]:
        for signal_b in [0, 1]:
            self.set_can_signal("signal_a", signal_a)
            self.set_can_signal("signal_b", signal_b)
            expected = signal_a and signal_b
            self.check_PS_signal("output", expected)
```

### State Change Verification
```python
def run(self):
    self.check_can_signal_statechange(
        "J1939_1::ECU::MSG::InputSignal", 1,
        "J1939_1::ECU::MSG::OutputSignal", 5
    )
```

---

## Running Tests

### Standalone Python Execution

```bash
python my_test.py
```
Generates XML in `test_xml/` directory (requires `if __name__ == "__main__"` block — see template).

### Using paqr CLI

```bash
paqr generate \
    --test-procedures-path "C:/path/to/tests" \
    --output-file "output.xml" \
    --name "My Test Suite"
```

### With Metadata Filtering

```bash
# Only stable tests
paqr generate --test-procedures-path "C:/path/to/tests" --output-file "stable.xml" --metadata-filter is_stable=True

# By tag
paqr generate --test-procedures-path "C:/path/to/tests" --output-file "smoke.xml" --metadata-filter tags=smoketest
```

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `TypeError: expected int or str, got Enum` | Passing `Enum` (not `IntEnum`) member | Use `IntEnum` instead of `Enum` — `IntEnum` members are ints and work directly |
| `Invalid signal format` | Wrong signal name format | Use `::` separators: `"J1939_1::BBM::VMCU::VehicleMode"` |
| `Test class not found` | Class not named `Test` | Rename class to `Test` |
| `Missing metadata field` | Incomplete metadata dict | Include all required fields (see SKILL.md template) |

---

*Quick Start Guide - Last Updated: 2026-03-03*
