# PAQR TestCase API Reference

Complete reference for the PAQR TestCase framework interfaces.

---

## Base Classes

### TestCase

Generic base class for all test types.

**Location:** `vbc_paqr.framework.python2xml.TestCase`

**Class Attributes:**
```python
ident: str = "TC"                           # Test case identifier
title: str = ""                             # Test case title
description: str = ""                       # Test case description
IC3_Parameters: dict = {}                   # IC3 ECU parameters
GFX_Parameters: dict = {}                   # GFX ECU parameters
IC3GFX_multiparam: list[ParameterSet] = []  # Multi-parameter sets (preferred)
IC3_multiparam: list[dict] = []             # IC3 multi-param (legacy)
GFX_multiparam: list[dict] = []             # GFX multi-param (legacy)
vehiclemodes: list[VehicleMode] = []        # Vehicle modes to test
metadata: dict                              # Test metadata (required)
```

**Abstract Method:**
```python
def run(self) -> None:
    """Implement test logic here."""
```

**XML Generation:**
```python
def to_xml(
    vehiclemode: VehicleMode = VehicleMode.PreRunning,
    first_vehicle_mode: VehicleMode = VehicleMode.PreRunning
) -> str:
    """Generate XML test case string."""
```

---

### GWTest

Specialized for gateway testing (signal routing). Inherits TestCase.

**Additional Methods:**
```python
def GW_Can_to_PS(
    can_signal: str, PS_signal: str,
    can_signal_value: int, PS_signal_value: int,
    wait: int = DEFAULT_SIGNAL_WAIT_SET
) -> None:
    """Test CAN signal to PS signal gateway."""

def LIN_to_CAN_GW(
    lin_signal: str, lin_signal_value: int,
    can_signal: str, can_signal_value: int,
    wait: int = DEFAULT_SIGNAL_WAIT
) -> None:
    """Test LIN signal to CAN signal gateway."""

def CAN_to_LIN_GW(
    can_signal: str, can_signal_value: int,
    lin_signal: str, lin_signal_value: int
) -> None:
    """Test CAN signal to LIN signal gateway."""

def check_web_socket(
    signal: str, value: int,
    wait: int = DEFAULT_SIGNAL_WAIT
) -> None:
    """Check PS/PV signal value via websocket."""
```

---

### DTCTest

Specialized for DTC (Diagnostic Trouble Code) testing. Inherits TestCase.

**Additional Methods:**
```python
def set_dtc(self, DTC: str, FMI: str) -> None:
    """Set diagnostic trouble code with failure mode identifier.
    Example: self.set_dtc("7BFE680B", "11")"""

def clear_dtc(self, DTC: str) -> None:
    """Clear specific diagnostic trouble code."""

def clear_all_dtcs(self, ecu: str) -> None:
    """Clear all DTCs from specified ECU ("IC3" or "GFX")."""

def dtc_test(self, *, DTC: list, NPP: str, delay: int = 5500, FMI: list | None = None) -> None:
    """Complete DTC test cycle: set → wait → verify active → clear → verify cleared.
    
    Args:
        DTC: List of DTC codes (e.g., ["7BFE680B"])
        NPP: Notification Popup ID
        delay: Wait time after setting DTC (default 5500ms)
        FMI: List of Failure Mode Identifiers (for DM1 DTCs, omit for DiagFaultstat)
    
    Examples:
        self.dtc_test(DTC=["7BFE680B"], NPP=19, FMI=["11"])          # DM1 with FMI
        self.dtc_test(DTC=["7A000C92", "7B000C92"], NPP=201, FMI=["18", "18"])  # Multiple
        self.dtc_test(DTC=["52F00097"], NPP=94)                       # DiagFaultstat (no FMI)
    """

def set_loss_comm(self, ecu: str, npp: str, delay: int = 7500) -> None:
    """Test loss of communication with ECU.
    Supported ECUs: BBM, CICU, DACU, EHRAS, EMS, FAS, HPCU, PCM, RECU, SCIM, TPMS, VECU"""
```

---

## Signal Methods

### CAN Signals

```python
def set_can_signal(
    self, can_signal_name: str, can_signal_value: int | str,
    wait: int = DEFAULT_SIGNAL_WAIT_SET  # 50ms
) -> None:
    """Set CAN signal. Format: "Network::ECU::Message::Signal"
    Example: self.set_can_signal("J1939_1::BBM::VMCU::VehicleMode", 6)"""

def check_can_signal(
    self, can_signal_name: str, value: int,
    wait: int = DEFAULT_SIGNAL_WAIT  # 2000ms
) -> None:
    """Check CAN signal has expected value over wait period."""

def check_can_signal_statechange(
    self, in_can_signal_name: str, in_value: int | str,
    out_can_signal_name: str, out_value: int | str,
    wait: int = DEFAULT_SIGNAL_WAIT, title: str = "Check GW"
) -> None:
    """Set input CAN signal and verify output signal changes."""
```

### LIN Signals

```python
def set_lin_signal(
    self, LIN_signal_name: str, LIN_signal_value: int | str,
    wait: int = DEFAULT_SIGNAL_WAIT_SET
) -> None:
    """Set LIN signal. Format: "LINBus::Node::Message::Signal"
    Example: self.set_lin_signal("LIN5::SM1::SM1toIC3_L5::LIN_DirInd_StalkStatus_1_1", 1)"""

def check_lin_signal_statechange(
    self, signal_in: str, value_in: int | str,
    signal_out: str, value_out: int | str,
    wait: int = DEFAULT_WAIT_TIME,
    signaltype_in: str = SignalTypes.LIN,
    signaltype_out: str = SignalTypes.LIN,
    title: str = "Check GW"
) -> None:
    """Set input LIN signal and verify output. Supports mixed signal types (LIN, CAN, SYSVAR)."""
```

### PS/PV Signals

```python
def check_PS_signal(self, signal_name: str, expected_value: int | str) -> None:
    """Check PS/PV signal value.
    Example: self.check_PS_signal("PS_VehicleMode", 6)"""

def check_PS_signal_array(self, signal_name: str, expected_value: int | str) -> None:
    """Check PS signal array element.
    Example: self.check_PS_signal_array("PS_TrafficSitInfo1.CondType", 8)"""

def set_PS_signal(self, signalName: str, value: int, delay: int = 0) -> None:
    """Set PS/PV signal value."""

def check_PS_DWMDTCStatChange(self, NPPId: int | str, Status: int | str) -> None:
    """Check DWM DTC status change. Status: 0=cleared, 1=active.
    Example: self.check_PS_DWMDTCStatChange(155, 1)"""
```

### System Variables

```python
def set_sysvar(
    self, sysvar_name: str, sysvar_value: int,
    wait: int = DEFAULT_SIGNAL_WAIT_SET, title: str = "Set Signals"
) -> None:
    """Set CANoe system variable. Format: "Namespace::Name"
    Example: self.set_sysvar("Environment::VehicleMode", 6)"""

def check_sysvar(self, can_signal_name: str, value: int, wait: int = DEFAULT_SIGNAL_WAIT) -> None:
    """Check system variable value."""
```

---

## Navigation and UI Methods

### Navigation

```python
def navigate_to_menu(self, menu_path: str) -> None:
    """Navigate to menu path (slash-separated).
    Top-level: MAINTENANCE, VEHICLE, TRIP COMPUTER, NOTIFICATIONS, SETTINGS, RECENT CALLS
    Example: self.navigate_to_menu("VEHICLE/Climate")"""

def navigate_to_gauge(self, gauge: str) -> None:
    """Navigate to gauge view. Example: self.navigate_to_gauge("Voltmeter")"""

def navigate_to_view(self, view: str) -> None:
    """Navigate to cluster view: "analogue", "navi", "enhanced", "digital" """
```

### Button Press

```python
def press_button(self, button: str) -> None:
    """Simulate button press.
    Navigation: left, right, up, down, enter, escape/esc
    Menu: home, menu, focus
    Audio: audio, mute, volup, voldown
    Phone: greenphone, redphone, PushToTalk
    Speed Control: SpdCtrl_PauseOff, SpdCtrl_Resume, SpdCtrl_Increase,
        SpdCtrl_Decrease, SpdCtrl_Enter, SpdCtrl_CC_ACC,
        SpdCtrl_EcoSettings, SpdCtrl_DHC, SpdCtrl_TimeGap"""
```

### Settings

```python
def set_language(self, language: str) -> None:
    """Change cluster language. Must navigate to language menu first.
    Supports 34 languages including: English, German, French, Spanish, Swedish, etc."""

def set_unit(self, unit: str) -> None:
    """Select unit when in unit menu.
    Example: self.navigate_to_menu("SETTINGS/Units/Temperature"); self.set_unit("Celsius")"""
```

---

## Verification Methods

### NPP (Notification Popup)

```python
def check_NPP_on(self, NPPID: int) -> None:
    """Verify notification popup is active."""

def check_NPP_off(self, NPPID: int) -> None:
    """Verify notification popup is not active."""
```

### Toast

```python
def check_toast_on(self, NPPID: int) -> None:
    """Verify toast notification is active."""

def check_toast_off(self, NPPID: int) -> None:
    """Verify toast notification is not active."""
```

### SWTT (Software Tell-Tale)

```python
def check_swtt_on(self, swtt: str, status: int = 1, waitForBulbCheck: bool = True) -> None:
    """Check tell-tale is active. status: 1=steady, 2=blinking.
    swtt is the image path (full or partial).
    Example: self.check_swtt_on("95302248_forward_collision_warning_50x46.png", 2)"""

def check_swtt_off(self, swtt: str) -> None:
    """Check tell-tale is inactive."""
```

### Object Checking

```python
def check_object_on(
    self, object_name: str, property_name: str,
    property_value: str, visibility: str
) -> None:
    """Check screen object property. visibility: "true" or "false".
    Example: self.check_object_on("mainCruiseStateIcon", "iconName",
        "downhill_cruise_icon_95301499_60x48.png", "false")"""
```

---

## Utility Methods

```python
def delay(self, delay_ms: int, reason: str = "Set Signals") -> None:
    """Add delay in milliseconds."""

def reset(self, ecu: str) -> None:
    """Reset ECU ("IC3" or "GFX") and wait for GFX to come back online."""

def block_frame(self, frame: str) -> None:
    """Block CAN frame (fault injection). Must call unblock_frame() at test end."""

def unblock_frame(self, frame: str) -> None:
    """Unblock previously blocked CAN frame."""

def start_new_driving_cycle(self) -> None:
    """Start new driving cycle. Transitions to Hibernate then back to PreRunning."""

def set_verdict_warning(self) -> None:
    """Set test verdict to warning (passes but shows warning in vtestreport)."""

def set_verdict_fail(self) -> None:
    """Set test verdict to fail."""
```

---

## Enumerations

```python
from vbc_paqr.framework.python2xml.TestCase import VehicleMode

class VehicleMode(IntEnum):
    Hibernate = 0      # System off
    Parked = 1         # Parked
    Living = 2         # Living mode
    Accessory = 3      # Accessory mode
    PreRunning = 4     # Pre-running (default)
    Cranking = 5       # Engine cranking
    Running = 6        # Engine running
```

---

## Type Definitions and Constants

```python
# ParameterSet (TypedDict)
class ParameterSet(TypedDict):
    title: str       # Descriptive title for parameter set
    IC3: dict        # IC3 parameters (DOID: value)
    GFX: dict        # GFX parameters (DOID: value)

# Wait time constants (milliseconds)
DEFAULT_WAIT_TIME = 200
DEFAULT_SIGNAL_WAIT = 2000
DEFAULT_SIGNAL_WAIT_SET = 50

# Signal types
class SignalTypes(IntEnum):
    CAN = 0
    LIN = 1
    SYSVAR = 2
```

---

*API Reference - Last Updated: 2026-03-03*
