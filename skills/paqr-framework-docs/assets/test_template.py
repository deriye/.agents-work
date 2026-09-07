"""
PAQR Test Template
Use this template as a starting point for creating new PAQR test cases.
See api_reference.md for full method documentation.
"""

from enum import IntEnum
from pathlib import Path

from vbc_paqr.framework.python2xml.TestCase import GWTest, VehicleMode


# Define IntEnum classes for signal values instead of using magic numbers.
# IntEnum members are ints and work directly with set_can_signal/check_PS_signal.
# Example:
# class InactiveActive(IntEnum):
#     Inactive = 0
#     Active = 1
#     Error = 2
#     NotAvailable = 3


class Test(GWTest):
    """
    Test class for PAQR test case.

    Change base class based on test type:
    - GWTest: Gateway/signal routing tests (most common)
    - DTCTest: Diagnostic trouble code tests
    - TestCase: Generic custom tests
    """

    # REQUIRED: Complete metadata dictionary
    metadata = {
        "metadata_version": "2.0",
        "tags": ["AI"],  # Only add AI tag, leave rest as is
        "testcase_name": "TODO: test name",
        "req_title": "TODO: Requirement title",
        "req_xid": "TODO: x04000000001234AB",
        "req_id": "TODO: Req-1234",
        "req_version": "1",
        "manual_test_case_xids": [],
        "is_stable": False,  # Set to False when creating or modifying
        "reason_not_stable": "",
        "comments": "",
    }

    # REQUIRED: Test title
    title = "TODO: Test Title"

    # REQUIRED: ECU parameter configuration (can be empty dicts)
    IC3_Parameters = {}  # Example: {"P1WHR": 0, "P16V1": 1}
    GFX_Parameters = {}  # Example: {"P10DO": 0}

    # OPTIONAL: Multi-parameter configurations
    # IC3GFX_multiparam = [
    #     {"title": "Config A", "IC3": {"P1WHR": 0}, "GFX": {}},
    #     {"title": "Config B", "IC3": {"P1WHR": 1}, "GFX": {}}
    # ]

    # REQUIRED: Vehicle modes to test
    # vehiclemodes = [VehicleMode.PreRunning, ...]

    def run(self):
        """REQUIRED: Implement test logic here. See api_reference.md for all available methods."""
        # Example: Simple gateway test
        # for value in [0, 1, 2, 3]:
        #     self.set_can_signal("J1939_1::ECU::MSG::InputSignal", value)
        #     self.check_PS_signal("PS_OutputSignal", value)
        pass


# XML generation for standalone testing
if __name__ == "__main__":
    test_xml = Test().to_xml()
    output_dir = Path("test_xml")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{Test.title}.xml"
    output_file.write_text(test_xml)
    print(f"Test XML written to {output_file.resolve()}")
