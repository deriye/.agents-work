# PAQR Test Patterns - Real World Examples

Advanced patterns from stable tests in the VBC IC test suite.
For basic test types (simple gateway, DTC, multi-mode, multi-param) see `quick_start.md`.

---
## Define Enums and Equation Functions

**Always use `IntEnum` instead of magic numbers for signal values.** Define enums at module level, above the `Test` class. `IntEnum` inherits from `int`, so members work directly with `set_can_signal`/`check_PS_signal` — no `.value` needed.

Also make sure NOT to use `raw` values with functions to set signal values which means you must almost always convert raw to real value before applying.

```python
from enum import IntEnum
from vbc_paqr.framework.python2xml.TestCase import GWTest


class PedalTestOrders(IntEnum):
    ApplyParkBrake = 0
    ReleaseAcceleratorPedal = 1
    PressAcceleratorPedal = 2
    PedalOperational1 = 3
    ContactWorkshop = 4
    PedalOperational2 = 5
    PedalTestFailed = 6
    NotAvailable = 15


class InactiveActive(IntEnum):
    Inactive = 0
    Active = 1
    Error = 2
    NotAvailable = 3


class Test(GWTest):
    metadata = { ... }
    title = "Accelerator Pedal Performance Warning"
    IC3_Parameters = {}
    GFX_Parameters = {}

    def run(self):
        can_signal = "J1939_1::VECU::VP227_X_V::PedalTestOrders_BB1_X_V"
        ps_signal = "PS_AccPedalPerformance"

        # Positive case: ContactWorkshop → Active
        self.set_can_signal(can_signal, PedalTestOrders.ContactWorkshop)
        self.check_PS_signal(ps_signal, InactiveActive.Active)

        # Negative cases: all other values → Inactive
        non_workshop_values = [
            PedalTestOrders.ApplyParkBrake,
            PedalTestOrders.ReleaseAcceleratorPedal,
            PedalTestOrders.PressAcceleratorPedal,
            PedalTestOrders.PedalOperational1,
            PedalTestOrders.PedalOperational2,
            PedalTestOrders.PedalTestFailed,
            PedalTestOrders.NotAvailable,
        ]
        for value in non_workshop_values:
            self.set_can_signal(can_signal, value)
            self.check_PS_signal(ps_signal, InactiveActive.Inactive)
```

**Key points:**
- Define one `IntEnum` per signal enum type (from the requirement's signal definitions)
- Place enums at module level, before the `Test` class
- Use descriptive member names matching the specification (e.g., `ContactWorkshop`, not `Val4`)
- Collect related values into named lists for loop iteration (e.g., `non_workshop_values`)


## DTC Testing Patterns

### Using dtc_test() Helper

Simplified DTC testing — handles the set/check/clear/check cycle automatically.

```python
class Test(DTCTest):
    metadata = { ... }
    title = "Brake System Warning"
    IC3_Parameters = {}
    GFX_Parameters = {}
    
    def run(self):
        # DM1 DTC with FMI
        self.dtc_test(DTC=["7BFE680B"], NPP=19, FMI=["11"])
        
        # Multiple DTCs triggering same NPP
        self.dtc_test(DTC=["7A000C92", "7B000C92"], NPP=201, FMI=["18", "18"])
        
        # DiagFaultstat DTC (no FMI needed)
        self.dtc_test(DTC=["52F00097"], NPP=94)
```

### Multiple DTC Groups

Organized testing of multiple warning levels with parallel arrays.

```python
class Test(DTCTest):
    metadata = { ... }
    title = "Engine System DTCs"
    IC3_Parameters = {}
    GFX_Parameters = {}
    
    def run(self):
        listNPPid = [8112, 8113, 8114]
        listDtc = [
            ["7A000CC2", "7B000CC2"],
            ["7A000CC3", "7B000CC3"],
            ["7A000CC4"]
        ]
        listFail = [["2", "2"], ["2", "2"], ["2"]]
        listsysvar = [[1, 0], [1, 0], [1]]
        
        for i in range(len(listNPPid)):
            for j in range(len(listDtc[i])):
                self.set_sysvar("FaultGeneration::RedYellow", listsysvar[i][j])
                self.set_dtc(listDtc[i][j], listFail[i][j])
                self.delay(1000)
                self.check_PS_DWMDTCStatChange(listNPPid[i], 1)
                
                self.clear_dtc(listDtc[i][j])
                self.delay(5000)
                self.check_PS_DWMDTCStatChange(listNPPid[i], 0)
```

---

## Complex Signal Patterns

### Nested Loop Signal Combinations

Testing multiple interacting signals with complex conditional logic.

```python
class Test(GWTest):
    metadata = { ... }
    title = "Direction Indicators Presentation"
    IC3_Parameters = {"P10KQ": 1, "P1RC3": 1, "X1DP4": 1}
    GFX_Parameters = {}
    
    def run(self):
        for HazardWarningStatus in range(4):
            self.set_can_signal(
                "Backbone2::BBM::BBM_BB2_10P::HazardWarningStatus",
                HazardWarningStatus
            )
            for LeftFlashTruck in range(4):
                self.set_can_signal(
                    "J1939_1::SLCM08::VP37::LeftFlash_Truck_BB1_X_LCM",
                    LeftFlashTruck
                )
                for RightFlashTruck in range(4):
                    self.set_can_signal(
                        "J1939_1::SLCM08::VP37::RightFlash_Truck_BB1_X_LCM",
                        RightFlashTruck
                    )
                    if HazardWarningStatus == 1 and LeftFlashTruck != 2:
                        self.check_web_socket("PS_DirectionIndication", 6)
                        self.delay(700)
                    elif LeftFlashTruck == 2:
                        self.check_web_socket("PS_DirectionIndication", 2)
                        self.delay(700)
                    # ... more conditions
```

### State Change Verification

Using `check_can_signal_statechange()` for input→output verification in one step.

```python
class Test(TestCase):
    metadata = { ... }
    title = "Zone Speed Limit Disabled"
    IC3_Parameters = {"P168P": 0, "P177R": 0}
    GFX_Parameters = {"P177R": 1}
    
    def run(self):
        self.check_can_signal_statechange(
            "J1939_1::TECU::VP15::EcoRollActiveStatus", 0,
            "InfotainmentSubnet::IC3::IC_Infot_122P::SpeedLimitStatus", 15
        )
        
        for i in range(4):
            self.check_can_signal_statechange(
                "J1939_1::SLCM08::VP37::LeftFlash_Truck_BB1_X_LCM", i,
                "InfotainmentSubnet::IC3::IC_Infot_122P::LeftDirectionIndicator", i
            )
```

---

## Multi-Parameter Patterns

### Legacy Multi-Parameter (Cartesian Product)

`IC3_multiparam` × `GFX_multiparam` creates all combinations automatically. Prefer `IC3GFX_multiparam` for explicit control.

```python
class Test(GWTest):
    metadata = { ... }
    title = "Gear Display Variants"
    
    IC3_multiparam = [
        {"P1Q8M": 0, "P1WHR": 0},
        {"P1Q8M": 1, "P1WHR": 0}
    ]
    GFX_multiparam = [
        {"P1E28": 0},
        {"P1E28": 1}
    ]
    # Creates 2×2 = 4 test configurations
    
    def run(self):
        for i in range(10):
            self.GW_Can_to_PS(
                "J1939_1::TCM::ETC2::SelectedGear",
                "PS_GearSelected", i, i
            )
```

---

## LIN Bus Patterns

### LIN Signal Gateway

```python
class Test(GWTest):
    metadata = { ... }
    title = "Direction Indicators LIN"
    IC3_Parameters = {"P10KQ": 1, "P1RC3": 1, "X1DP4": 1}
    GFX_Parameters = {}
    
    def run(self):
        for TurnSignalSwitch in range(8):
            self.set_lin_signal(
                "LIN5::SM1::SM1toIC3_L5::LIN_DirInd_StalkStatus_1_1",
                TurnSignalSwitch
            )
            if TurnSignalSwitch == 1:
                self.check_web_socket("PS_DirectionIndication", 2)
                self.delay(700)
                self.check_web_socket("PS_DirectionIndication", 0)
            elif TurnSignalSwitch == 2:
                self.check_web_socket("PS_DirectionIndication", 1)
                self.delay(700)
                self.check_web_socket("PS_DirectionIndication", 0)
            elif TurnSignalSwitch == 3:
                self.check_web_socket("PS_DirectionIndication", 2)
```

### LIN to CAN Gateway

```python
class Test(GWTest):
    metadata = { ... }
    title = "Speed Control Buttons"
    IC3_Parameters = {}
    GFX_Parameters = {}
    
    def run(self):
        for i in range(10):
            self.LIN_to_CAN_GW(
                "LIN5::SWS6::SWS6toIC3_L5::LIN_SW_Enter_ButtonStatus_6",
                i,
                "J1939_1::IC3::VP11_X_IC::VecTimeGapButton_BB1_X_I",
                1 if i == 9 else 0
            )
```

---

## User Interaction Patterns

### PS Signal Request and CAN Response

```python
class Test(GWTest):
    metadata = { ... }
    title = "DPF Regeneration Request"
    IC3_Parameters = {}
    GFX_Parameters = {"P12BE": 1}
    
    def run(self):
        for value in range(4):
            self.set_PS_signal("ConfirmRegeneration_SoftStatus", value)
            if value == 1:
                self.delay(500)
                self.set_PS_signal("ConfirmRegeneration_SoftStatus", 0)
                self.check_can_signal(
                    "J1939_1::IC3::CM1::DslPrtcltFltrRgnrtonForceSwitch", 1
                )
                self.delay(4500)
            self.check_can_signal(
                "J1939_1::IC3::CM1::DslPrtcltFltrRgnrtonForceSwitch", 0
            )
```

---

## Timing-Sensitive Patterns

### Blinking Indicator

```python
class Test(GWTest):
    metadata = { ... }
    title = "Temporary Direction Indicator"
    IC3_Parameters = {"P10KQ": 1}
    GFX_Parameters = {}
    
    def run(self):
        self.set_lin_signal(
            "LIN5::SM1::SM1toIC3_L5::LIN_DirInd_StalkStatus_1_1", 3
        )
        self.check_web_socket("PS_DirectionIndication", 2)
        self.delay(700)  # Typical blink timing: 500-700ms
        self.check_web_socket("PS_DirectionIndication", 0)
        self.delay(700)
        self.check_web_socket("PS_DirectionIndication", 2)
```

### Speed-Dependent Behavior

```python
class Test(GWTest):
    metadata = { ... }
    title = "Seat Belt Reminder Speed Dependent"
    IC3_Parameters = {"P1X1F": 0, "P1AXO": 1, "P1AXQ": 40, "P1AXR": 15}
    GFX_Parameters = {}
    vehiclemodes = [VehicleMode.PreRunning, VehicleMode.Cranking, VehicleMode.Running]
    
    def run(self):
        for seatbelt_state in range(4):
            self.set_can_signal(
                "Backbone2::BBM::BBM_BB2_05P::SeatBeltSwitch", seatbelt_state
            )
            for speed in [0, 10, 20, 30, 50]:
                self.set_can_signal(
                    "J1939_1::VECU::CCVS::WheelBasedVehicleSpeed", speed
                )
                if seatbelt_state == 1 and speed <= 15:
                    self.check_PS_signal("PS_SeatBeltReminder", 1)
                else:
                    self.check_PS_signal("PS_SeatBeltReminder", 0)
```

---

## Best Practices Summary

- **Signal testing:** Set before check, include delays, test boundary values
- **Timing:** 50ms default for setting, 2000ms for checking, 5s+ for DTC operations, 500-700ms for blink cycles
- **Parameters:** Use `IC3GFX_multiparam` over legacy format, document parameter meanings in comments
- **Vehicle modes:** Test in appropriate modes; some features only work in specific modes
- **Error conditions:** Test NotAvailable states and fault injection (`block_frame`/`unblock_frame`)

---

*Test Patterns Guide - Last Updated: 2026-03-03*
