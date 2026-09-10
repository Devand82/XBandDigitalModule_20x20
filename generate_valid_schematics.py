#!/usr/bin/env python3
"""
Generate valid KiCad .kicad_sch files with proper symbol definitions.
Each symbol is manually defined with correct paren balancing.
"""
import os, uuid

BASE = "/opt/cryptobot/XBandDigitalModule_20x20"
SCH = os.path.join(BASE, "schematic")

def uid():
    return str(uuid.uuid4()).replace('-', '')[:32]

# ===== MINIMAL SYMBOL DEFINITIONS (proven to work) =====
R_SYM = '''    (symbol "Device:R" (pin_numbers hide) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at 0 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at -1.778 0 90) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "R_0_1" (rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "R_1_1" (pin passive line (at 0 3.81 270) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))) (pin passive line (at 0 -3.81 90) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))
    )'''

C_SYM = '''    (symbol "Device:C" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)
      (property "Reference" "C" (at 0.635 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "C" (at 0.635 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0.9652 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "C_0_1" (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none))) (polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none))))
      (symbol "C_1_1" (pin passive line (at 0 3.81 270) (length 2.54) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))) (pin passive line (at 0 -3.81 90) (length 2.54) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))
    )'''

L_SYM = '''    (symbol "Device:L" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
      (property "Reference" "L" (at -0.762 0 90) (effects (font (size 1.27 1.27))))
      (property "Value" "L" (at 1.778 0 90) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "L_0_1" (arc (start 0 -2.54) (mid 1.905 0) (end 0 2.54) (stroke (width 0.381) (type default)) (fill (type none))) (arc (start 0 -1.27) (mid 1.27 0) (end 0 1.27) (stroke (width 0.381) (type default)) (fill (type none))) (arc (start 0 0) (mid 0.635 0.635) (end 0 1.27) (stroke (width 0.381) (type default)) (fill (type none))) (polyline (pts (xy 0 0) (xy 0 -2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 2.54) (xy 0 5.08)) (stroke (width 0) (type default)) (fill (type none))))
      (symbol "L_1_1" (pin passive line (at 0 5.08 270) (length 2.54) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))) (pin passive line (at 0 -5.08 90) (length 2.54) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))
    )'''

FB_SYM = '''    (symbol "Device:FerriteBead" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
      (property "Reference" "FB" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "FerriteBead" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "FerriteBead_0_1" (polyline (pts (xy 0 -2.54) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy -1.016 -2.286) (xy 1.016 -2.286)) (stroke (width 0.508) (type default)) (fill (type none))) (polyline (pts (xy -1.016 -1.524) (xy 1.016 -1.524)) (stroke (width 0.508) (type default)) (fill (type none))) (polyline (pts (xy -1.016 -0.762) (xy 1.016 -0.762)) (stroke (width 0.508) (type default)) (fill (type none))) (polyline (pts (xy -1.016 0) (xy 1.016 0)) (stroke (width 0.508) (type default)) (fill (type none))) (polyline (pts (xy -1.016 0.762) (xy 1.016 0.762)) (stroke (width 0.508) (type default)) (fill (type none))) (polyline (pts (xy -1.016 1.524) (xy 1.016 1.524)) (stroke (width 0.508) (type default)) (fill (type none))) (polyline (pts (xy -1.016 2.286) (xy 1.016 2.286)) (stroke (width 0.508) (type default)) (fill (type none))))
      (symbol "FerriteBead_1_1" (pin passive line (at 0 5.08 270) (length 2.54) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))) (pin passive line (at 0 -5.08 90) (length 2.54) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))
    )'''

CRYSTAL_SYM = '''    (symbol "Device:Crystal" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
      (property "Reference" "Y" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Crystal" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "Crystal_0_1" (polyline (pts (xy -1.524 1.27) (xy -1.524 -1.27)) (stroke (width 0.381) (type default)) (fill (type none))) (polyline (pts (xy 1.524 1.27) (xy 1.524 -1.27)) (stroke (width 0.381) (type default)) (fill (type none))) (polyline (pts (xy -0.508 1.27) (xy -0.508 -1.27)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0.508 1.27) (xy 0.508 -1.27)) (stroke (width 0.254) (type default)) (fill (type none))))
      (symbol "Crystal_1_1" (pin passive line (at 0 5.08 270) (length 3.81) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))) (pin passive line (at 0 -5.08 90) (length 3.81) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))
    )'''

GND_SYM = '''    (symbol "power:GND" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "GND_0_1" (polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type none))))
      (symbol "GND_1_1" (pin power_in line (at 0 0 270) (length 0) (name "GND" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
    )'''

P1V0_SYM = '''    (symbol "power:+1V0" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+1V0" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "+1V0_0_1" (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none))))
      (symbol "+1V0_1_1" (pin power_in line (at 0 0 90) (length 0) (name "+1V0" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
    )'''

P1V8_SYM = '''    (symbol "power:+1V8" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+1V8" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "+1V8_0_1" (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none))))
      (symbol "+1V8_1_1" (pin power_in line (at 0 0 90) (length 0) (name "+1V8" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
    )'''

P3V3_SYM = '''    (symbol "power:+3V3" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+3V3" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "+3V3_0_1" (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none))))
      (symbol "+3V3_1_1" (pin power_in line (at 0 0 90) (length 0) (name "+3V3" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
    )'''

P2V5_SYM = '''    (symbol "power:+2V5" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+2V5" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "+2V5_0_1" (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none))))
      (symbol "+2V5_1_1" (pin power_in line (at 0 0 90) (length 0) (name "+2V5" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
    )'''

P4V5_SYM = '''    (symbol "power:+4V5" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+4V5" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (symbol "+4V5_0_1" (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none))))
      (symbol "+4V5_1_1" (pin power_in line (at 0 0 90) (length 0) (name "+4V5" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
    )'''

# Connector symbols - simple box with pins
def conn_sym(n):
    pins = ""
    for i in range(1, n+1):
        pins += f' (pin passive line (at -5.08 {(n+1-2*i)*1.27:.2f} 0) (length 5.08) (name "Pin{i}" (effects (font (size 1.27 1.27)))) (number "{i}" (effects (font (size 1.27 1.27)))))'
    return f'''    (symbol "Connector_Generic:Conn_01x{n:02d}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 {(n+1)*1.27:.2f} 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Conn_01x{n:02d}" (at 0 -{(n+1)*1.27:.2f} 0) (effects (font (size 1.27 1.27))))
      (symbol "Conn_01x{n:02d}_0_1" (rectangle (start -3.81 {(n+1)*1.27:.2f}) (end 1.27 -{(n+1)*1.27:.2f}) (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "Conn_01x{n:02d}_1_1"{pins})
    )'''

# ===== SHEET GENERATOR =====
def make_sheet(filename, syms_needed, components, wires, glabels, paper="A3"):
    """Generate a complete .kicad_sch file."""
    # Build lib_symbols from needed symbols
    sym_map = {
        'Device:R': R_SYM, 'Device:C': C_SYM, 'Device:L': L_SYM,
        'Device:FerriteBead': FB_SYM, 'Device:Crystal': CRYSTAL_SYM,
        'power:GND': GND_SYM, 'power:+1V0': P1V0_SYM, 'power:+1V8': P1V8_SYM,
        'power:+3V3': P3V3_SYM, 'power:+2V5': P2V5_SYM, 'power:+4V5': P4V5_SYM,
    }
    for n in [2,3,4,6,8]:
        sym_map[f'Connector_Generic:Conn_01x{n:02d}'] = conn_sym(n)

    lib_lines = []
    for sym_key in syms_needed:
        if sym_key in sym_map:
            lib_lines.append(sym_map[sym_key])

    lines = []
    lines.append(f'(kicad_sch (version 20230121) (generator eeschema)')
    lines.append(f'  (uuid "{uid()}")')
    lines.append(f'  (paper "{paper}")')
    lines.append(f'  (title_block')
    lines.append(f'    (title "X-Band Digital Module 20x20cm")')
    lines.append(f'    (date "2026-09-10")')
    lines.append(f'    (rev "1.0")')
    lines.append(f'  )')
    lines.append(f'  (lib_symbols')
    lines.extend(lib_lines)
    lines.append(f'  )')

    # Components
    for ref, val, lib_id, x, y, angle, fp in components:
        lines.append(f'  (symbol (lib_id "{lib_id}") (at {x} {y} {angle}) (unit 1)')
        lines.append(f'    (in_bom yes) (on_board yes)')
        lines.append(f'    (uuid "{uid()}")')
        lines.append(f'    (property "Reference" "{ref}" (at {x} {y-8} 0) (effects (font (size 1.27 1.27))))')
        lines.append(f'    (property "Value" "{val}" (at {x} {y+8} 0) (effects (font (size 1.27 1.27))))')
        if fp:
            lines.append(f'    (property "Footprint" "{fp}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))')
        # Determine pin count and add pin instances
        if 'R' in ref and ref[0] == 'R':
            lines.append(f'    (pin "1" (uuid "{uid()}"))')
            lines.append(f'    (pin "2" (uuid "{uid()}"))')
        elif 'C' in ref and ref[0] == 'C':
            lines.append(f'    (pin "1" (uuid "{uid()}"))')
            lines.append(f'    (pin "2" (uuid "{uid()}"))')
        elif 'L' in ref and ref[0] == 'L':
            lines.append(f'    (pin "1" (uuid "{uid()}"))')
            lines.append(f'    (pin "2" (uuid "{uid()}"))')
        elif 'FB' in ref:
            lines.append(f'    (pin "1" (uuid "{uid()}"))')
            lines.append(f'    (pin "2" (uuid "{uid()}"))')
        elif 'Y' in ref:
            lines.append(f'    (pin "1" (uuid "{uid()}"))')
            lines.append(f'    (pin "2" (uuid "{uid()}"))')
        elif ref.startswith('J'):
            # Count pins from conn_sym
            n = int(lib_id.split('x')[1])
            for p in range(1, n+1):
                lines.append(f'    (pin "{p}" (uuid "{uid()}"))')
        elif ref.startswith('#'):
            lines.append(f'    (pin "1" (uuid "{uid()}"))')
        lines.append(f'  )')

    # Wires
    for x1, y1, x2, y2 in wires:
        lines.append(f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{uid()}"))')

    # Global labels
    for name, x, y, shape, angle in glabels:
        just = "left" if angle == 0 else "right"
        lines.append(f'  (global_label "{name}" (shape {shape}) (at {x} {y} {angle}) (effects (font (size 1.27 1.27)) (justify {just})))')

    lines.append(f'  (sheet_instances (path "/" (page "1")))')
    lines.append(f')')

    path = os.path.join(SCH, filename)
    with open(path, 'w') as f:
        f.write('\n'.join(lines))

    # Verify balanced parens
    depth = 0
    for ch in '\n'.join(lines):
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
    if depth != 0:
        print(f'  WARNING: {filename} unbalanced (depth={depth})')
    else:
        print(f'  OK: {filename} ({len(components)} comp, {len(wires)} wires, {len(glabels)} labels)')


# ===== GENERATE ALL SHEETS =====

print("Generating valid KiCad schematics...")

# Sheet07: Buck 1.0V Core
make_sheet("Sheet07_Buck_1V0.kicad_sch",
    syms_needed=['Device:R', 'Device:C', 'Device:L', 'Device:FerriteBead', 'power:GND', 'power:+4V5', 'power:+1V0'],
    components=[
        ('R6', '100k', 'Device:R', 80, 80, 0, 'Resistor_SMD:R_0402_1005Metric'),
        ('R7', '390k', 'Device:R', 80, 110, 0, 'Resistor_SMD:R_0402_1005Metric'),
        ('R8', '10k', 'Device:R', 80, 140, 0, 'Resistor_SMD:R_0402_1005Metric'),
        ('C27', '22uF', 'Device:C', 60, 60, 0, 'Capacitor_SMD:C_0805_2012Metric'),
        ('C28', '4.7nF', 'Device:C', 100, 80, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C29', '330pF', 'Device:C', 100, 110, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C30', '10nF', 'Device:C', 100, 140, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('L1', '100nH/55A', 'Device:L', 160, 60, 0, 'Inductor_SMD:L_1210_3225Metric'),
        ('C31', '470uF', 'Device:C', 200, 60, 0, 'Capacitor_SMD:CP_EIA-7343-43_P5.00mm'),
        ('C32', '470uF', 'Device:C', 200, 90, 0, 'Capacitor_SMD:CP_EIA-7343-43_P5.00mm'),
        ('C33', '10uF', 'Device:C', 230, 60, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C34', '22uF', 'Device:C', 230, 90, 0, 'Capacitor_SMD:C_0805_2012Metric'),
        ('R9', '5m', 'Device:R', 260, 60, 0, 'Resistor_SMD:R_2512_6332Metric'),
    ],
    wires=[
        (45, 60, 55, 60), (60, 55, 60, 45), (60, 65, 60, 80),
        (100, 75, 100, 60), (100, 85, 100, 100),
        (165, 60, 195, 60), (200, 55, 200, 45), (200, 65, 200, 80),
    ],
    glabels=[
        ('VIN_4V5', 40, 60, 'input', 180),
        ('VCCINT_1V0', 280, 60, 'output', 0),
        ('GND', 60, 45, 'input', 90),
        ('GND', 200, 45, 'input', 90),
        ('BUCK1_EN', 40, 140, 'input', 180),
        ('BUCK1_PG', 165, 80, 'output', 0),
    ])

# Sheet08: Buck 1.8V Aux
make_sheet("Sheet08_Buck_1V8.kicad_sch",
    syms_needed=['Device:R', 'Device:C', 'Device:L', 'power:GND', 'power:+4V5', 'power:+1V8'],
    components=[
        ('R10', '47k', 'Device:R', 80, 80, 0, 'Resistor_SMD:R_0402_1005Metric'),
        ('R11', '22k', 'Device:R', 80, 110, 0, 'Resistor_SMD:R_0402_1005Metric'),
        ('R12', '10k', 'Device:R', 80, 140, 0, 'Resistor_SMD:R_0402_1005Metric'),
        ('C38', '22uF', 'Device:C', 60, 60, 0, 'Capacitor_SMD:C_0805_2012Metric'),
        ('C39', '100nF', 'Device:C', 100, 80, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C40', '4.7nF', 'Device:C', 100, 110, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C41', '10nF', 'Device:C', 100, 140, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('L2', '2.2uH', 'Device:L', 160, 60, 0, 'Inductor_SMD:L_1210_3225Metric'),
        ('C42', '470uF', 'Device:C', 200, 60, 0, 'Capacitor_SMD:CP_EIA-7343-43_P5.00mm'),
        ('C43', '10uF', 'Device:C', 230, 60, 0, 'Capacitor_SMD:C_0603_1608Metric'),
    ],
    wires=[
        (45, 60, 55, 60), (60, 55, 60, 45), (60, 65, 60, 80),
        (100, 75, 100, 60), (100, 85, 100, 100),
        (165, 60, 195, 60),
    ],
    glabels=[
        ('VIN_4V5', 40, 60, 'input', 180),
        ('VDDIO_1V8', 250, 60, 'output', 0),
        ('GND', 60, 45, 'input', 90),
        ('GND', 200, 80, 'input', 90),
        ('BUCK2_EN', 40, 140, 'input', 180),
    ])

# Sheet09: Buck 3.3V I/O
make_sheet("Sheet09_Buck_3V3.kicad_sch",
    syms_needed=['Device:R', 'Device:C', 'Device:L', 'power:GND', 'power:+4V5', 'power:+3V3'],
    components=[
        ('R13', '47k', 'Device:R', 80, 80, 0, 'Resistor_SMD:R_0402_1005Metric'),
        ('R14', '22k', 'Device:R', 80, 110, 0, 'Resistor_SMD:R_0402_1005Metric'),
        ('R15', '10k', 'Device:R', 80, 140, 0, 'Resistor_SMD:R_0402_1005Metric'),
        ('C44', '22uF', 'Device:C', 60, 60, 0, 'Capacitor_SMD:C_0805_2012Metric'),
        ('C45', '100nF', 'Device:C', 100, 80, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C46', '4.7nF', 'Device:C', 100, 110, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C47', '10nF', 'Device:C', 100, 140, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('L3', '4.7uH', 'Device:L', 160, 60, 0, 'Inductor_SMD:L_1210_3225Metric'),
        ('C48', '470uF', 'Device:C', 200, 60, 0, 'Capacitor_SMD:CP_EIA-7343-43_P5.00mm'),
        ('C49', '10uF', 'Device:C', 230, 60, 0, 'Capacitor_SMD:C_0603_1608Metric'),
    ],
    wires=[
        (45, 60, 55, 60), (60, 55, 60, 45), (60, 65, 60, 80),
        (100, 75, 100, 60), (100, 85, 100, 100),
        (165, 60, 195, 60),
    ],
    glabels=[
        ('VIN_4V5', 40, 60, 'input', 180),
        ('VDDIO_3V3', 250, 60, 'output', 0),
        ('GND', 60, 45, 'input', 90),
        ('GND', 200, 80, 'input', 90),
        ('BUCK3_EN', 40, 140, 'input', 180),
    ])

# Sheet10: LDO 1.0V Analog
make_sheet("Sheet10_LDO_1V0.kicad_sch",
    syms_needed=['Device:C', 'power:GND', 'power:+1V8', 'power:+1V0'],
    components=[
        ('C50', '10uF', 'Device:C', 60, 60, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C51', '100nF', 'Device:C', 60, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C52', '1uF', 'Device:C', 60, 120, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C53', '10uF', 'Device:C', 160, 60, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C54', '100nF', 'Device:C', 160, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C55', '1uF', 'Device:C', 160, 120, 0, 'Capacitor_SMD:C_0402_1005Metric'),
    ],
    wires=[
        (60, 55, 60, 45), (60, 65, 60, 80), (60, 95, 60, 110),
        (160, 55, 160, 45), (160, 65, 160, 80), (160, 95, 160, 110),
    ],
    glabels=[
        ('VDDIO_1V8', 50, 45, 'input', 180),
        ('GND', 60, 120, 'input', 90),
        ('VANA_1V0', 170, 45, 'output', 0),
        ('GND', 160, 120, 'input', 90),
    ])

# Sheet11: LDO 1.8V Digital
make_sheet("Sheet11_LDO_1V8.kicad_sch",
    syms_needed=['Device:C', 'power:GND', 'power:+1V8'],
    components=[
        ('C56', '10uF', 'Device:C', 60, 60, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C57', '100nF', 'Device:C', 60, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C58', '10uF', 'Device:C', 160, 60, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C59', '100nF', 'Device:C', 160, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
    ],
    wires=[
        (60, 55, 60, 45), (60, 65, 60, 80), (60, 95, 60, 110),
        (160, 55, 160, 45), (160, 65, 160, 80), (160, 95, 160, 110),
    ],
    glabels=[
        ('VDDIO_1V8', 50, 45, 'input', 180),
        ('GND', 60, 110, 'input', 90),
        ('VDIG_1V8', 170, 45, 'output', 0),
        ('GND', 160, 110, 'input', 90),
    ])

# Sheet12: LDO 2.5V Clock
make_sheet("Sheet12_LDO_2V5.kicad_sch",
    syms_needed=['Device:C', 'power:GND', 'power:+3V3', 'power:+2V5'],
    components=[
        ('C60', '10uF', 'Device:C', 60, 60, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C61', '100nF', 'Device:C', 60, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C62', '1uF', 'Device:C', 60, 120, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C63', '10uF', 'Device:C', 160, 60, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C64', '100nF', 'Device:C', 160, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
    ],
    wires=[
        (60, 55, 60, 45), (60, 65, 60, 80), (60, 95, 60, 110),
        (160, 55, 160, 45), (160, 65, 160, 80), (160, 95, 160, 110),
    ],
    glabels=[
        ('VDDIO_3V3', 50, 45, 'input', 180),
        ('GND', 60, 120, 'input', 90),
        ('VCLK_2V5', 170, 45, 'output', 0),
        ('GND', 160, 110, 'input', 90),
    ])

# Sheet06: Power Input
make_sheet("Sheet06_PowerInput.kicad_sch",
    syms_needed=['Device:C', 'Device:FerriteBead', 'power:GND', 'power:+4V5', 'Connector_Generic:Conn_01x02'],
    components=[
        ('J_PWR', 'POWER_IN', 'Connector_Generic:Conn_01x02', 60, 80, 0, 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical'),
        ('FB_PWR', '600R@100MHz', 'Device:FerriteBead', 100, 80, 0, 'Inductor_SMD:L_0805_2012Metric'),
        ('C_PWR1', '470uF', 'Device:C', 140, 60, 0, 'Capacitor_SMD:CP_EIA-7343-43_P5.00mm'),
        ('C_PWR2', '100nF', 'Device:C', 140, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_PWR3', '10uF', 'Device:C', 170, 60, 0, 'Capacitor_SMD:C_0805_2012Metric'),
    ],
    wires=[
        (65, 75, 95, 75), (105, 75, 135, 75),
        (140, 55, 140, 45), (140, 65, 140, 80),
    ],
    glabels=[
        ('VIN_4V5', 50, 75, 'input', 180),
        ('VIN_4V5', 185, 75, 'output', 0),
        ('GND', 140, 45, 'input', 90),
    ])

# Sheet05: Clock Tree
make_sheet("Sheet05_Clock.kicad_sch",
    syms_needed=['Device:C', 'Device:Crystal', 'Device:FerriteBead', 'power:GND', 'power:+2V5'],
    components=[
        ('Y1', '122.88MHz', 'Device:Crystal', 80, 80, 0, 'Crystal:Crystal_SMD_2012-2Pin_2.0x1.2mm'),
        ('C_CLK1', '100nF', 'Device:C', 120, 80, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_CLK2', '1uF', 'Device:C', 120, 110, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_CLK3', '100nF', 'Device:C', 160, 80, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_CLK4', '10uF', 'Device:C', 160, 110, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('FB_CLK', '600R', 'Device:FerriteBead', 100, 60, 0, 'Inductor_SMD:L_0402_1005Metric'),
    ],
    wires=[
        (80, 75, 80, 60), (80, 85, 80, 100),
        (120, 75, 120, 60), (120, 85, 120, 100),
    ],
    glabels=[
        ('VCLK_2V5', 70, 60, 'input', 180),
        ('GND', 80, 100, 'input', 90),
        ('GND', 120, 110, 'input', 90),
        ('ADC_CLK', 200, 80, 'output', 0),
        ('FPGA_CLK', 200, 110, 'output', 0),
    ])

# Sheet03: ADC
make_sheet("Sheet03_ADC.kicad_sch",
    syms_needed=['Device:C', 'Device:FerriteBead', 'power:GND', 'power:+1V0'],
    components=[
        ('C_A1', '100nF', 'Device:C', 80, 80, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_A2', '10uF', 'Device:C', 100, 80, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C_A3', '100nF', 'Device:C', 120, 80, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_A4', '1uF', 'Device:C', 140, 80, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('FB_ADC', '600R', 'Device:FerriteBead', 100, 60, 0, 'Inductor_SMD:L_0402_1005Metric'),
    ],
    wires=[
        (80, 75, 80, 60), (80, 85, 80, 100),
        (100, 75, 100, 60), (100, 85, 100, 100),
        (120, 75, 120, 60), (120, 85, 120, 100),
        (140, 75, 140, 60), (140, 85, 140, 100),
    ],
    glabels=[
        ('VANA_1V0', 70, 60, 'input', 180),
        ('GND', 100, 100, 'input', 90),
        ('ADC_D0', 200, 80, 'output', 0),
        ('JESD_SYNC', 200, 110, 'output', 0),
    ])

# Sheet04: FPGA
make_sheet("Sheet04_FPGA.kicad_sch",
    syms_needed=['Device:C', 'power:GND', 'power:+1V0', 'power:+1V8', 'power:+3V3'],
    components=[
        ('C_F1', '100nF', 'Device:C', 60, 60, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_F2', '100nF', 'Device:C', 75, 60, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_F3', '100nF', 'Device:C', 90, 60, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_F4', '100nF', 'Device:C', 105, 60, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_F5', '10uF', 'Device:C', 60, 90, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C_F6', '10uF', 'Device:C', 75, 90, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C_F7', '4.7uF', 'Device:C', 90, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_F8', '4.7uF', 'Device:C', 105, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_F9', '100nF', 'Device:C', 130, 60, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_F10', '100nF', 'Device:C', 145, 60, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_F11', '10uF', 'Device:C', 130, 90, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C_F12', '10uF', 'Device:C', 145, 90, 0, 'Capacitor_SMD:C_0603_1608Metric'),
    ],
    wires=[
        (60, 55, 60, 45), (60, 65, 60, 80),
        (75, 55, 75, 45), (75, 65, 75, 80),
        (90, 55, 90, 45), (90, 65, 90, 80),
        (105, 55, 105, 45), (105, 65, 105, 80),
    ],
    glabels=[
        ('VCCINT_1V0', 50, 45, 'input', 180),
        ('GND', 80, 100, 'input', 90),
        ('JESD_D0', 200, 60, 'bidirectional', 0),
        ('JESD_D1', 200, 75, 'bidirectional', 0),
        ('SPW_TX0', 200, 90, 'output', 0),
        ('FPGA_CLK', 200, 105, 'input', 0),
    ])

# Sheet13: Sequencer
make_sheet("Sheet13_Sequencer.kicad_sch",
    syms_needed=['Device:R', 'Device:C', 'power:GND', 'power:+4V5'],
    components=[
        ('R16', '10k', 'Device:R', 60, 60, 0, 'Resistor_SMD:R_0402_1005Metric'),
        ('R17', '10k', 'Device:R', 60, 90, 0, 'Resistor_SMD:R_0402_1005Metric'),
        ('C65', '100nF', 'Device:C', 60, 120, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C66', '1uF', 'Device:C', 60, 150, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C67', '10nF', 'Device:C', 90, 120, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('R18', '47k', 'Device:R', 120, 60, 0, 'Resistor_SMD:R_0402_1005Metric'),
    ],
    wires=[
        (60, 55, 60, 45), (60, 65, 60, 80), (60, 95, 60, 110), (60, 125, 60, 140),
    ],
    glabels=[
        ('VIN_4V5', 50, 45, 'input', 180),
        ('GND', 60, 150, 'input', 90),
        ('SEQ_EN', 40, 120, 'input', 180),
        ('SEQ_OUT_A', 150, 60, 'output', 0),
        ('SEQ_OUT_B', 150, 90, 'output', 0),
    ])

# Sheet14: Connectors
make_sheet("Sheet14_Connectors.kicad_sch",
    syms_needed=['Connector_Generic:Conn_01x02', 'Connector_Generic:Conn_01x04', 'Connector_Generic:Conn_01x06', 'power:GND', 'power:+4V5'],
    components=[
        ('J1', 'JTAG', 'Connector_Generic:Conn_01x06', 60, 80, 0, 'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical'),
        ('J2', 'SPW_TX', 'Connector_Generic:Conn_01x04', 140, 80, 0, 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical'),
        ('J3', 'SPW_RX', 'Connector_Generic:Conn_01x04', 220, 80, 0, 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical'),
        ('J4', 'POWER', 'Connector_Generic:Conn_01x02', 60, 140, 0, 'TerminalBlock:TerminalBlock_bornier-2_P5.08mm'),
        ('J5', 'UART', 'Connector_Generic:Conn_01x04', 140, 140, 0, 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical'),
    ],
    wires=[],
    glabels=[
        ('TCK', 45, 75, 'input', 180), ('TMS', 45, 80, 'input', 180),
        ('TDI', 45, 85, 'input', 180), ('TDO', 45, 90, 'input', 180),
        ('SPW_TX0+', 125, 75, 'output', 180), ('SPW_TX0-', 125, 80, 'output', 180),
        ('SPW_TX1+', 205, 75, 'output', 180), ('SPW_TX1-', 205, 80, 'output', 180),
        ('VIN_4V5', 45, 135, 'input', 180), ('GND', 45, 145, 'input', 180),
        ('UART_TX', 125, 135, 'output', 180), ('UART_RX', 125, 140, 'output', 180),
    ])

# Sheet15: Test Points
make_sheet("Sheet15_TestPoints.kicad_sch",
    syms_needed=['Device:C'],
    components=[
        ('TP1', 'VCCINT_1V0', 'Device:C', 60, 60, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP2', 'VDDIO_1V8', 'Device:C', 60, 80, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP3', 'VDDIO_3V3', 'Device:C', 60, 100, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP4', 'VANA_1V0', 'Device:C', 60, 120, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP5', 'VDIG_1V8', 'Device:C', 60, 140, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP6', 'VCLK_2V5', 'Device:C', 60, 160, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP7', 'VIN_4V5', 'Device:C', 60, 180, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP8', 'BUCK1_PG', 'Device:C', 140, 60, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP9', 'BUCK2_PG', 'Device:C', 140, 80, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP10', 'BUCK3_PG', 'Device:C', 140, 100, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP11', 'SEQ_OUT_A', 'Device:C', 140, 120, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP12', 'SEQ_OUT_B', 'Device:C', 140, 140, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP13', 'SPW_TX0+', 'Device:C', 220, 60, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP14', 'SPW_TX0-', 'Device:C', 220, 80, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP15', 'SPW_TX1+', 'Device:C', 220, 100, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP16', 'SPW_TX1-', 'Device:C', 220, 120, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP17', 'JESD_SYNC', 'Device:C', 220, 140, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
        ('TP18', 'FPGA_CLK', 'Device:C', 220, 160, 0, 'TestPoint:TestPoint_Pad_1.5x1.5mm'),
    ],
    wires=[],
    glabels=[
        ('VCCINT_1V0', 50, 60, 'bidirectional', 180),
        ('VDDIO_1V8', 50, 80, 'bidirectional', 180),
        ('VDDIO_3V3', 50, 100, 'bidirectional', 180),
        ('VANA_1V0', 50, 120, 'bidirectional', 180),
        ('VDIG_1V8', 50, 140, 'bidirectional', 180),
        ('VCLK_2V5', 50, 160, 'bidirectional', 180),
        ('VIN_4V5', 50, 180, 'bidirectional', 180),
        ('BUCK1_PG', 130, 60, 'bidirectional', 180),
        ('BUCK2_PG', 130, 80, 'bidirectional', 180),
        ('BUCK3_PG', 130, 100, 'bidirectional', 180),
        ('SEQ_OUT_A', 130, 120, 'bidirectional', 180),
        ('SEQ_OUT_B', 130, 140, 'bidirectional', 180),
        ('SPW_TX0+', 210, 60, 'bidirectional', 180),
        ('SPW_TX0-', 210, 80, 'bidirectional', 180),
        ('SPW_TX1+', 210, 100, 'bidirectional', 180),
        ('SPW_TX1-', 210, 120, 'bidirectional', 180),
        ('JESD_SYNC', 210, 140, 'bidirectional', 180),
        ('FPGA_CLK', 210, 160, 'bidirectional', 180),
    ])

# Sheet16: Decoupling
make_sheet("Sheet16_Decoupling.kicad_sch",
    syms_needed=['Device:C'],
    components=[
        ('C_D1', '100nF', 'Device:C', 60, 60, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_D2', '10uF', 'Device:C', 75, 60, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C_D3', '4.7uF', 'Device:C', 90, 60, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_D4', '100nF', 'Device:C', 60, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_D5', '10uF', 'Device:C', 75, 90, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C_D6', '1uF', 'Device:C', 90, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_D7', '100nF', 'Device:C', 60, 120, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_D8', '10uF', 'Device:C', 75, 120, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C_D9', '100nF', 'Device:C', 150, 60, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_D10', '10uF', 'Device:C', 165, 60, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C_D11', '100nF', 'Device:C', 150, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_D12', '10uF', 'Device:C', 165, 90, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C_D13', '100nF', 'Device:C', 150, 120, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_D14', '1uF', 'Device:C', 165, 120, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_D15', '100nF', 'Device:C', 240, 60, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_D16', '10uF', 'Device:C', 255, 60, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C_D17', '100nF', 'Device:C', 240, 90, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_D18', '10uF', 'Device:C', 255, 90, 0, 'Capacitor_SMD:C_0603_1608Metric'),
        ('C_D19', '100nF', 'Device:C', 240, 120, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('C_D20', '1uF', 'Device:C', 255, 120, 0, 'Capacitor_SMD:C_0402_1005Metric'),
    ],
    wires=[],
    glabels=[])

# Sheet17: Power Tree
make_sheet("Sheet17_PowerTree.kicad_sch",
    syms_needed=['Device:R', 'Device:L', 'power:GND'],
    components=[
        ('PT1', 'VIN 4.5V', 'Device:R', 40, 80, 0, ''),
        ('PT2', 'TPS7H5002', 'Device:R', 120, 60, 0, ''),
        ('PT3', 'ISL70003A x2', 'Device:R', 120, 100, 0, ''),
        ('PT4', 'TPS7H1111 x2', 'Device:R', 200, 60, 0, ''),
        ('PT5', 'TPS7H1121', 'Device:R', 200, 100, 0, ''),
        ('PT6', 'VCCINT 1.0V', 'Device:R', 300, 60, 0, ''),
        ('PT7', 'VDDIO 1.8V', 'Device:R', 300, 80, 0, ''),
        ('PT8', 'VDDIO 3.3V', 'Device:R', 300, 100, 0, ''),
        ('PT9', 'VANA 1.0V', 'Device:R', 300, 120, 0, ''),
        ('PT10', 'VDIG 1.8V', 'Device:R', 300, 140, 0, ''),
        ('PT11', 'VCLK 2.5V', 'Device:R', 300, 160, 0, ''),
    ],
    wires=[
        (55, 80, 115, 60), (55, 80, 115, 100),
        (135, 60, 195, 60), (135, 100, 195, 100),
        (215, 60, 295, 60), (215, 60, 295, 80),
        (215, 100, 295, 100), (215, 100, 295, 120),
        (215, 100, 295, 140), (215, 100, 295, 160),
    ],
    glabels=[])

# Sheet01: Title (minimal)
make_sheet("Sheet01_Title.kicad_sch",
    syms_needed=[],
    components=[],
    wires=[],
    glabels=[])

# Sheet02: RF Input
make_sheet("Sheet02_RF_Input.kicad_sch",
    syms_needed=['Device:R', 'Device:C', 'Device:L', 'power:GND'],
    components=[
        ('R1', '50', 'Device:R', 80, 80, 0, 'Resistor_SMD:R_0402_1005Metric'),
        ('C1', '100pF', 'Device:C', 120, 80, 0, 'Capacitor_SMD:C_0402_1005Metric'),
        ('L1', '100nH', 'Device:L', 160, 80, 0, 'Inductor_SMD:L_0402_1005Metric'),
        ('C2', '10pF', 'Device:C', 160, 110, 0, 'Capacitor_SMD:C_0402_1005Metric'),
    ],
    wires=[
        (65, 80, 75, 80), (85, 80, 115, 80),
        (125, 80, 155, 80), (160, 85, 160, 105),
    ],
    glabels=[
        ('RF_IN', 55, 80, 'input', 180),
        ('ADC_RF', 175, 80, 'output', 0),
        ('GND', 160, 120, 'input', 90),
    ])

print("\nDone! All 17 sheets generated.")
