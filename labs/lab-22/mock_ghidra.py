"""
Mock Ghidra module for testing export_functions.py without Ghidra.

Simulates the subset of the Ghidra API used in this lab:
  - Program.getName()
  - Program.getFunctionManager()
  - FunctionManager.getFunctions(forward)
  - Function.getName()
  - Function.getEntryPoint()
  - Function.getBody().getNumAddresses()
"""


class MockAddress:
    """Simulates ghidra.program.model.address.Address."""

    def __init__(self, offset):
        self._offset = offset

    def getOffset(self):
        return self._offset

    def __str__(self):
        return f"{self._offset:08x}"


class MockAddressSet:
    """Simulates ghidra.program.model.address.AddressSetView."""

    def __init__(self, size):
        self._size = size

    def getNumAddresses(self):
        return self._size


class MockFunction:
    """Simulates ghidra.program.model.listing.Function."""

    def __init__(self, name, entry_offset, size):
        self._name = name
        self._entry = MockAddress(entry_offset)
        self._body = MockAddressSet(size)

    def getName(self):
        return self._name

    def getEntryPoint(self):
        return self._entry

    def getBody(self):
        return self._body


class MockFunctionManager:
    """Simulates ghidra.program.model.listing.FunctionManager."""

    def __init__(self, functions):
        self._functions = list(functions)

    def getFunctions(self, forward=True):
        if forward:
            return iter(self._functions)
        return iter(reversed(self._functions))


class MockProgram:
    """Simulates ghidra.program.model.listing.Program."""

    def __init__(self, name, functions):
        self._name = name
        self._fm = MockFunctionManager(functions)

    def getName(self):
        return self._name

    def getFunctionManager(self):
        return self._fm


# ---------------------------------------------------------------------------
# Pre-built test fixture
# ---------------------------------------------------------------------------

def make_test_program():
    """Create a MockProgram with several functions for testing."""
    funcs = [
        MockFunction("entry",     0x08000000, 16),
        MockFunction("main",      0x08000100, 64),
        MockFunction("init_hw",   0x08000200, 32),
        MockFunction("game_loop", 0x08000300, 128),
        MockFunction("vblank_isr", 0x08000500, 48),
    ]
    return MockProgram("test_binary", funcs)
