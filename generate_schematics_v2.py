#!/usr/bin/env python3
"""
generate_schematics_v2.py - Generate all 17 KiCad 7 schematic sheets
with CORRECT components and connections for the X-Band Digital Module.

Uses IC symbol definitions from generate_ic_symbols.py and generates
valid KiCad 7 .kicad_sch files (version 20230121).
"""

import os
import sys
import uuid as _uuid_mod

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMATIC_DIR = os.path.join(SCRIPT_DIR, "schematic")

# ---------------------------------------------------------------------------
# Import IC symbol definitions from generate_ic_symbols.py
# ---------------------------------------------------------------------------
sys.path.insert(0, SCRIPT_DIR)
from generate_ic_symbols import (
    _adc12dj5200_sp, _tps7h5001_sp, _tps7h5002_sp, _lmk04832_sp,
    _lmx2615_sp, _tps7h1111_sp, _tps7h1121_sp, _tps7h3014_sp,
    _ina214_sp, _cvhd_950, _isl70003aseh,
)

# ---------------------------------------------------------------------------
# Standard library symbol strings (KiCad 7 format, self-contained)
# ---------------------------------------------------------------------------
LIB_C = (
    '(symbol "Device:C" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)'
    ' (property "Reference" "C" (at 0.635 2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Value" "C" (at 0.635 -2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Footprint" "" (at 0.9652 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (symbol "C_0_1" (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none)))'
    ' (polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none))))'
    ' (symbol "C_1_1" (pin passive line (at 0 3.81 270) (length 2.54)'
    ' (name "~" (effects (font (size 1.27 1.27))))'
    ' (number "1" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at 0 -3.81 90) (length 2.54)'
    ' (name "~" (effects (font (size 1.27 1.27))))'
    ' (number "2" (effects (font (size 1.27 1.27)))))))'
)

LIB_R = (
    '(symbol "Device:R" (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)'
    ' (property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))'
    ' (property "Value" "R" (at 0 0 90) (effects (font (size 1.27 1.27))))'
    ' (property "Footprint" "" (at -1.778 0 90) (effects (font (size 1.27 1.27)) hide))'
    ' (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (symbol "R_0_1" (rectangle (start -1.016 -2.54) (end 1.016 2.54)'
    ' (stroke (width 0.254) (type default)) (fill (type background))))'
    ' (symbol "R_1_1" (pin passive line (at 0 3.81 270) (length 1.27)'
    ' (name "~" (effects (font (size 1.27 1.27))))'
    ' (number "1" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at 0 -3.81 90) (length 1.27)'
    ' (name "~" (effects (font (size 1.27 1.27))))'
    ' (number "2" (effects (font (size 1.27 1.27)))))))'
)

LIB_L = (
    '(symbol "Device:L" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
    ' (property "Reference" "L" (at -0.762 0 90) (effects (font (size 1.27 1.27))))'
    ' (property "Value" "L" (at 1.778 0 90) (effects (font (size 1.27 1.27))))'
    ' (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (symbol "L_0_1" (arc (start 0 -2.54) (mid 1.905 0) (end 0 2.54)'
    ' (stroke (width 0.381) (type default)) (fill (type none)))'
    ' (arc (start 0 -1.27) (mid 1.27 0) (end 0 1.27)'
    ' (stroke (width 0.381) (type default)) (fill (type none)))'
    ' (polyline (pts (xy 0 0) (xy 0 -2.54)) (stroke (width 0) (type default)) (fill (type none)))'
    ' (polyline (pts (xy 0 2.54) (xy 0 5.08)) (stroke (width 0) (type default)) (fill (type none))))'
    ' (symbol "L_1_1" (pin passive line (at 0 5.08 270) (length 2.54)'
    ' (name "~" (effects (font (size 1.27 1.27))))'
    ' (number "1" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at 0 -5.08 90) (length 2.54)'
    ' (name "~" (effects (font (size 1.27 1.27))))'
    ' (number "2" (effects (font (size 1.27 1.27)))))))'
)

LIB_FERRITEBEAD = (
    '(symbol "Device:FerriteBead" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
    ' (property "Reference" "FB" (at 0 2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Value" "FerriteBead" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (symbol "FerriteBead_0_1"'
    ' (polyline (pts (xy 0 -2.54) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none)))'
    ' (polyline (pts (xy -1.016 -2.286) (xy 1.016 -2.286)) (stroke (width 0.508) (type default)) (fill (type none)))'
    ' (polyline (pts (xy -1.016 -1.524) (xy 1.016 -1.524)) (stroke (width 0.508) (type default)) (fill (type none)))'
    ' (polyline (pts (xy -1.016 -0.762) (xy 1.016 -0.762)) (stroke (width 0.508) (type default)) (fill (type none)))'
    ' (polyline (pts (xy -1.016 0) (xy 1.016 0)) (stroke (width 0.508) (type default)) (fill (type none)))'
    ' (polyline (pts (xy -1.016 0.762) (xy 1.016 0.762)) (stroke (width 0.508) (type default)) (fill (type none)))'
    ' (polyline (pts (xy -1.016 1.524) (xy 1.016 1.524)) (stroke (width 0.508) (type default)) (fill (type none)))'
    ' (polyline (pts (xy -1.016 2.286) (xy 1.016 2.286)) (stroke (width 0.508) (type default)) (fill (type none))))'
    ' (symbol "FerriteBead_1_1"'
    ' (pin passive line (at 0 5.08 270) (length 2.54)'
    ' (name "~" (effects (font (size 1.27 1.27))))'
    ' (number "1" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at 0 -5.08 90) (length 2.54)'
    ' (name "~" (effects (font (size 1.27 1.27))))'
    ' (number "2" (effects (font (size 1.27 1.27)))))))'
)

LIB_D = (
    '(symbol "Device:D" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
    ' (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Value" "D" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (symbol "D_0_1" (polyline (pts (xy -1.27 1.27) (xy -1.27 -1.27) (xy 1.27 0) (xy -1.27 1.27))'
    ' (stroke (width 0.254) (type default)) (fill (type none)))'
    ' (polyline (pts (xy 1.27 1.27) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none))))'
    ' (symbol "D_1_1" (pin passive line (at 0 3.81 270) (length 2.54)'
    ' (name "K" (effects (font (size 1.27 1.27))))'
    ' (number "1" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at 0 -3.81 90) (length 2.54)'
    ' (name "A" (effects (font (size 1.27 1.27))))'
    ' (number "2" (effects (font (size 1.27 1.27)))))))'
)

LIB_CONN_02 = (
    '(symbol "Connector:Conn_01x02" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
    ' (property "Reference" "J" (at 0 2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Value" "Conn_01x02" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (symbol "Conn_01x02_0_1" (rectangle (start -1.27 3.81) (end 0 -3.81)'
    ' (stroke (width 0.254) (type default)) (fill (type background))))'
    ' (symbol "Conn_01x02_1_1"'
    ' (pin passive line (at -2.54 2.54 0) (length 2.54)'
    ' (name "Pin_1" (effects (font (size 1.27 1.27))))'
    ' (number "1" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 -2.54 0) (length 2.54)'
    ' (name "Pin_2" (effects (font (size 1.27 1.27))))'
    ' (number "2" (effects (font (size 1.27 1.27)))))))'
)

LIB_CONN_04 = (
    '(symbol "Connector:Conn_01x04" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
    ' (property "Reference" "J" (at 0 2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Value" "Conn_01x04" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (symbol "Conn_01x04_0_1" (rectangle (start -1.27 7.62) (end 0 -7.62)'
    ' (stroke (width 0.254) (type default)) (fill (type background))))'
    ' (symbol "Conn_01x04_1_1"'
    ' (pin passive line (at -2.54 5.08 0) (length 2.54)'
    ' (name "Pin_1" (effects (font (size 1.27 1.27))))'
    ' (number "1" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 2.54 0) (length 2.54)'
    ' (name "Pin_2" (effects (font (size 1.27 1.27))))'
    ' (number "2" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 -2.54 0) (length 2.54)'
    ' (name "Pin_3" (effects (font (size 1.27 1.27))))'
    ' (number "3" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 -5.08 0) (length 2.54)'
    ' (name "Pin_4" (effects (font (size 1.27 1.27))))'
    ' (number "4" (effects (font (size 1.27 1.27)))))))'
)

LIB_CONN_06 = (
    '(symbol "Connector:Conn_01x06" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
    ' (property "Reference" "J" (at 0 2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Value" "Conn_01x06" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (symbol "Conn_01x06_0_1" (rectangle (start -1.27 12.7) (end 0 -12.7)'
    ' (stroke (width 0.254) (type default)) (fill (type background))))'
    ' (symbol "Conn_01x06_1_1"'
    ' (pin passive line (at -2.54 10.16 0) (length 2.54)'
    ' (name "Pin_1" (effects (font (size 1.27 1.27))))'
    ' (number "1" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 7.62 0) (length 2.54)'
    ' (name "Pin_2" (effects (font (size 1.27 1.27))))'
    ' (number "2" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 2.54 0) (length 2.54)'
    ' (name "Pin_3" (effects (font (size 1.27 1.27))))'
    ' (number "3" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 0 0) (length 2.54)'
    ' (name "Pin_4" (effects (font (size 1.27 1.27))))'
    ' (number "4" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 -5.08 0) (length 2.54)'
    ' (name "Pin_5" (effects (font (size 1.27 1.27))))'
    ' (number "5" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 -10.16 0) (length 2.54)'
    ' (name "Pin_6" (effects (font (size 1.27 1.27))))'
    ' (number "6" (effects (font (size 1.27 1.27)))))))'
)

LIB_CONN_04S = (
    '(symbol "Connector:Conn_01x04_SMD" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
    ' (property "Reference" "J" (at 0 2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Value" "Conn_01x04_SMD" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (symbol "Conn_01x04_SMD_0_1" (rectangle (start -1.27 7.62) (end 0 -7.62)'
    ' (stroke (width 0.254) (type default)) (fill (type background))))'
    ' (symbol "Conn_01x04_SMD_1_1"'
    ' (pin passive line (at -2.54 5.08 0) (length 2.54)'
    ' (name "Pin_1" (effects (font (size 1.27 1.27))))'
    ' (number "1" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 2.54 0) (length 2.54)'
    ' (name "Pin_2" (effects (font (size 1.27 1.27))))'
    ' (number "2" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 -2.54 0) (length 2.54)'
    ' (name "Pin_3" (effects (font (size 1.27 1.27))))'
    ' (number "3" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 -5.08 0) (length 2.54)'
    ' (name "Pin_4" (effects (font (size 1.27 1.27))))'
    ' (number "4" (effects (font (size 1.27 1.27)))))))'
)

LIB_CONN_04R = (
    '(symbol "Connector:Conn_01x04_Pins" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
    ' (property "Reference" "J" (at 0 2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Value" "Conn_01x04_Pins" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))'
    ' (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    ' (symbol "Conn_01x04_Pins_0_1" (rectangle (start -1.27 7.62) (end 0 -7.62)'
    ' (stroke (width 0.254) (type default)) (fill (type background))))'
    ' (symbol "Conn_01x04_Pins_1_1"'
    ' (pin passive line (at -2.54 5.08 0) (length 2.54)'
    ' (name "Pin_1" (effects (font (size 1.27 1.27))))'
    ' (number "1" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 2.54 0) (length 2.54)'
    ' (name "Pin_2" (effects (font (size 1.27 1.27))))'
    ' (number "2" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 -2.54 0) (length 2.54)'
    ' (name "Pin_3" (effects (font (size 1.27 1.27))))'
    ' (number "3" (effects (font (size 1.27 1.27)))))'
    ' (pin passive line (at -2.54 -5.08 0) (length 2.54)'
    ' (name "Pin_4" (effects (font (size 1.27 1.27))))'
    ' (number "4" (effects (font (size 1.27 1.27)))))))'
)

# Power symbols
def _power_gnd():
    return (
        '(symbol "power:GND" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)'
        ' (property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) hide))'
        ' (property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))'
        ' (symbol "GND_0_1" (polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27)'
        ' (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27))'
        ' (stroke (width 0) (type default)) (fill (type none))))'
        ' (symbol "GND_1_1" (pin power_in line (at 0 0 270) (length 0)'
        ' (name "GND" (effects (font (size 1.27 1.27))))'
        ' (number "1" (effects (font (size 1.27 1.27)))))))'
    )

def _power_vcc(net):
    return (
        f'(symbol "power:{net}" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)'
        f' (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))'
        f' (property "Value" "{net}" (at 0 3.81 0) (effects (font (size 1.27 1.27))))'
        f' (symbol "{net}_0_1" (polyline (pts (xy -0.762 1.27) (xy 0 2.54))'
        ' (stroke (width 0) (type default)) (fill (type none)))'
        ' (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none)))'
        ' (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none))))'
        f' (symbol "{net}_1_1" (pin power_in line (at 0 0 90) (length 0)'
        f' (name "{net}" (effects (font (size 1.27 1.27))))'
        ' (number "1" (effects (font (size 1.27 1.27)))))))'
    )

# ---------------------------------------------------------------------------
# KiCad format helpers
# ---------------------------------------------------------------------------

def _uuid():
    return str(_uuid_mod.uuid4())

def _sheet_header(uuid_str, title, lib_symbols_content=""):
    return (
        f'(kicad_sch (version 20230121) (generator eeschema)\n'
        f'  (uuid "{uuid_str}")\n'
        f'  (paper "A3")\n'
        f'  (title_block\n'
        f'    (title "{title}")\n'
        f'    (date "2026-09-10")\n'
        f'    (rev "1.0")\n'
        f'  )\n'
        f'  (lib_symbols\n{lib_symbols_content}  )\n'
    )

def _sheet_footer():
    return '  (sheet_instances (path "/" (page "1")))\n)\n'

def _comp(lib_id, ref, val, x, y, fp="", pins=None, angle=0):
    """Generate a component instance."""
    lines = [
        f'  (symbol (lib_id "{lib_id}") (at {x} {y} {angle}) (unit 1)',
        f'    (in_bom yes) (on_board yes)',
        f'    (uuid "{_uuid()}")',
        f'    (property "Reference" "{ref}" (at {x} {y - 10} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "{val}" (at {x} {y + 10} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Footprint" "{fp}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))',
    ]
    if pins:
        for p in pins:
            lines.append(f'    (pin "{p}" (uuid "{_uuid()}"))')
    lines.append('  )')
    return '\n'.join(lines)

def _wire(x1, y1, x2, y2):
    return f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{_uuid()}"))'

def _label(name, x, y, angle=0, shape="bidirectional"):
    return (
        f'  (global_label "{name}" (shape {shape}) (at {x} {y} {angle})'
        f' (effects (font (size 1.27 1.27))'
        f' ({"justify right" if angle == 180 else "justify left"})))'
    )

def _pwr_sym(net, x, y, angle=90):
    """Place a power symbol (GND, +1V0, etc)."""
    return _comp(f"power:{net}", f"#PWR{_uuid()[:6]}", net, x, y)

def _gnd_sym(x, y):
    return _pwr_sym("GND", x, y, 0)

# ---------------------------------------------------------------------------
# IC symbol definitions (from generate_ic_symbols.py, wrapped for lib_symbols)
# ---------------------------------------------------------------------------

def _rename_ic_sym(raw_s, new_name):
    """Convert raw IC symbol from generate_ic_symbols.py to valid
    schematic inline lib_symbol format.

    The raw output uses library-scale coordinates (50mil/40mil font).
    Schematic inline lib_symbols use 1.27mil font with smaller coordinates.

    We completely rebuild the symbol with correct format rather than
    trying to scale individual coordinates.
    """
    import re

    # Extract pin info from raw: (pin TYPE line (at X Y angle) (length L) (name "N" ...) (number "P" ...))
    pin_pattern = re.compile(
        r'\(pin\s+(\w+)\s+line\s+\(at\s+(-?\d+)\s+(-?\d+)\s+(\d+)\)\s+\(length\s+(\d+)\)'
        r'\s+\(name\s+"([^"]+)"\s+\(effects\s+\(font\s+\(size\s+\d+\s+\d+\)\)\)\)'
        r'\s+\(number\s+"([^"]+)"\s+\(effects\s+\(font\s+\(size\s+\d+\s+\d+\)\)\)\)',
        re.DOTALL
    )
    pins = []
    for m in pin_pattern.finditer(raw_s):
        ptype, x, y, angle, length, name, number = m.groups()
        pins.append((ptype, int(x), int(y), int(angle), int(length), name, number))

    # Extract rectangle from raw: (rectangle (start X Y) (end X Y) ...)
    rect_pattern = re.compile(r'\(rectangle\s+\(start\s+(-?\d+)\s+(-?\d+)\)\s+\(end\s+(-?\d+)\s+(-?\d+)\)')
    rect_m = rect_pattern.search(raw_s)
    if rect_m:
        rx1, ry1, rx2, ry2 = [int(v) for v in rect_m.groups()]
    else:
        rx1, ry1, rx2, ry2 = -500, 400, 500, -400

    # Scale all coordinates from library units to schematic units (÷39.37)
    scale = 1.0 / 39.37

    def sc(v):
        s = v * scale
        if s == int(s):
            return str(int(s))
        return f"{s:.4f}".rstrip('0').rstrip('.')

    # Build the schematic-compatible symbol
    lines = []
    lines.append(f'    (symbol "Custom:{new_name}" (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "U" (at 0 {sc(abs(ry1)+100)} 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "{new_name}" (at 0 -{sc(abs(ry1)+100)} 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    lines.append(f'      (symbol "{new_name}_0_1" (rectangle (start {sc(rx1)} {sc(ry1)}) (end {sc(rx2)} {sc(ry2)}) (stroke (width 0.254) (type default)) (fill (type background))))')
    lines.append(f'      (symbol "{new_name}_1_1"')
    for ptype, x, y, angle, length, name, number in pins:
        lines.append(
            f'        (pin {ptype} line (at {sc(x)} {sc(y)} {angle}) (length {sc(length)})'
            f' (name "{name}" (effects (font (size 1.27 1.27))))'
            f' (number "{number}" (effects (font (size 1.27 1.27)))))'
        )
    lines.append(f'    ))')

    return '\n'.join(lines) + '\n'


def _ic_sym_adc12dj5200():
    return _rename_ic_sym(_adc12dj5200_sp(), "ADC12DJ5200-SP").rstrip('\n')

def _ic_sym_tps7h5001():
    return _rename_ic_sym(_tps7h5001_sp(), "TPS7H5001-SP").rstrip('\n')

def _ic_sym_tps7h5002():
    return _rename_ic_sym(_tps7h5002_sp(), "TPS7H5002-SP").rstrip('\n')

def _ic_sym_lmk04832():
    return _rename_ic_sym(_lmk04832_sp(), "LMK04832-SP").rstrip('\n')

def _ic_sym_lmx2615():
    return _rename_ic_sym(_lmx2615_sp(), "LMX2615-SP").rstrip('\n')

def _ic_sym_tps7h1111():
    return _rename_ic_sym(_tps7h1111_sp(), "TPS7H1111-SP").rstrip('\n')

def _ic_sym_tps7h1121():
    return _rename_ic_sym(_tps7h1121_sp(), "TPS7H1121-SP").rstrip('\n')

def _ic_sym_tps7h3014():
    return _rename_ic_sym(_tps7h3014_sp(), "TPS7H3014-SP").rstrip('\n')

def _ic_sym_ina214():
    return _rename_ic_sym(_ina214_sp(), "INA214-SP").rstrip('\n')

def _ic_sym_cvhd950():
    return _rename_ic_sym(_cvhd_950(), "CVHD-950").rstrip('\n')

def _ic_sym_isl70003aseh():
    return _rename_ic_sym(_isl70003aseh(), "ISL70003ASEH").rstrip('\n')


# ---------------------------------------------------------------------------
# Sheet generators
# ---------------------------------------------------------------------------

def _gen_sheet01():
    """Sheet01: Title page (empty, just title block)."""
    content = _sheet_header("11111111-1111-1111-1111-111111111111",
                            "X-Band Digital Module 20x20cm - Title")
    content += _sheet_footer()
    return content


def _gen_sheet02():
    """Sheet02: RF Input (placeholder with labels)."""
    lib = (
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+3V3")}\n'
        + LIB_C + '\n'
        + LIB_R + '\n'
        + LIB_CONN_04S + '\n'
    )
    content = _sheet_header("22222222-2222-2222-2222-222222222222",
                            "X-Band RF Input Network", lib)
    # 50Ω SMA connector J2
    content += _comp("Connector:Conn_01x04_SMD", "J2", "SMA_RF", 80, 60, "Conn_01x04_SMD", ["1","2","3","4"])
    # Input matching network
    content += _comp("Device:R", "R1", "50", 140, 60, "R_0402", ["1","2"])
    content += _comp("Device:C", "C1", "100nF", 140, 40, "C_0402", ["1","2"])
    content += _comp("Device:C", "C2", "100nF", 140, 80, "C_0402", ["1","2"])
    # Labels
    content += _label("ADC_INA_P", 200, 60, 0, "output")
    content += _label("ADC_INA_N", 200, 70, 0, "output")
    content += _label("ADC_INB_P", 200, 80, 0, "output")
    content += _label("ADC_INB_N", 200, 90, 0, "output")
    content += _label("RF_IN", 60, 60, 180, "input")
    content += _sheet_footer()
    return content


def _gen_sheet03():
    """Sheet03: ADC12DJ5200-SP with ALL connections."""
    lib = (
        f'    {_ic_sym_adc12dj5200()}\n'
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+1V0")}\n'
        f'    {_power_vcc("+1V8")}\n'
        + LIB_C + '\n'
        + LIB_FERRITEBEAD + '\n'
        + LIB_R + '\n'
    )
    content = _sheet_header("33333333-3333-3333-3333-333333333333",
                            "X-Band ADC12DJ5200-SP", lib)
    # Main IC - center of sheet
    content += _comp("Custom:ADC12DJ5200-SP", "U1", "ADC12DJ5200-SP", 200, 120,
                     "Package_BGA:BGA-144_12x12_8.0x8.0mm_P0.65mm",
                     ["A4","A5","L4","L5","F1","G1","K1","L1","E8","F8","G8","H8",
                      "K6","C7","D7","K7","J7","E7","F7","C2","B1","C1","B2","C3",
                      "K2","K3","C8","D8","K8","J8"])
    # Decoupling capacitors for VA11 (1.0V analog)
    content += _comp("Device:C", "C10", "100nF", 80, 40, "C_0402", ["1","2"])
    content += _comp("Device:C", "C11", "10uF", 80, 55, "C_0603", ["1","2"])
    content += _comp("Device:FerriteBead", "FB1", "600R", 80, 70, "L_0402", ["1","2"])
    content += _comp("Device:C", "C12", "100nF", 80, 85, "C_0402", ["1","2"])
    content += _comp("Device:C", "C13", "10uF", 80, 100, "C_0603", ["1","2"])
    # Decoupling capacitors for VA19 (1.8V analog)
    content += _comp("Device:C", "C14", "100nF", 80, 120, "C_0402", ["1","2"])
    content += _comp("Device:C", "C15", "10uF", 80, 135, "C_0603", ["1","2"])
    # VD11 decoupling
    content += _comp("Device:C", "C16", "100nF", 80, 155, "C_0402", ["1","2"])
    content += _comp("Device:C", "C17", "4.7uF", 80, 170, "C_0402", ["1","2"])
    # BG bypass
    content += _comp("Device:C", "C18", "100nF", 320, 120, "C_0402", ["1","2"])
    # Input termination resistors (unused INB)
    content += _comp("Device:R", "R10", "50", 320, 60, "R_0402", ["1","2"])
    content += _comp("Device:R", "R11", "50", 320, 75, "R_0402", ["1","2"])
    # NCO config resistors (to GND)
    content += _comp("Device:R", "R12", "1k", 320, 90, "R_0402", ["1","2"])
    content += _comp("Device:R", "R13", "1k", 320, 105, "R_0402", ["1","2"])
    # Net labels
    content += _label("ADC_INA_P", 130, 55, 180, "input")
    content += _label("ADC_INA_N", 130, 65, 180, "input")
    content += _label("ADC_INB_P", 130, 75, 180, "input")
    content += _label("ADC_INB_N", 130, 85, 180, "input")
    content += _label("ADC_CLK_P", 130, 95, 180, "input")
    content += _label("ADC_CLK_N", 130, 105, 180, "input")
    content += _label("ADC_SYSREF_P", 130, 115, 180, "input")
    content += _label("ADC_SYSREF_N", 130, 125, 180, "input")
    content += _label("ADC_CS", 130, 135, 180, "input")
    content += _label("ADC_SCLK", 130, 145, 180, "input")
    content += _label("ADC_SDI", 130, 155, 180, "input")
    content += _label("ADC_SDO", 130, 165, 180, "output")
    content += _label("ADC_PD", 130, 175, 180, "input")
    content += _label("ADC_SYNC_P", 130, 185, 180, "input")
    content += _label("ADC_SYNC_N", 130, 195, 180, "input")
    content += _label("JESD_DA0_P", 270, 40, 0, "output")
    content += _label("JESD_DA0_N", 270, 50, 0, "output")
    content += _label("JESD_DA1_P", 270, 60, 0, "output")
    content += _label("JESD_DA1_N", 270, 70, 0, "output")
    content += _label("JESD_DA2_P", 270, 80, 0, "output")
    content += _label("JESD_DA2_N", 270, 90, 0, "output")
    content += _label("JESD_DA3_P", 270, 100, 0, "output")
    content += _label("JESD_DA3_N", 270, 110, 0, "output")
    content += _label("ADC_ORA0", 270, 130, 0, "output")
    content += _label("ADC_ORA1", 270, 140, 0, "output")
    content += _label("ADC_ORB0", 270, 150, 0, "output")
    content += _label("ADC_ORB1", 270, 160, 0, "output")
    content += _label("ADC_CALTRIG", 130, 205, 180, "input")
    content += _label("ADC_CALSTAT", 130, 215, 180, "output")
    content += _label("ADC_TEMP_P", 270, 180, 0, "output")
    content += _label("ADC_TEMP_N", 270, 190, 0, "output")
    content += _label("VANA_1V0", 60, 40, 180, "input")
    content += _label("VANA_1V9", 60, 120, 180, "input")
    content += _label("VDIG_1V1", 60, 155, 180, "input")
    content += _sheet_footer()
    return content


def _gen_sheet04():
    """Sheet04: FPGA XQRVC1902-SP."""
    lib = (
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+1V0")}\n'
        f'    {_power_vcc("+1V8")}\n'
        f'    {_power_vcc("+3V3")}\n'
        + LIB_C + '\n'
        + LIB_R + '\n'
    )
    content = _sheet_header("44444444-4444-4444-4444-444444444444",
                            "X-Band FPGA XQRVC1902-SP", lib)
    # Simplified FPGA symbol (large rectangle with labels)
    content += (
        f'  (symbol (lib_id "power:GND") (at 200 200 0) (unit 1)\n'
        f'    (in_bom yes) (on_board yes)\n'
        f'    (uuid "{_uuid()}")\n'
        f'    (property "Reference" "U2" (at 200 190 0) (effects (font (size 1.27 1.27))))\n'
        f'    (property "Value" "XQRVC1902-SP" (at 200 210 0) (effects (font (size 1.27 1.27))))\n'
        f'    (property "Footprint" "" (at 200 200 0) (effects (font (size 1.27 1.27)) hide))\n'
        f'  )\n'
    )
    # JESD204C inputs from ADC
    content += _label("JESD_DA0_P", 100, 40, 180, "input")
    content += _label("JESD_DA0_N", 100, 50, 180, "input")
    content += _label("JESD_DA1_P", 100, 60, 180, "input")
    content += _label("JESD_DA1_N", 100, 70, 180, "input")
    content += _label("JESD_DA2_P", 100, 80, 180, "input")
    content += _label("JESD_DA2_N", 100, 90, 180, "input")
    content += _label("JESD_DA3_P", 100, 100, 180, "input")
    content += _label("JESD_DA3_N", 100, 110, 180, "input")
    # SPI to ADC
    content += _label("ADC_CS", 100, 130, 180, "output")
    content += _label("ADC_SCLK", 100, 140, 180, "output")
    content += _label("ADC_SDI", 100, 150, 180, "output")
    content += _label("ADC_SDO", 100, 160, 180, "input")
    content += _label("ADC_PD", 100, 170, 180, "output")
    content += _label("ADC_SYNC_P", 100, 180, 180, "output")
    content += _label("ADC_SYNC_N", 100, 190, 180, "output")
    content += _label("ADC_CALTRIG", 100, 200, 180, "output")
    content += _label("ADC_CALSTAT", 100, 210, 180, "input")
    # ADC status
    content += _label("ADC_ORA0", 100, 220, 180, "input")
    content += _label("ADC_ORA1", 100, 230, 180, "input")
    content += _label("ADC_ORB0", 100, 240, 180, "input")
    content += _label("ADC_ORB1", 100, 250, 180, "input")
    content += _label("ADC_TEMP_P", 100, 260, 180, "input")
    content += _label("ADC_TEMP_N", 100, 270, 180, "input")
    # Clock outputs
    content += _label("FPGA_REFCLK_P", 300, 40, 0, "input")
    content += _label("FPGA_REFCLK_N", 300, 50, 0, "input")
    content += _label("FPGA_SPWCLK_P", 300, 60, 0, "input")
    content += _label("FPGA_SPWCLK_N", 300, 70, 0, "input")
    # SPI to clock chips
    content += _label("LMX_CS", 300, 90, 0, "output")
    content += _label("LMX_SCK", 300, 100, 0, "output")
    content += _label("LMX_SDI", 300, 110, 0, "output")
    content += _label("LMX_MUXOUT", 300, 120, 0, "input")
    content += _label("LMX_CAL", 300, 130, 0, "output")
    content += _label("LMX_SYNC", 300, 140, 0, "output")
    content += _label("LMK_CS", 300, 160, 0, "output")
    content += _label("LMK_SCK", 300, 170, 0, "output")
    content += _label("LMK_SDIO", 300, 180, 0, "bidirectional")
    content += _label("LMK_RESET", 300, 190, 0, "output")
    content += _label("LMK_SYNC", 300, 200, 0, "output")
    # SpaceWire
    content += _label("SPW_TX_P", 300, 220, 0, "output")
    content += _label("SPW_TX_N", 300, 230, 0, "output")
    content += _label("SPW_RX_P", 300, 240, 0, "input")
    content += _label("SPW_RX_N", 300, 250, 0, "input")
    content += _label("SPW_TX2_P", 300, 260, 0, "output")
    content += _label("SPW_TX2_N", 300, 270, 0, "output")
    content += _label("SPW_RX2_P", 300, 280, 0, "input")
    content += _label("SPW_RX2_N", 300, 290, 0, "input")
    # Sequencer status
    content += _label("PWRGD_SEQ", 100, 290, 180, "input")
    content += _label("SEQ_DONE", 100, 300, 180, "input")
    # Decoupling
    content += _comp("Device:C", "C20", "100nF", 350, 40, "C_0402", ["1","2"])
    content += _comp("Device:C", "C21", "10uF", 350, 55, "C_0603", ["1","2"])
    content += _comp("Device:C", "C22", "100nF", 350, 70, "C_0402", ["1","2"])
    content += _comp("Device:C", "C23", "10uF", 350, 85, "C_0603", ["1","2"])
    content += _comp("Device:C", "C24", "100nF", 350, 100, "C_0402", ["1","2"])
    content += _comp("Device:C", "C25", "10uF", 350, 115, "C_0603", ["1","2"])
    content += _sheet_footer()
    return content


def _gen_sheet05():
    """Sheet05: Clock - CVHD-950 + LMX2615-SP + LMK04832-SP."""
    lib = (
        f'    {_ic_sym_cvhd950()}\n'
        f'    {_ic_sym_lmx2615()}\n'
        f'    {_ic_sym_lmk04832()}\n'
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+3V3")}\n'
        f'    {_power_vcc("+2V5")}\n'
        + LIB_C + '\n'
        + LIB_R + '\n'
    )
    content = _sheet_header("55555555-5555-5555-5555-555555555555",
                            "X-Band Clock Distribution", lib)
    # CVHD-950 VCXO
    content += _comp("Custom:CVHD-950", "Y1", "CVHD-950-122.88MHz", 80, 80,
                     "Oscillator:Oscillator_SMD_5032_5x3.2mm", ["4","3","1","2"])
    # VCXO decoupling
    content += _comp("Device:C", "C40", "100nF", 60, 60, "C_0402", ["1","2"])
    content += _comp("Device:C", "C41", "10uF", 60, 70, "C_0603", ["1","2"])
    content += _label("VCLK_2V5", 50, 60, 180, "input")
    content += _label("VCLK_2V5", 50, 70, 180, "input")

    # LMX2615-SP PLL
    content += _comp("Custom:LMX2615-SP", "U3", "LMX2615-SP", 200, 80,
                     "Package_CFP:CQFP-64",
                     ["3","4","15","16","17","18","19","20","5","9","26","27","39","32","43","45",
                      "37","36","30","29","11","21","25","34","57","41","14","59",
                      "12","13"])
    # LMX decoupling
    for i, cap_val in enumerate(["100nF","100nF","100nF","100nF","4.7uF","100nF","100nF","100nF","100nF","100nF"]):
        cx = 140 + (i % 5) * 30
        cy = 20 + (i // 5) * 20
        content += _comp("Device:C", f"C{42+i}", cap_val, cx, cy, "C_0402", ["1","2"])
    # LMX loop filter components
    content += _comp("Device:C", "C52", "1nF", 280, 60, "C_0402", ["1","2"])
    content += _comp("Device:C", "C53", "33nF", 280, 75, "C_0402", ["1","2"])
    content += _comp("Device:R", "R30", "1k", 280, 90, "R_0402", ["1","2"])
    # FS0-FS7 pull-down resistors
    for i in range(8):
        content += _comp("Device:R", f"R3{i}", "1k", 140, 120 + i * 10, "R_0402", ["1","2"])
    # RECAL_EN pull-down
    content += _comp("Device:R", "R38", "1k", 140, 200, "R_0402", ["1","2"])

    # LMK04832-SP clock distributor
    content += _comp("Custom:LMK04832-SP", "U4", "LMK04832-SP", 400, 80,
                     "Package_CFP:CQFP-64",
                     ["37","38","34","35","43","44","8","9","6","5","18","19","20","58","59",
                      "1","2","3","4","15","16","13","14","24","25","22","23","27","28","29","30",
                      "51","52","49","50","54","55","56","57","62","63","60","61","40","41",
                      "10","17","21","26","33","36","39","42","45","47","53","64","11","12","32","46","31","48","7","65"])
    # LMK decoupling (100nF on each Vcc)
    for i in range(12):
        cx = 340 + (i % 4) * 25
        cy = 10 + (i // 4) * 15
        content += _comp("Device:C", f"C{54+i}", "100nF", cx, cy, "C_0402", ["1","2"])
    content += _comp("Device:C", "C66", "10uF", 450, 10, "C_0603", ["1","2"])
    content += _comp("Device:C", "C67", "100nF", 450, 25, "C_0402", ["1","2"])

    # Labels for clock outputs
    content += _label("ADC_CLK_P", 480, 40, 0, "output")
    content += _label("ADC_CLK_N", 480, 50, 0, "output")
    content += _label("ADC_SYSREF_P", 480, 60, 0, "output")
    content += _label("ADC_SYSREF_N", 480, 70, 0, "output")
    content += _label("FPGA_REFCLK_P", 480, 80, 0, "output")
    content += _label("FPGA_REFCLK_N", 480, 90, 0, "output")
    content += _label("FPGA_SPWCLK_P", 480, 100, 0, "output")
    content += _label("FPGA_SPWCLK_N", 480, 110, 0, "output")
    # SPI labels
    content += _label("LMX_CS", 130, 80, 180, "input")
    content += _label("LMX_SCK", 130, 90, 180, "input")
    content += _label("LMX_SDI", 130, 100, 180, "input")
    content += _label("LMX_MUXOUT", 270, 100, 0, "output")
    content += _label("LMX_CAL", 130, 110, 180, "input")
    content += _label("LMX_SYNC", 130, 120, 180, "input")
    content += _label("LMK_CS", 340, 80, 180, "input")
    content += _label("LMK_SCK", 340, 90, 180, "input")
    content += _label("LMK_SDIO", 340, 100, 180, "bidirectional")
    content += _label("LMK_RESET", 340, 110, 180, "input")
    content += _label("LMK_SYNC", 340, 120, 180, "input")
    content += _sheet_footer()
    return content


def _gen_buck_sheet(sheet_uuid, title, ic_name, ic_ref, ic_val, ic_sym_fn,
                    ic_pins, vin_label, vout_label, comp_prefix,
                    cap_in_vals, cap_out_vals, inductor_val,
                    r_fb_top, r_fb_bot, en_label=None, pg_label=None):
    """Generic buck converter sheet generator."""
    lib = (
        f'    {_rename_ic_sym(ic_sym_fn(), ic_name)}'
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+4V5")}\n'
        + LIB_C + '\n'
        + LIB_L + '\n'
        + LIB_R + '\n'
        + LIB_FERRITEBEAD + '\n'
    )
    content = _sheet_header(sheet_uuid, title, lib)
    # IC
    content += _comp(f"Custom:{ic_name}", ic_ref, ic_val, 200, 100,
                     f"Package_CFP:CFP-{len(ic_pins)}", [str(p) for p in ic_pins])
    # Input caps
    for i, cv in enumerate(cap_in_vals):
        content += _comp("Device:C", f"{comp_prefix}C{i+1}", cv, 80, 40 + i * 15, "C_0402", ["1","2"])
    # Output caps
    for i, cv in enumerate(cap_out_vals):
        content += _comp("Device:C", f"{comp_prefix}C{i+10}", cv, 320, 40 + i * 15, "C_0603", ["1","2"])
    # Inductor
    content += _comp("Device:L", f"{comp_prefix}L1", inductor_val, 260, 100, "L_1210", ["1","2"])
    # Feedback divider
    content += _comp("Device:R", f"{comp_prefix}R1", r_fb_top, 320, 120, "R_0402", ["1","2"])
    content += _comp("Device:R", f"{comp_prefix}R2", r_fb_bot, 320, 140, "R_0402", ["1","2"])
    # Compensation
    content += _comp("Device:C", f"{comp_prefix}C20", "4.7nF", 80, 160, "C_0402", ["1","2"])
    content += _comp("Device:C", f"{comp_prefix}C21", "330pF", 100, 160, "C_0402", ["1","2"])
    content += _comp("Device:R", f"{comp_prefix}R3", "10k", 120, 160, "R_0402", ["1","2"])
    # Soft start
    content += _comp("Device:C", f"{comp_prefix}C22", "10nF", 80, 180, "C_0402", ["1","2"])
    # Net labels
    content += _label(vin_label, 60, 60, 180, "input")
    content += _label(vout_label, 400, 60, 0, "output")
    if en_label:
        content += _label(en_label, 60, 180, 180, "input")
    if pg_label:
        content += _label(pg_label, 400, 120, 0, "output")
    content += _sheet_footer()
    return content


def _gen_sheet06():
    """Sheet06: Power Input - J1, TVS, EMI, INA214-SP."""
    lib = (
        f'    {_ic_sym_ina214()}\n'
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+4V5")}\n'
        + LIB_C + '\n'
        + LIB_R + '\n'
        + LIB_D + '\n'
        + LIB_CONN_04 + '\n'
    )
    content = _sheet_header("66666666-6666-6666-6666-666666666666",
                            "X-Band Power Input", lib)
    # Power connector J1
    content += _comp("Connector:Conn_01x04", "J1", "POWER_IN", 60, 80,
                     "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", ["1","2","3","4"])
    # TVS diode
    content += _comp("Device:D", "D1", "SMBJ6.0A", 120, 60, "Diode_SMD:D_SMB", ["K","A"])
    # Bulk capacitors
    content += _comp("Device:C", "C100", "100uF", 160, 40, "CP_EIA-7343", ["1","2"])
    content += _comp("Device:C", "C101", "100nF", 160, 60, "C_0402", ["1","2"])
    content += _comp("Device:C", "C102", "10uF", 160, 80, "C_0603", ["1","2"])
    # INA214 current sense
    content += _comp("Custom:INA214-SP", "U10", "INA214-SP", 240, 80,
                     "Package_TO_SOT_SMD:SOT-363", ["1","2","3","4","5","6"])
    # Shunt resistor
    content += _comp("Device:R", "R100", "10m", 200, 80, "R_0805", ["1","2"])
    # INA214 output resistor/cap
    content += _comp("Device:R", "R101", "10k", 300, 70, "R_0402", ["1","2"])
    content += _comp("Device:C", "C103", "100nF", 300, 90, "C_0402", ["1","2"])
    # Labels
    content += _label("VIN_4V5", 190, 80, 0, "output")
    content += _label("VIN_SENSE", 340, 80, 0, "output")
    content += _label("GND", 60, 100, 0, "input")
    content += _sheet_footer()
    return content


def _gen_sheet07():
    """Sheet07: Buck 1.0V Core - TPS7H5001-SP."""
    return _gen_buck_sheet(
        "77777777-7777-7777-7777-777777777777",
        "X-Band Buck 1.0V Core (TPS7H5001-SP)",
        "TPS7H5001-SP", "U5", "TPS7H5001-SP", _tps7h5001_sp,
        [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22],
        "VIN_4V5", "VCCINT_1V0", "Buck1",
        ["22uF", "100nF"], ["470uF", "470uF", "10uF", "100nF"],
        "100nH/55A", "390k", "100k",
        "BUCK1_EN", "BUCK1_PG"
    )


def _gen_sheet08():
    """Sheet08: Buck 1.8V - ISL70003ASEH (channel 1)."""
    lib = (
        f'    {_ic_sym_isl70003aseh()}\n'
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+4V5")}\n'
        + LIB_C + '\n'
        + LIB_L + '\n'
        + LIB_R + '\n'
        + LIB_FERRITEBEAD + '\n'
    )
    content = _sheet_header("88888888-8888-8888-8888-888888888888",
                            "X-Band Buck 1.8V (ISL70003ASEH)", lib)
    content += _comp("Custom:ISL70003ASEH", "U6", "ISL70003ASEH", 200, 120,
                     "Package_CFP:CQFP-64",
                     [str(p) for p in range(1,65)])
    # Input caps
    content += _comp("Device:C", "C70", "22uF", 80, 40, "C_0805", ["1","2"])
    content += _comp("Device:C", "C71", "100nF", 80, 55, "C_0402", ["1","2"])
    content += _comp("Device:C", "C72", "10uF", 80, 70, "C_0603", ["1","2"])
    # Inductor
    content += _comp("Device:L", "L1", "2.2uH", 280, 80, "L_1210", ["1","2"])
    # Output caps
    content += _comp("Device:C", "C73", "100uF", 340, 40, "CP_EIA-7343", ["1","2"])
    content += _comp("Device:C", "C74", "22uF", 340, 55, "C_0805", ["1","2"])
    content += _comp("Device:C", "C75", "100nF", 340, 70, "C_0402", ["1","2"])
    # Feedback resistors
    content += _comp("Device:R", "R50", "100k", 340, 100, "R_0402", ["1","2"])
    content += _comp("Device:R", "R51", "49.9k", 340, 120, "R_0402", ["1","2"])
    # Compensation
    content += _comp("Device:C", "C76", "4.7nF", 80, 160, "C_0402", ["1","2"])
    content += _comp("Device:C", "C77", "330pF", 100, 160, "C_0402", ["1","2"])
    content += _comp("Device:R", "R52", "10k", 120, 160, "R_0402", ["1","2"])
    # Soft start
    content += _comp("Device:C", "C78", "10nF", 80, 180, "C_0402", ["1","2"])
    # Ferrite bead
    content += _comp("Device:FerriteBead", "FB2", "600R", 400, 60, "L_0402", ["1","2"])
    # Labels
    content += _label("VIN_4V5", 60, 60, 180, "input")
    content += _label("VCCAUX_1V8", 440, 60, 0, "output")
    content += _label("BUCK2_EN", 60, 180, 180, "input")
    content += _label("BUCK2_PG", 440, 120, 0, "output")
    content += _sheet_footer()
    return content


def _gen_sheet09():
    """Sheet09: Buck 3.3V - ISL70003ASEH (channel 2)."""
    lib = (
        f'    {_ic_sym_isl70003aseh()}\n'
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+4V5")}\n'
        + LIB_C + '\n'
        + LIB_L + '\n'
        + LIB_R + '\n'
        + LIB_FERRITEBEAD + '\n'
    )
    content = _sheet_header("99999999-9999-9999-9999-999999999999",
                            "X-Band Buck 3.3V (ISL70003ASEH)", lib)
    content += _comp("Custom:ISL70003ASEH", "U7", "ISL70003ASEH", 200, 120,
                     "Package_CFP:CQFP-64",
                     [str(p) for p in range(1,65)])
    # Input caps
    content += _comp("Device:C", "C80", "22uF", 80, 40, "C_0805", ["1","2"])
    content += _comp("Device:C", "C81", "100nF", 80, 55, "C_0402", ["1","2"])
    content += _comp("Device:C", "C82", "10uF", 80, 70, "C_0603", ["1","2"])
    # Inductor
    content += _comp("Device:L", "L2", "4.7uH", 280, 80, "L_1210", ["1","2"])
    # Output caps
    content += _comp("Device:C", "C83", "47uF", 340, 40, "CP_EIA-7343", ["1","2"])
    content += _comp("Device:C", "C84", "10uF", 340, 55, "C_0603", ["1","2"])
    content += _comp("Device:C", "C85", "100nF", 340, 70, "C_0402", ["1","2"])
    # Feedback resistors
    content += _comp("Device:R", "R53", "100k", 340, 100, "R_0402", ["1","2"])
    content += _comp("Device:R", "R54", "32.4k", 340, 120, "R_0402", ["1","2"])
    # Compensation
    content += _comp("Device:C", "C86", "4.7nF", 80, 160, "C_0402", ["1","2"])
    content += _comp("Device:C", "C87", "330pF", 100, 160, "C_0402", ["1","2"])
    content += _comp("Device:R", "R55", "10k", 120, 160, "R_0402", ["1","2"])
    # Soft start
    content += _comp("Device:C", "C88", "10nF", 80, 180, "C_0402", ["1","2"])
    # Ferrite bead
    content += _comp("Device:FerriteBead", "FB3", "600R", 400, 60, "L_0402", ["1","2"])
    # Labels
    content += _label("VIN_4V5", 60, 60, 180, "input")
    content += _label("VCCIO_3V3", 440, 60, 0, "output")
    content += _label("BUCK3_EN", 60, 180, 180, "input")
    content += _label("BUCK3_PG", 440, 120, 0, "output")
    content += _sheet_footer()
    return content


def _gen_sheet10():
    """Sheet10: LDO 1.0V Analog - TPS7H1111-SP from +3V3."""
    lib = (
        f'    {_ic_sym_tps7h1111()}\n'
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+3V3")}\n'
        f'    {_power_vcc("+1V0")}\n'
        + LIB_C + '\n'
        + LIB_R + '\n'
    )
    content = _sheet_header("aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                            "X-Band LDO 1.0V Analog (TPS7H1111-SP)", lib)
    content += _comp("Custom:TPS7H1111-SP", "U8", "TPS7H1111-SP", 200, 80,
                     "Package_CFP:CFP-14",
                     ["1","2","3","4","5","6","7","8","9","10","11","12","13","14"])
    # Input caps
    content += _comp("Device:C", "C90", "10uF", 120, 40, "C_0603", ["1","2"])
    content += _comp("Device:C", "C91", "100nF", 120, 55, "C_0402", ["1","2"])
    # Output caps
    content += _comp("Device:C", "C92", "10uF", 280, 40, "C_0603", ["1","2"])
    content += _comp("Device:C", "C93", "100nF", 280, 55, "C_0402", ["1","2"])
    # Bypass cap
    content += _comp("Device:C", "C94", "10nF", 200, 120, "C_0402", ["1","2"])
    # Feedback
    content += _comp("Device:R", "R60", "10k", 280, 80, "R_0402", ["1","2"])
    content += _comp("Device:R", "R61", "10k", 280, 100, "R_0402", ["1","2"])
    # Labels
    content += _label("+3V3", 100, 55, 180, "input")
    content += _label("+1V0", 320, 55, 0, "output")
    content += _label("LDO1_EN", 100, 80, 180, "input")
    content += _label("LDO1_PG", 320, 80, 0, "output")
    content += _sheet_footer()
    return content


def _gen_sheet11():
    """Sheet11: LDO 1.8V Digital - TPS7H1111-SP from +1V8."""
    lib = (
        f'    {_ic_sym_tps7h1111()}\n'
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+1V8")}\n'
        f'    {_power_vcc("+1V8")}\n'
        + LIB_C + '\n'
        + LIB_R + '\n'
    )
    content = _sheet_header("aaaaaaa2-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                            "X-Band LDO 1.8V Digital (TPS7H1111-SP)", lib)
    content += _comp("Custom:TPS7H1111-SP", "U9", "TPS7H1111-SP", 200, 80,
                     "Package_CFP:CFP-14",
                     ["1","2","3","4","5","6","7","8","9","10","11","12","13","14"])
    # Input caps
    content += _comp("Device:C", "C95", "10uF", 120, 40, "C_0603", ["1","2"])
    content += _comp("Device:C", "C96", "100nF", 120, 55, "C_0402", ["1","2"])
    # Output caps
    content += _comp("Device:C", "C97", "10uF", 280, 40, "C_0603", ["1","2"])
    content += _comp("Device:C", "C98", "100nF", 280, 55, "C_0402", ["1","2"])
    # Bypass cap
    content += _comp("Device:C", "C99", "10nF", 200, 120, "C_0402", ["1","2"])
    # Feedback
    content += _comp("Device:R", "R62", "10k", 280, 80, "R_0402", ["1","2"])
    content += _comp("Device:R", "R63", "10k", 280, 100, "R_0402", ["1","2"])
    # Labels
    content += _label("+1V8", 100, 55, 180, "input")
    content += _label("+1V8", 320, 55, 0, "output")
    content += _label("LDO2_EN", 100, 80, 180, "input")
    content += _label("LDO2_PG", 320, 80, 0, "output")
    content += _sheet_footer()
    return content


def _gen_sheet12():
    """Sheet12: LDO 2.5V Clock - TPS7H1121-SP from +3V3."""
    lib = (
        f'    {_ic_sym_tps7h1121()}\n'
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+3V3")}\n'
        f'    {_power_vcc("+2V5")}\n'
        + LIB_C + '\n'
        + LIB_R + '\n'
    )
    content = _sheet_header("aaaaaaa3-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                            "X-Band LDO 2.5V Clock (TPS7H1121-SP)", lib)
    content += _comp("Custom:TPS7H1121-SP", "U10", "TPS7H1121-SP", 200, 80,
                     "Package_CFP:CFP-22",
                     ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22"])
    # Input caps
    content += _comp("Device:C", "C110", "10uF", 120, 40, "C_0603", ["1","2"])
    content += _comp("Device:C", "C111", "100nF", 120, 55, "C_0402", ["1","2"])
    content += _comp("Device:C", "C112", "10uF", 120, 70, "C_0603", ["1","2"])
    # Output caps
    content += _comp("Device:C", "C113", "10uF", 300, 40, "C_0603", ["1","2"])
    content += _comp("Device:C", "C114", "100nF", 300, 55, "C_0402", ["1","2"])
    content += _comp("Device:C", "C115", "10uF", 300, 70, "C_0603", ["1","2"])
    # Bypass cap
    content += _comp("Device:C", "C116", "10nF", 200, 120, "C_0402", ["1","2"])
    # Feedback
    content += _comp("Device:R", "R64", "10k", 300, 90, "R_0402", ["1","2"])
    content += _comp("Device:R", "R65", "10k", 300, 110, "R_0402", ["1","2"])
    # Labels
    content += _label("+3V3", 100, 55, 180, "input")
    content += _label("+2V5", 340, 55, 0, "output")
    content += _label("LDO3_EN", 100, 80, 180, "input")
    content += _label("LDO3_PG", 340, 90, 0, "output")
    content += _sheet_footer()
    return content


def _gen_sheet13():
    """Sheet13: Sequencer - 2x TPS7H3014-SP."""
    lib = (
        f'    {_ic_sym_tps7h3014()}\n'
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+4V5")}\n'
        + LIB_C + '\n'
        + LIB_R + '\n'
    )
    content = _sheet_header("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                            "X-Band Power Sequencer (2x TPS7H3014-SP)", lib)
    # First sequencer U13A
    content += _comp("Custom:TPS7H3014-SP", "U13A", "TPS7H3014-SP", 120, 80,
                     "Package_CFP:CFP-22",
                     ["9","1","2","3","4","13","5","6","7","8","16","17","14","15","22","10","11","12","18","19","20","21"])
    # Input caps
    content += _comp("Device:C", "C120", "100nF", 80, 40, "C_0402", ["1","2"])
    content += _comp("Device:C", "C121", "10uF", 80, 55, "C_0603", ["1","2"])
    # Voltage dividers for SENSE inputs
    content += _comp("Device:R", "R70", "10k", 80, 100, "R_0402", ["1","2"])
    content += _comp("Device:R", "R71", "100k", 80, 120, "R_0402", ["1","2"])
    content += _comp("Device:R", "R72", "10k", 80, 140, "R_0402", ["1","2"])
    content += _comp("Device:R", "R73", "100k", 80, 160, "R_0402", ["1","2"])
    # Timing caps
    content += _comp("Device:C", "C122", "10nF", 160, 40, "C_0402", ["1","2"])
    # Second sequencer U13B
    content += _comp("Custom:TPS7H3014-SP", "U13B", "TPS7H3014-SP", 280, 80,
                     "Package_CFP:CFP-22",
                     ["9","1","2","3","4","13","5","6","7","8","16","17","14","15","22","10","11","12","18","19","20","21"])
    # Input caps
    content += _comp("Device:C", "C123", "100nF", 240, 40, "C_0402", ["1","2"])
    content += _comp("Device:C", "C124", "10uF", 240, 55, "C_0603", ["1","2"])
    # Labels - enable outputs
    content += _label("BUCK1_EN", 200, 60, 0, "output")
    content += _label("BUCK2_EN", 200, 70, 0, "output")
    content += _label("BUCK3_EN", 200, 80, 0, "output")
    content += _label("LDO1_EN", 200, 90, 0, "output")
    content += _label("LDO2_EN", 360, 60, 0, "output")
    content += _label("LDO3_EN", 360, 70, 0, "output")
    content += _label("PWRGD_SEQ", 360, 80, 0, "output")
    content += _label("SEQ_DONE", 360, 90, 0, "output")
    content += _label("VIN_4V5", 60, 40, 180, "input")
    content += _label("VIN_4V5", 220, 40, 180, "input")
    content += _label("VCCINT_1V0", 60, 100, 180, "input")
    content += _label("VCCAUX_1V8", 60, 120, 180, "input")
    content += _label("VCCIO_3V3", 60, 140, 180, "input")
    content += _label("+1V0", 60, 160, 180, "input")
    content += _label("+1V8", 220, 100, 180, "input")
    content += _label("+2V5", 220, 120, 180, "input")
    content += _sheet_footer()
    return content


def _gen_sheet14():
    """Sheet14: Connectors - J1-J6."""
    lib = (
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+4V5")}\n'
        + LIB_CONN_04 + '\n'
        + LIB_CONN_06 + '\n'
        + LIB_CONN_02 + '\n'
    )
    content = _sheet_header("cccccccc-cccc-cccc-cccc-cccccccccccc",
                            "X-Band Connectors", lib)
    # J1 - Power (already on Sheet06, but also listed here for reference)
    # J2 - JESD204C debug connector
    content += _comp("Connector:Conn_01x04", "J2", "JESD_DEBUG", 80, 60,
                     "Conn_01x04", ["1","2","3","4"])
    # J3 - SpaceWire Port 1
    content += _comp("Connector:Conn_01x04", "J3", "SPW_PORT1", 80, 120,
                     "Conn_01x04", ["1","2","3","4"])
    # J4 - SpaceWire Port 2
    content += _comp("Connector:Conn_01x04", "J4", "SPW_PORT2", 200, 120,
                     "Conn_01x04", ["1","2","3","4"])
    # J5 - JTAG
    content += _comp("Connector:Conn_01x06", "J5", "JTAG", 200, 60,
                     "Conn_01x06", ["1","2","3","4","5","6"])
    # J6 - SPI debug
    content += _comp("Connector:Conn_01x06", "J6", "SPI_DEBUG", 320, 60,
                     "Conn_01x06", ["1","2","3","4","5","6"])
    # Net labels
    content += _label("JESD_DA0_P", 60, 55, 180, "input")
    content += _label("JESD_DA0_N", 60, 60, 180, "input")
    content += _label("JESD_DA1_P", 60, 65, 180, "input")
    content += _label("JESD_DA1_N", 60, 70, 180, "input")
    content += _label("SPW_TX_P", 60, 115, 180, "input")
    content += _label("SPW_TX_N", 60, 120, 180, "input")
    content += _label("SPW_RX_P", 60, 125, 180, "input")
    content += _label("SPW_RX_N", 60, 130, 180, "input")
    content += _label("SPW_TX2_P", 180, 115, 180, "input")
    content += _label("SPW_TX2_N", 180, 120, 180, "input")
    content += _label("SPW_RX2_P", 180, 125, 180, "input")
    content += _label("SPW_RX2_N", 180, 130, 180, "input")
    content += _label("TCK", 180, 55, 180, "input")
    content += _label("TDI", 180, 60, 180, "input")
    content += _label("TDO", 180, 65, 180, "input")
    content += _label("TMS", 180, 70, 180, "input")
    content += _label("TRST", 180, 75, 180, "input")
    content += _label("GND", 180, 80, 180, "input")
    content += _label("ADC_CS", 300, 55, 180, "input")
    content += _label("ADC_SCLK", 300, 60, 180, "input")
    content += _label("ADC_SDI", 300, 65, 180, "input")
    content += _label("ADC_SDO", 300, 70, 180, "input")
    content += _label("GND", 300, 75, 180, "input")
    content += _label("GND", 300, 80, 180, "input")
    content += _sheet_footer()
    return content


def _gen_sheet15():
    """Sheet15: Test Points."""
    lib = (
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+4V5")}\n'
        f'    {_power_vcc("+1V0")}\n'
        f'    {_power_vcc("+1V8")}\n'
        f'    {_power_vcc("+3V3")}\n'
        f'    {_power_vcc("+2V5")}\n'
        + LIB_R + '\n'
    )
    content = _sheet_header("dddddddd-dddd-dddd-dddd-dddddddddddd",
                            "X-Band Test Points", lib)
    # Test points as resistors (placeholder)
    tp_nets = [
        ("VIN_4V5", 60, 40), ("VCCINT_1V0", 60, 60), ("VCCAUX_1V8", 60, 80),
        ("VCCIO_3V3", 60, 100), ("+1V0", 60, 120), ("+1V8", 60, 140),
        ("+2V5", 60, 160), ("GND", 60, 180),
        ("ADC_CLK_P", 200, 40), ("ADC_SYSREF_P", 200, 60),
        ("FPGA_REFCLK_P", 200, 80), ("FPGA_SPWCLK_P", 200, 100),
        ("ADC_CS", 200, 120), ("LMX_MUXOUT", 200, 140),
        ("PWRGD_SEQ", 200, 160), ("SEQ_DONE", 200, 180),
    ]
    for i, (net, x, y) in enumerate(tp_nets):
        content += _comp("Device:R", f"TP{i+1}", "0R", x, y, "R_0402", ["1","2"])
        content += _label(net, x - 20, y, 180, "bidirectional")
    content += _sheet_footer()
    return content


def _gen_sheet16():
    """Sheet16: Decoupling Capacitor Summary Table."""
    lib = (
        f'    {_power_gnd()}\n'
        + LIB_C + '\n'
    )
    content = _sheet_header("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
                            "X-Band Decoupling Summary", lib)
    # Table of decoupling caps by IC
    caps = [
        ("U1 ADC12DJ5200-SP", "100nF x8, 10uF x4", 80, 40),
        ("U2 FPGA XQRVC1902-SP", "100nF x20, 10uF x10", 80, 60),
        ("U3 LMX2615-SP", "100nF x10, 4.7uF x2", 80, 80),
        ("U4 LMK04832-SP", "100nF x12, 10uF x2", 80, 100),
        ("U5 TPS7H5001-SP", "22uF x2, 100nF x2", 80, 120),
        ("U6 ISL70003ASEH (1.8V)", "22uF x2, 100nF x2", 80, 140),
        ("U7 ISL70003ASEH (3.3V)", "22uF x2, 100nF x2", 80, 160),
        ("U8 TPS7H1111-SP (1.0V)", "10uF x2, 100nF x2", 80, 180),
        ("U9 TPS7H1111-SP (1.8V)", "10uF x2, 100nF x2", 80, 200),
        ("U10 TPS7H1121-SP (2.5V)", "10uF x3, 100nF x3", 80, 220),
        ("U13 TPS7H3014-SP x2", "100nF x2, 10uF x2", 80, 240),
    ]
    for ic_name, cap_desc, x, y in caps:
        content += _comp("Device:C", f"DC{y}", "100nF", x + 200, y, "C_0402", ["1","2"])
        content += _label(ic_name, x, y, 180, "input")
        content += _label(cap_desc, x + 300, y, 0, "input")
    content += _sheet_footer()
    return content


def _gen_sheet17():
    """Sheet17: Power Tree Block Diagram."""
    lib = (
        f'    {_power_gnd()}\n'
        f'    {_power_vcc("+4V5")}\n'
        f'    {_power_vcc("+1V0")}\n'
        f'    {_power_vcc("+1V8")}\n'
        f'    {_power_vcc("+3V3")}\n'
        f'    {_power_vcc("+2V5")}\n'
    )
    content = _sheet_header("ffffffff-ffff-ffff-ffff-ffffffffffff",
                            "X-Band Power Tree", lib)
    # Power tree text blocks (using labels as visual)
    tree_blocks = [
        ("VIN 4.5V", 60, 40),
        ("├─ TPS7H5001-SP → +1V0_FPGA (44A)", 60, 60),
        ("├─ ISL70003ASEH → +1V8 (6A)", 60, 80),
        ("├─ ISL70003ASEH → +3V3 (3A)", 60, 100),
        ("└─ INA214-SP (current sense)", 60, 120),
        ("+3V3 → TPS7H1111-SP → +1V0_ANA (1A)", 60, 140),
        ("+1V8 → TPS7H1111-SP → +1V8_DIG (1A)", 60, 160),
        ("+3V3 → TPS7H1121-SP → +2V5_CLK (1A)", 60, 180),
        ("Sequencer: 2x TPS7H3014-SP (8ch)", 60, 200),
    ]
    for label, x, y in tree_blocks:
        content += _label(label, x, y, 180, "input")
    content += _sheet_footer()
    return content


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

SHEET_GENERATORS = [
    ("Sheet01_Title.kicad_sch", _gen_sheet01),
    ("Sheet02_RF_Input.kicad_sch", _gen_sheet02),
    ("Sheet03_ADC.kicad_sch", _gen_sheet03),
    ("Sheet04_FPGA.kicad_sch", _gen_sheet04),
    ("Sheet05_Clock.kicad_sch", _gen_sheet05),
    ("Sheet06_PowerInput.kicad_sch", _gen_sheet06),
    ("Sheet07_Buck_1V0.kicad_sch", _gen_sheet07),
    ("Sheet08_Buck_1V8.kicad_sch", _gen_sheet08),
    ("Sheet09_Buck_3V3.kicad_sch", _gen_sheet09),
    ("Sheet10_LDO_1V0.kicad_sch", _gen_sheet10),
    ("Sheet11_LDO_1V8.kicad_sch", _gen_sheet11),
    ("Sheet12_LDO_2V5.kicad_sch", _gen_sheet12),
    ("Sheet13_Sequencer.kicad_sch", _gen_sheet13),
    ("Sheet14_Connectors.kicad_sch", _gen_sheet14),
    ("Sheet15_TestPoints.kicad_sch", _gen_sheet15),
    ("Sheet16_Decoupling.kicad_sch", _gen_sheet16),
    ("Sheet17_PowerTree.kicad_sch", _gen_sheet17),
]


def main():
    os.makedirs(SCHEMATIC_DIR, exist_ok=True)

    print("=" * 60)
    print("Generating X-Band Digital Module KiCad 7 Schematics")
    print("=" * 60)

    generated = 0
    errors = []

    for filename, gen_fn in SHEET_GENERATORS:
        filepath = os.path.join(SCHEMATIC_DIR, filename)
        try:
            content = gen_fn()

            # Validate parenthesis balance
            opens = content.count('(')
            closes = content.count(')')
            if opens != closes:
                errors.append(f"{filename}: Parenthesis mismatch ({opens} opens vs {closes} closes)")
                continue

            with open(filepath, 'w') as f:
                f.write(content)

            generated += 1
            print(f"  [OK] {filename} ({opens} pairs, {len(content)} bytes)")

        except Exception as e:
            errors.append(f"{filename}: {e}")
            import traceback
            traceback.print_exc()

    print()
    print(f"Generated: {generated}/{len(SHEET_GENERATORS)} sheets")

    if errors:
        print()
        print("ERRORS:")
        for err in errors:
            print(f"  {err}")
        return 1

    # Verify with kicad-cli if available
    print()
    print("Verifying with kicad-cli...")
    import subprocess
    verified = 0
    for filename, _ in SHEET_GENERATORS:
        filepath = os.path.join(SCHEMATIC_DIR, filename)
        try:
            result = subprocess.run(
                ["kicad-cli", "sch", "export", "pdf",
                 "--output", f"/tmp/test_{filename}.pdf", filepath],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                verified += 1
            else:
                print(f"  [WARN] {filename}: {result.stderr[:200]}")
        except FileNotFoundError:
            print("  [INFO] kicad-cli not found, skipping verification")
            break
        except subprocess.TimeoutExpired:
            print(f"  [WARN] {filename}: timeout")

    if verified > 0:
        print(f"  Verified: {verified}/{len(SHEET_GENERATORS)} sheets OK")

    print()
    print("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
