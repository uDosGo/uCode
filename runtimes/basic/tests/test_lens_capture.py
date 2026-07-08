#!/usr/bin/env python3
"""
Integration tests for the LENS program registry and capture/restore
infrastructure in gridcore_adapter.py.

Verifies that:
- LENS program registry lists Repton, Elite, NetHack, and Eamon
- LENS CAPTURE/LIST/RESTORE commands work through dispatch_command
- Mock emulator can exercise extractor properties
- Error handling works for unknown programs

Run: python -m pytest runtimes/basic/tests/test_lens_capture.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bridge"))

# Import the adapter's module-level functions directly
import gridcore_adapter  # noqa: E402


class TestLensRegistry:
    """Verify the LENS program registry is configured correctly."""

    def test_list_programs_returns_expected_programs(self):
        programs = gridcore_adapter.list_programs()
        assert "repton" in programs, f"Expected 'repton' in programs, got: {programs}"
        assert "elite" in programs, f"Expected 'elite' in programs, got: {programs}"
        assert "nethack" in programs, f"Expected 'nethack' in programs, got: {programs}"
        assert "eamon" in programs, f"Expected 'eamon' in programs, got: {programs}"
        assert len(programs) >= 4, f"Expected at least 4 programs, got: {len(programs)}"

    def test_list_programs_is_sorted(self):
        programs = gridcore_adapter.list_programs()
        assert programs == sorted(programs), f"Programs should be sorted: {programs}"


class TestLensCommands:
    """Verify LENS commands dispatch through the adapter."""

    def test_lens_command_alone_shows_usage(self):
        result = gridcore_adapter.dispatch_command("LENS")
        output = result["output"]
        if isinstance(output, list):
            output = " ".join(output)
        assert "capture/restore" in output.lower() or "LENS" in output

    def test_lens_help_shows_programs(self):
        result = gridcore_adapter.dispatch_command("LENS HELP")
        output = result["output"]
        assert isinstance(output, list), f"Expected list output, got: {type(output)}"
        combined = " ".join(output)
        assert "repton" in combined, f"Expected 'repton' in LENS HELP: {combined}"
        assert "elite" in combined, f"Expected 'elite' in LENS HELP: {combined}"
        assert "nethack" in combined, f"Expected 'nethack' in LENS HELP: {combined}"
        assert "eamon" in combined, f"Expected 'eamon' in LENS HELP: {combined}"

    def test_lens_list_shows_programs(self):
        result = gridcore_adapter.dispatch_command("LENS LIST")
        output = result["output"]
        assert isinstance(output, list), f"Expected list output, got: {type(output)}"
        combined = " ".join(output)
        assert "repton" in combined, f"Expected 'repton' in LENS LIST: {combined}"
        assert "elite" in combined, f"Expected 'elite' in LENS LIST: {combined}"
        assert "nethack" in combined, f"Expected 'nethack' in LENS LIST: {combined}"
        assert "eamon" in combined, f"Expected 'eamon' in LENS LIST: {combined}"

    def test_lens_capture_repton(self):
        """Capture should load extractor and report snapshot success."""
        result = gridcore_adapter.dispatch_command("LENS CAPTURE repton")
        output = result["output"]
        assert isinstance(output, str), f"Expected string output, got: {type(output)}"
        assert "snapshot taken" in output.lower(), f"Expected successful snapshot: {output}"

    def test_lens_capture_nethack(self):
        result = gridcore_adapter.dispatch_command("LENS CAPTURE nethack")
        output = result["output"]
        assert isinstance(output, str), f"Expected string output, got: {type(output)}"
        assert "snapshot taken" in output.lower(), f"Expected successful snapshot: {output}"

    def test_lens_capture_unknown_program(self):
        result = gridcore_adapter.dispatch_command("LENS CAPTURE nonexistent")
        output = result["output"]
        assert "not found" in output.lower() or "failed" in output.lower()

    def test_lens_restore_returns_simulated(self):
        result = gridcore_adapter.dispatch_command("LENS RESTORE repton")
        output = result["output"]
        assert "simulated" in output.lower() or "restored" in output.lower()


class TestCaptureProgramState:
    """Verify capture_program_state handles edge cases gracefully."""

    def test_none_for_unknown_program(self):
        state = gridcore_adapter.capture_program_state("totally_fake_program")
        assert state is None, f"Expected None for unknown program, got: {state}"

    def test_returns_state_for_registered_program(self):
        state = gridcore_adapter.capture_program_state("elite")
        assert isinstance(state, dict), f"Expected dict, got: {type(state)}"
        assert len(state) > 0, f"Expected non-empty state, got: {state}"


class TestMockEmulator:
    """
    A mock 6502 emulator that implements read_byte, read_uint16, read_uint32.
    This exercises the LENS extractor pattern without a real emulator.
    """

    def __init__(self, memory=None):
        self.memory = memory or {}

    def read_byte(self, addr):
        return self.memory.get(addr, 0)

    def read_uint16(self, addr):
        lo = self.read_byte(addr)
        hi = self.read_byte(addr + 1)
        return (hi << 8) | lo

    def read_uint32(self, addr):
        lo = self.read_uint16(addr)
        hi = self.read_uint16(addr + 2)
        return (hi << 16) | lo

    def write_byte(self, addr, value):
        self.memory[addr] = value & 0xFF


class TestMockEmulatorBasics:
    def test_create_with_empty_memory(self):
        emu = TestMockEmulator()
        assert emu is not None

    def test_read_byte_from_empty_memory(self):
        emu = TestMockEmulator()
        assert emu.read_byte(0x0222) == 0

    def test_read_byte_with_data(self):
        emu = TestMockEmulator({0x0902: 3, 0x0900: 0, 0x0901: 0})
        assert emu.read_byte(0x0902) == 3

    def test_write_byte(self):
        emu = TestMockEmulator()
        emu.write_byte(0x0902, 5)
        assert emu.read_byte(0x0902) == 5

    def test_read_uint16(self):
        emu = TestMockEmulator({0x0234: 0x20, 0x0235: 0x4E})
        val = emu.read_uint16(0x0234)
        assert val == 0x4E20  # little-endian

    def test_read_uint32(self):
        emu = TestMockEmulator({0x0200: 0x64, 0x0201: 0x00, 0x0202: 0x00, 0x0203: 0x01})
        val = emu.read_uint32(0x0200)
        assert val == 0x01000064  # little-endian

    def test_lens_extractor_pattern_with_mock(self):
        """
        Simulates what repton_lens.py / elite_lens.py do:
        - Initialize with emu instance
        - Read memory-mapped game state variables
        - Return structured dict via capture_all()
        """
        emu = TestMockEmulator({
            0x0902: 3,     # LIVES = 3
            0x0900: 0,     # SCORE_LO = 0
            0x0901: 0,     # SCORE_HI = 0
            0x0903: 1,     # LEVEL_NUM = 1
            0x0905: 0xFF,  # TIME_REMAINING = 255
            0x0904: 0,     # REPTOL_STATE = 0 (idle)
        })

        # This is exactly what repton_lens.py would do
        state = {
            "lives": emu.read_byte(0x0902),
            "level_num": emu.read_byte(0x0903),
            "time_remaining": emu.read_byte(0x0905),
            "reptol_state": emu.read_byte(0x0904),
            "score": emu.read_uint16(0x0900),
        }

        assert state["lives"] == 3
        assert state["level_num"] == 1
        assert state["time_remaining"] == 255
        assert state["reptol_state"] == 0
        assert state["score"] == 0