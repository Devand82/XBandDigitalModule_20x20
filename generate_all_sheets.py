#!/usr/bin/env python3
"""Regenerate ALL schematic sheets with proper wiring, component placement, and labels."""
import os, re, uuid

BASE = "/opt/cryptobot/XBandDigitalModule_20x20"
SCH = os.path.join(BASE, "schematic")

def uid():
    return str(uuid.uuid4()).replace('-', '')[:32]

def wire(x1, y1, x2, y2):
    return f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0.1524) (type solid)) (uuid "{uid()}"))\n'

def label(name, x, y, angle=0):
    return f'  (label "{name}" (at {x} {y} {angle}) (effects (font (size 1.27 1.27)) (justify left)))\n'

def glabel(name, x, y, shape="bidirectional", angle=0):
    just = "right" if angle == 0 else "left"
    return f'  (global_label "{name}" (shape {shape}) (at {x} {y} {angle}) (effects (font (size 1.27 1.27)) (justify {just})))\n'

def power_flag(x, y):
    return f'  (power_port "+1.0V" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left)))\n'

def no_connect(x, y):
    return f'  (no_connect (at {x} {y}) (uuid "{uid()}"))\n'

def make_sheet(filename, components, wires_list, labels_list, glabels_list, title, comment1, comment2=""):
    """Build a complete .kicad_sch file."""
    lines = []
    lines.append(f'(kicad_sch (version 20230121) (generator eeschema)')
    lines.append(f'  (uuid "{uid()}")')
    lines.append(f'  (paper "A3")')
    lines.append(f'  (title_block')
    lines.append(f'    (title "X-Band Digital Module 20x20cm")')
    lines.append(f'    (date "2026-09-10")')
    lines.append(f'    (rev "1.0")')
    lines.append(f'    (comment 1 "{comment1}")')
    if comment2:
        lines.append(f'    (comment 2 "{comment2}")')
    lines.append(f'  )')
    lines.append(f'  (lib_symbols')
    # Library symbols used
    lines.append(f'    (symbol "X-Band:Resistor" (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "R" (at 2.032 0 90) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "R" (at 0 0 90) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (symbol "Resistor_0_1" (rectangle (start -1.016 2.54) (end 1.016 -2.54) (stroke (width 0.254) (type default)) (fill (type background))))')
    lines.append(f'      (symbol "Resistor_1_1" (pin passive line (at 0 5.08 270) (length 2.54) (name "1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))')
    lines.append(f'      (symbol "Resistor_2_1" (pin passive line (at 0 -5.08 90) (length 2.54) (name "2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))')
    lines.append(f'    )')
    lines.append(f'    (symbol "X-Band:Capacitor" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "C" (at 1.016 2.54 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "C" (at 0 0 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (symbol "Capacitor_0_1" (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none))))')
    lines.append(f'      (symbol "Capacitor_0_2" (polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none))))')
    lines.append(f'      (symbol "Capacitor_1_1" (pin passive line (at 0 3.81 270) (length 3.048) (name "1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))')
    lines.append(f'      (symbol "Capacitor_2_1" (pin passive line (at 0 -3.81 90) (length 3.048) (name "2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))')
    lines.append(f'    )')
    lines.append(f'    (symbol "X-Band:Inductor" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)')
    lines.append(f'      (property "Reference" "L" (at -1.016 3.81 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (property "Value" "L" (at 0 0 0) (effects (font (size 1.27 1.27))))')
    lines.append(f'      (symbol "Inductor_1_1" (pin passive line (at 0 5.08 270) (length 2.54) (name "1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))')
    lines.append(f'      (symbol "Inductor_2_1" (pin passive line (at 0 -5.08 90) (length 2.54) (name "2" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27))))))')
    lines.append(f'    )')
    lines.append(f'  )')

    # Components
    for c in components:
        lib = c['lib']
        ref = c['ref']
        val = c['val']
        x, y, angle = c['x'], c['y'], c.get('angle', 0)
        fp = c.get('fp', 'Resistor_SMD:R_0402_1005Metric')
        lines.append(f'  (symbol (lib_id "X-Band:{lib}" (at {x} {y} {angle}) (unit 1)')
        lines.append(f'    (in_bom yes) (on_board yes)')
        lines.append(f'    (uuid "{uid()}")')
        lines.append(f'    (property "Reference" "{ref}" (at {x} {y-10} 0) (effects (font (size 1.27 1.27))))')
        lines.append(f'    (property "Value" "{val}" (at {x} {y+10} 0) (effects (font (size 1.27 1.27))))')
        lines.append(f'    (property "Footprint" "{fp}" (at {x} {y} 0) (effects (font (size 1.27 1.27))))')
        lines.append(f'  )')

    # Wires
    for w in wires_list:
        lines.append(wire(*w))

    # Labels
    for l in labels_list:
        lines.append(label(*l))

    # Global labels
    for gl in glabels_list:
        lines.append(glabel(*gl))

    lines.append(f'  (sheet_instances (path "/" (page "1")))')
    lines.append(f')')

    with open(os.path.join(SCH, filename), 'w') as f:
        f.write('\n'.join(lines))
    print(f'  Written: {filename} ({len(components)} comp, {len(wires_list)} wires, {len(labels_list)+len(glabels_list)} labels)')


# ===== Sheet07: Buck 1.0V Core (TPS7H5002-SP) =====
def gen_sheet07():
    comp = [
        {'lib': 'TPS7H5002-SP', 'ref': 'U6', 'val': 'TPS7H5002-SP', 'x': 100, 'y': 80, 'fp': 'Package_DFN_QFN:QFN-56_8x8mm_P0.5mm'},
        {'lib': 'Inductor', 'ref': 'L1', 'val': '100nH/55A', 'x': 145, 'y': 60, 'fp': 'Inductor_SMD:L_1210_3225Metric'},
        {'lib': 'Capacitor', 'ref': 'C27', 'val': '4.7nF', 'x': 55, 'y': 100, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C28', 'val': '330pF', 'x': 55, 'y': 115, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R6', 'val': '100k', 'x': 55, 'y': 85, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R7', 'val': '390k', 'x': 55, 'y': 130, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R8', 'val': '10k', 'x': 55, 'y': 145, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C29', 'val': '10nF', 'x': 70, 'y': 145, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C30', 'val': '3.3nF', 'x': 85, 'y': 145, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C31', 'val': '22uF', 'x': 165, 'y': 60, 'angle': 90, 'fp': 'Capacitor_SMD:C_0805_2012Metric'},
        {'lib': 'Capacitor', 'ref': 'C32', 'val': '22uF', 'x': 175, 'y': 60, 'angle': 90, 'fp': 'Capacitor_SMD:C_0805_2012Metric'},
        {'lib': 'Capacitor', 'ref': 'C33', 'val': '470uF', 'x': 155, 'y': 80, 'angle': 90, 'fp': 'Capacitor_SMD:CP_EIA-7343-43_P5.00mm'},
        {'lib': 'Capacitor', 'ref': 'C34', 'val': '470uF', 'x': 165, 'y': 80, 'angle': 90, 'fp': 'Capacitor_SMD:CP_EIA-7343-43_P5.00mm'},
        {'lib': 'Capacitor', 'ref': 'C35', 'val': '10uF', 'x': 175, 'y': 80, 'angle': 90, 'fp': 'Capacitor_SMD:C_0603_1608Metric'},
        {'lib': 'Resistor', 'ref': 'R9', 'val': '10k', 'x': 195, 'y': 60, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R10', 'val': '15.8k', 'x': 210, 'y': 60, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R11', 'val': '5m', 'x': 225, 'y': 60, 'fp': 'Resistor_SMD:R_2512_6332Metric'},
        {'lib': 'Capacitor', 'ref': 'C36', 'val': '100nF', 'x': 70, 'y': 100, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C37', 'val': '100nF', 'x': 85, 'y': 100, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
    ]
    # Wire list: (x1,y1, x2,y2) connecting component pins
    wires = [
        # VIN to IC VIN (pin 1)
        (70, 80, 87, 80),
        # IC EN (pin 2) to R6
        (70, 85, 55, 85),
        # IC FB (pin 4) to divider R6/R7
        (70, 90, 55, 100),
        # IC CSS (pin 5) to R8
        (70, 95, 55, 145),
        # IC RCOMP (pin 6) to RCOMP network
        (70, 100, 85, 145),
        # IC SW (pin 7) to L1
        (113, 80, 145, 60),
        # L1 to VOUT
        (145, 55, 165, 55),
        # Output caps to GND
        (155, 75, 155, 100),
        (165, 75, 165, 100),
        (175, 75, 175, 100),
        # Feedback divider
        (195, 55, 195, 70),
        (210, 55, 210, 70),
        (225, 55, 225, 70),
        # GND connections
        (87, 95, 87, 100),
        (100, 95, 100, 100),
    ]
    labels_list = [
        ('VIN_4V5', 65, 80, 0),
    ]
    glabels = [
        ('VCCINT_1V0', 165, 55, 'output', 0),
        ('GND', 87, 100, 'input', 90),
        ('GND', 155, 100, 'input', 90),
        ('BUCK1_EN', 45, 85, 'input', 180),
        ('BUCK1_PG', 125, 80, 'output', 0),
    ]
    make_sheet('Sheet07_Buck_1V0.kicad_sch', comp, wires, labels_list, glabels,
               'Buck 1.0V Core Rail', 'Sheet 7: TPS7H5002-SP, 44A Output, 100nH Inductor',
               'VCCINT_1V0 Rail for FPGA Core')


# ===== Sheet08: Buck 1.8V Aux (ISL70003ASEH) =====
def gen_sheet08():
    comp = [
        {'lib': 'Inductor', 'ref': 'U7', 'val': 'ISL70003ASEH', 'x': 100, 'y': 80, 'fp': 'Package_DFN_QFN:QFN-40_6x6mm_P0.5mm'},
        {'lib': 'Inductor', 'ref': 'L2', 'val': '2.2uH', 'x': 145, 'y': 60, 'fp': 'Inductor_SMD:L_1210_3225Metric'},
        {'lib': 'Capacitor', 'ref': 'C38', 'val': '22uF', 'x': 165, 'y': 60, 'angle': 90, 'fp': 'Capacitor_SMD:C_0805_2012Metric'},
        {'lib': 'Capacitor', 'ref': 'C39', 'val': '22uF', 'x': 175, 'y': 60, 'angle': 90, 'fp': 'Capacitor_SMD:C_0805_2012Metric'},
        {'lib': 'Capacitor', 'ref': 'C40', 'val': '10uF', 'x': 185, 'y': 60, 'angle': 90, 'fp': 'Capacitor_SMD:C_0603_1608Metric'},
        {'lib': 'Capacitor', 'ref': 'C41', 'val': '100nF', 'x': 55, 'y': 100, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C42', 'val': '100nF', 'x': 70, 'y': 100, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R12', 'val': '47k', 'x': 55, 'y': 85, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R13', 'val': '22k', 'x': 55, 'y': 115, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C43', 'val': '4.7nF', 'x': 85, 'y': 115, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R14', 'val': '10k', 'x': 55, 'y': 130, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C44', 'val': '10nF', 'x': 70, 'y': 130, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R15', 'val': '5m', 'x': 225, 'y': 60, 'fp': 'Resistor_SMD:R_2512_6332Metric'},
        {'lib': 'Capacitor', 'ref': 'C45', 'val': '470uF', 'x': 155, 'y': 80, 'angle': 90, 'fp': 'Capacitor_SMD:CP_EIA-7343-43_P5.00mm'},
        {'lib': 'Capacitor', 'ref': 'C46', 'val': '470uF', 'x': 165, 'y': 80, 'angle': 90, 'fp': 'Capacitor_SMD:CP_EIA-7343-43_P5.00mm'},
        {'lib': 'Resistor', 'ref': 'R16', 'val': '10k', 'x': 195, 'y': 60, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R17', 'val': '15.8k', 'x': 210, 'y': 60, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
    ]
    wires = [
        (70, 80, 87, 80),
        (113, 80, 145, 60),
        (145, 55, 165, 55),
        (70, 85, 55, 85),
        (70, 90, 55, 100),
        (70, 95, 55, 130),
        (155, 75, 155, 100),
        (165, 75, 165, 100),
    ]
    labels_list = [('VIN_4V5', 65, 80, 0)]
    glabels = [
        ('VDDIO_1V8', 165, 55, 'output', 0),
        ('GND', 87, 100, 'input', 90),
        ('GND', 155, 100, 'input', 90),
        ('BUCK2_EN', 45, 85, 'input', 180),
        ('BUCK2_PG', 125, 80, 'output', 0),
    ]
    make_sheet('Sheet08_Buck_1V8.kicad_sch', comp, wires, labels_list, glabels,
               'Buck 1.8V Auxiliary Rail', 'Sheet 8: ISL70003ASEH, 6A Output, 2.2uH Inductor',
               'VDDIO_1V8 Rail')


# ===== Sheet09: Buck 3.3V I/O (ISL70003ASEH) =====
def gen_sheet09():
    comp = [
        {'lib': 'Inductor', 'ref': 'U8', 'val': 'ISL70003ASEH', 'x': 100, 'y': 80, 'fp': 'Package_DFN_QFN:QFN-40_6x6mm_P0.5mm'},
        {'lib': 'Inductor', 'ref': 'L3', 'val': '4.7uH', 'x': 145, 'y': 60, 'fp': 'Inductor_SMD:L_1210_3225Metric'},
        {'lib': 'Capacitor', 'ref': 'C47', 'val': '22uF', 'x': 165, 'y': 60, 'angle': 90, 'fp': 'Capacitor_SMD:C_0805_2012Metric'},
        {'lib': 'Capacitor', 'ref': 'C48', 'val': '22uF', 'x': 175, 'y': 60, 'angle': 90, 'fp': 'Capacitor_SMD:C_0805_2012Metric'},
        {'lib': 'Capacitor', 'ref': 'C49', 'val': '10uF', 'x': 185, 'y': 60, 'angle': 90, 'fp': 'Capacitor_SMD:C_0603_1608Metric'},
        {'lib': 'Capacitor', 'ref': 'C50', 'val': '100nF', 'x': 55, 'y': 100, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C51', 'val': '100nF', 'x': 70, 'y': 100, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R18', 'val': '47k', 'x': 55, 'y': 85, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R19', 'val': '22k', 'x': 55, 'y': 115, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C52', 'val': '4.7nF', 'x': 85, 'y': 115, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R20', 'val': '10k', 'x': 55, 'y': 130, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C53', 'val': '10nF', 'x': 70, 'y': 130, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R21', 'val': '5m', 'x': 225, 'y': 60, 'fp': 'Resistor_SMD:R_2512_6332Metric'},
        {'lib': 'Capacitor', 'ref': 'C54', 'val': '470uF', 'x': 155, 'y': 80, 'angle': 90, 'fp': 'Capacitor_SMD:CP_EIA-7343-43_P5.00mm'},
        {'lib': 'Capacitor', 'ref': 'C55', 'val': '470uF', 'x': 165, 'y': 80, 'angle': 90, 'fp': 'Capacitor_SMD:CP_EIA-7343-43_P5.00mm'},
    ]
    wires = [
        (70, 80, 87, 80), (113, 80, 145, 60), (145, 55, 165, 55),
        (70, 85, 55, 85), (70, 90, 55, 100), (70, 95, 55, 130),
        (155, 75, 155, 100), (165, 75, 165, 100),
    ]
    labels_list = [('VIN_4V5', 65, 80, 0)]
    glabels = [
        ('VDDIO_3V3', 165, 55, 'output', 0),
        ('GND', 87, 100, 'input', 90), ('GND', 155, 100, 'input', 90),
        ('BUCK3_EN', 45, 85, 'input', 180), ('BUCK3_PG', 125, 80, 'output', 0),
    ]
    make_sheet('Sheet09_Buck_3V3.kicad_sch', comp, wires, labels_list, glabels,
               'Buck 3.3V I/O Rail', 'Sheet 9: ISL70003ASEH, 3A Output, 4.7uH Inductor', 'VDDIO_3V3 Rail')


# ===== Sheet10: LDO 1.0V Analog (TPS7H1111-SP) =====
def gen_sheet10():
    comp = [
        {'lib': 'Inductor', 'ref': 'U9', 'val': 'TPS7H1111-SP', 'x': 100, 'y': 80, 'fp': 'Package_TO_SOT_SMD:SOT-23-5'},
        {'lib': 'Capacitor', 'ref': 'C56', 'val': '10uF', 'x': 55, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0603_1608Metric'},
        {'lib': 'Capacitor', 'ref': 'C57', 'val': '10uF', 'x': 155, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0603_1608Metric'},
        {'lib': 'Capacitor', 'ref': 'C58', 'val': '100nF', 'x': 70, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C59', 'val': '100nF', 'x': 170, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C60', 'val': '1uF', 'x': 85, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C61', 'val': '1uF', 'x': 185, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
    ]
    wires = [
        (85, 80, 85, 100), (115, 80, 155, 80), (155, 80, 155, 100),
        (85, 85, 55, 85), (115, 85, 155, 85), (115, 75, 155, 75),
    ]
    labels_list = [('VDDIO_1V8', 60, 80, 0)]
    glabels = [
        ('VANA_1V0', 155, 75, 'output', 0),
        ('GND', 85, 100, 'input', 90), ('GND', 155, 100, 'input', 90),
    ]
    make_sheet('Sheet10_LDO_1V0.kicad_sch', comp, wires, labels_list, glabels,
               'LDO 1.0V Analog Rail', 'Sheet 10: TPS7H1111-SP, 1A, Low Noise for ADC AVDD', 'VANA_1V0 Rail')


# ===== Sheet11: LDO 1.8V Digital (TPS7H1111-SP) =====
def gen_sheet11():
    comp = [
        {'lib': 'Inductor', 'ref': 'U10', 'val': 'TPS7H1111-SP', 'x': 100, 'y': 80, 'fp': 'Package_TO_SOT_SMD:SOT-23-5'},
        {'lib': 'Capacitor', 'ref': 'C62', 'val': '10uF', 'x': 55, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0603_1608Metric'},
        {'lib': 'Capacitor', 'ref': 'C63', 'val': '10uF', 'x': 155, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0603_1608Metric'},
        {'lib': 'Capacitor', 'ref': 'C64', 'val': '100nF', 'x': 70, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C65', 'val': '100nF', 'x': 170, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
    ]
    wires = [
        (85, 80, 85, 100), (115, 80, 155, 80), (155, 80, 155, 100),
        (85, 85, 55, 85), (115, 85, 155, 85),
    ]
    labels_list = [('VDDIO_1V8', 60, 80, 0)]
    glabels = [
        ('VDIG_1V8', 155, 75, 'output', 0),
        ('GND', 85, 100, 'input', 90), ('GND', 155, 100, 'input', 90),
    ]
    make_sheet('Sheet11_LDO_1V8.kicad_sch', comp, wires, labels_list, glabels,
               'LDO 1.8V Digital Rail', 'Sheet 11: TPS7H1111-SP, 1A, Digital DVDD', 'VDIG_1V8 Rail')


# ===== Sheet12: LDO 2.5V Clock (TPS7H1121-SP) =====
def gen_sheet12():
    comp = [
        {'lib': 'Inductor', 'ref': 'U11', 'val': 'TPS7H1121-SP', 'x': 100, 'y': 80, 'fp': 'Package_TO_SOT_SMD:SOT-23-5'},
        {'lib': 'Capacitor', 'ref': 'C66', 'val': '10uF', 'x': 55, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0603_1608Metric'},
        {'lib': 'Capacitor', 'ref': 'C67', 'val': '10uF', 'x': 155, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0603_1608Metric'},
        {'lib': 'Capacitor', 'ref': 'C68', 'val': '100nF', 'x': 70, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C69', 'val': '100nF', 'x': 170, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C70', 'val': '1uF', 'x': 85, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C71', 'val': '1uF', 'x': 185, 'y': 100, 'angle': 90, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
    ]
    wires = [
        (85, 80, 85, 100), (115, 80, 155, 80), (155, 80, 155, 100),
        (85, 85, 55, 85), (115, 85, 155, 85), (115, 75, 155, 75),
    ]
    labels_list = [('VDDIO_3V3', 60, 80, 0)]
    glabels = [
        ('VCLK_2V5', 155, 75, 'output', 0),
        ('GND', 85, 100, 'input', 90), ('GND', 155, 100, 'input', 90),
    ]
    make_sheet('Sheet12_LDO_2V5.kicad_sch', comp, wires, labels_list, glabels,
               'LDO 2.5V Clock Rail', 'Sheet 12: TPS7H1121-SP, 300mA, Ultra Low Noise for Clock', 'VCLK_2V5 Rail')


# ===== Sheet13: Sequencer (2x TPS7H3014-SP) =====
def gen_sheet13():
    comp = [
        {'lib': 'Inductor', 'ref': 'U12', 'val': 'TPS7H3014-SP-A', 'x': 80, 'y': 70, 'fp': 'Package_TO_SOT_SMD:SOT-23-6'},
        {'lib': 'Inductor', 'ref': 'U13', 'val': 'TPS7H3014-SP-B', 'x': 170, 'y': 70, 'fp': 'Package_TO_SOT_SMD:SOT-23-6'},
        {'lib': 'Resistor', 'ref': 'R22', 'val': '10k', 'x': 55, 'y': 60, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R23', 'val': '10k', 'x': 55, 'y': 80, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R24', 'val': '100k', 'x': 55, 'y': 100, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R25', 'val': '10k', 'x': 200, 'y': 60, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R26', 'val': '10k', 'x': 200, 'y': 80, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C72', 'val': '100nF', 'x': 55, 'y': 120, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C73', 'val': '100nF', 'x': 200, 'y': 100, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C74', 'val': '1uF', 'x': 70, 'y': 120, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C75', 'val': '1uF', 'x': 215, 'y': 100, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Capacitor', 'ref': 'C76', 'val': '10nF', 'x': 85, 'y': 120, 'fp': 'Capacitor_SMD:C_0402_1005Metric'},
        {'lib': 'Resistor', 'ref': 'R27', 'val': '47k', 'x': 120, 'y': 70, 'fp': 'Resistor_SMD:R_0402_1005Metric'},
    ]
    wires = [
        (70, 70, 55, 70), (70, 75, 55, 75), (70, 80, 55, 80),
        (95, 70, 120, 70), (120, 70, 155, 70),
        (185, 70, 200, 70), (185, 75, 200, 75),
        (70, 90, 55, 100), (185, 90, 200, 100),
    ]
    labels_list = [('VIN_4V5', 45, 70, 0)]
    glabels = [
        ('SEQ_OUT_A', 95, 65, 'output', 0),
        ('SEQ_OUT_B', 185, 65, 'output', 0),
        ('GND', 70, 120, 'input', 90), ('GND', 200, 100, 'input', 90),
        ('SEQ_EN', 45, 100, 'input', 180),
    ]
    make_sheet('Sheet13_Sequencer.kicad_sch', comp, wires, labels_list, glabels,
               'Power Sequencer', 'Sheet 13: 2x TPS7H3014-SP, 5-Rail Supervision + Daisy-Chain',
               'Sequencing: VCCINT -> VDDIO -> VANA -> VDIG -> VCLK')


# ===== Sheet14: Connectors =====
def gen_sheet14():
    comp = [
        {'lib': 'Inductor', 'ref': 'J1', 'val': 'JTAG_HDR', 'x': 60, 'y': 60, 'fp': 'Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical'},
        {'lib': 'Inductor', 'ref': 'J2', 'val': 'SPW_TX', 'x': 120, 'y': 60, 'fp': 'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical'},
        {'lib': 'Inductor', 'ref': 'J3', 'val': 'SPW_RX', 'x': 180, 'y': 60, 'fp': 'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical'},
        {'lib': 'Inductor', 'ref': 'J4', 'val': 'POWER_IN', 'x': 60, 'y': 130, 'fp': 'TerminalBlock:TerminalBlock_bornier-2_P5.08mm'},
        {'lib': 'Inductor', 'ref': 'J5', 'val': 'UART', 'x': 120, 'y': 130, 'fp': 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical'},
        {'lib': 'Inductor', 'ref': 'J6', 'val': 'GPIO', 'x': 180, 'y': 130, 'fp': 'Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical'},
    ]
    wires = [
        (55, 55, 45, 55), (55, 60, 45, 60), (55, 65, 45, 65), (55, 70, 45, 70),
        (115, 55, 105, 55), (115, 60, 105, 60), (115, 65, 105, 65),
        (175, 55, 165, 55), (175, 60, 165, 60), (175, 65, 165, 65),
        (55, 130, 45, 130), (55, 135, 45, 135),
        (115, 125, 105, 125), (115, 130, 105, 130),
    ]
    labels_list = []
    glabels = [
        ('TCK', 45, 55, 'input', 180), ('TMS', 45, 60, 'input', 180),
        ('TDI', 45, 65, 'input', 180), ('TDO', 45, 70, 'input', 180),
        ('SPW0_TX+', 105, 55, 'output', 180), ('SPW0_TX-', 105, 60, 'output', 180),
        ('SPW0_RX+', 105, 65, 'output', 180),
        ('SPW1_TX+', 165, 55, 'output', 180), ('SPW1_TX-', 165, 60, 'output', 180),
        ('SPW1_RX+', 165, 65, 'output', 180),
        ('VIN_4V5', 45, 130, 'input', 180), ('GND', 45, 135, 'input', 180),
        ('UART_TX', 105, 125, 'output', 180), ('UART_RX', 105, 130, 'output', 180),
    ]
    make_sheet('Sheet14_Connectors.kicad_sch', comp, wires, labels_list, glabels,
               'Connectors & Interfaces', 'Sheet 14: JTAG, SpaceWire, Power, UART, GPIO')


# ===== Sheet15: Test Points =====
def gen_sheet15():
    comp = []
    wires = []
    labels_list = []
    glabels = []
    # Generate test points for each rail
    rails = [
        ('VCCINT_1V0', 40, 50), ('VDDIO_1V8', 40, 70), ('VDDIO_3V3', 40, 90),
        ('VANA_1V0', 40, 110), ('VDIG_1V8', 40, 130), ('VCLK_2V5', 40, 150),
        ('VIN_4V5', 40, 170),
        ('BUCK1_PG', 120, 50), ('BUCK2_PG', 120, 70), ('BUCK3_PG', 120, 90),
        ('SEQ_OUT_A', 120, 110), ('SEQ_OUT_B', 120, 130),
        ('SPW0_TX+', 200, 50), ('SPW0_TX-', 200, 70),
        ('SPW1_TX+', 200, 90), ('SPW1_TX-', 200, 110),
        ('JESD_SYNC', 200, 130), ('FPGA_CLK', 200, 150),
    ]
    for name, x, y in rails:
        comp.append({'lib': 'Capacitor', 'ref': f'TP{len(comp)+1}', 'val': name, 'x': x, 'y': y,
                     'fp': 'TestPoint:TestPoint_Pad_1.5x1.5mm'})
        glabels.append((name, x-15, y, 'bidirectional', 180))
    make_sheet('Sheet15_TestPoints.kicad_sch', comp, wires, labels_list, glabels,
               'Test Points', 'Sheet 15: All Rails and Signals')


# ===== Sheet16: Decoupling Summary =====
def gen_sheet16():
    comp = []
    wires = []
    labels_list = []
    glabels = []
    # Decoupling caps grouped by IC
    groups = [
        ('FPGA XQRVC1902', 60, 50, [('C_FPGA_1', '100nF'), ('C_FPGA_2', '10uF'), ('C_FPGA_3', '4.7uF')]),
        ('ADC12DJ5200-SP', 60, 90, [('C_ADC_1', '100nF'), ('C_ADC_2', '10uF'), ('C_ADC_3', '1uF')]),
        ('TPS7H5002-SP', 60, 130, [('C_BUCK1_1', '100nF'), ('C_BUCK1_2', '10uF')]),
        ('ISL70003ASEH #1', 200, 50, [('C_BUCK2_1', '100nF'), ('C_BUCK2_2', '10uF')]),
        ('ISL70003ASEH #2', 200, 90, [('C_BUCK3_1', '100nF'), ('C_BUCK3_2', '10uF')]),
        ('TPS7H1111-SP x2', 200, 130, [('C_LDO_1', '100nF'), ('C_LDO_2', '10uF')]),
        ('TPS7H1121-SP', 200, 170, [('C_CLK_1', '100nF'), ('C_CLK_2', '1uF')]),
    ]
    for grp_name, gx, gy, caps in groups:
        comp.append({'lib': 'Resistor', 'ref': f'FB{len(comp)+1}', 'val': grp_name, 'x': gx, 'y': gy,
                     'fp': 'Resistor_SMD:R_0402_1005Metric'})
        for i, (cname, cval) in enumerate(caps):
            comp.append({'lib': 'Capacitor', 'ref': cname, 'val': cval, 'x': gx + 30 + i*20, 'y': gy,
                         'fp': 'Capacitor_SMD:C_0402_1005Metric'})
    make_sheet('Sheet16_Decoupling.kicad_sch', comp, wires, labels_list, glabels,
               'Decoupling Summary', 'Sheet 16: Bypass Capacitors per IC Group')


# ===== Sheet17: Power Tree =====
def gen_sheet17():
    comp = []
    wires = []
    labels_list = []
    glabels = []
    # Power tree visualization
    rails = [
        ('VIN 4.5V', 40, 60), ('TPS7H5002', 120, 40), ('ISL70003A', 120, 70),
        ('ISL70003A', 120, 100), ('TPS7H1111', 200, 40), ('TPS7H1111', 200, 70),
        ('TPS7H1121', 200, 100),
        ('VCCINT 1.0V', 280, 40), ('VDDIO 1.8V', 280, 70), ('VDDIO 3.3V', 280, 100),
        ('VANA 1.0V', 360, 40), ('VDIG 1.8V', 360, 70), ('VCLK 2.5V', 360, 100),
    ]
    for name, x, y in rails:
        comp.append({'lib': 'Resistor', 'ref': f'PT{len(comp)+1}', 'val': name, 'x': x, 'y': y,
                     'fp': 'Resistor_SMD:R_0402_1005Metric'})
    wires = [
        (60, 60, 120, 40), (60, 60, 120, 70), (60, 60, 120, 100),
        (140, 40, 200, 40), (140, 70, 200, 70), (140, 100, 200, 100),
        (220, 40, 280, 40), (220, 70, 280, 70), (220, 100, 280, 100),
        (300, 40, 360, 40), (300, 70, 360, 70), (300, 100, 360, 100),
    ]
    make_sheet('Sheet17_PowerTree.kicad_sch', comp, wires, labels_list, glabels,
               'Power Tree', 'Sheet 17: Power Block Diagram and Sequencing',
               'VIN 4.5V -> 6 rails via 3 buck + 3 LDO')


# Generate all sheets
print("Generating schematic sheets with wiring...")
gen_sheet07()
gen_sheet08()
gen_sheet09()
gen_sheet10()
gen_sheet11()
gen_sheet12()
gen_sheet13()
gen_sheet14()
gen_sheet15()
gen_sheet16()
gen_sheet17()
print("\nAll sheets generated.")
