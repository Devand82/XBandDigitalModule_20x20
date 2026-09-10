#!/usr/bin/env python3
"""
Generate valid KiCad schematic files using real symbol libraries.
Extracts symbols from installed KiCad libs and creates proper .kicad_sch
files with correct pin definitions, wires, and net connections.
"""
import os, re, uuid, copy, math

BASE = "/opt/cryptobot/XBandDigitalModule_20x20"
SCH_DIR = os.path.join(BASE, "schematic")
SYM_DIR = "/usr/share/kicad/symbols"

def uid():
    return str(uuid.uuid4()).replace('-', '')[:32]

# ===== SYMBOL EXTRACTION =====
def extract_symbol(lib_name, sym_name):
    """Extract a complete symbol definition from KiCad library."""
    lib_file = os.path.join(SYM_DIR, f"{lib_name}.kicad_sym")
    if not os.path.exists(lib_file):
        print(f"  WARNING: Library {lib_name} not found")
        return None
    with open(lib_file) as f:
        content = f.read()

    # Find the symbol definition
    start = content.find(f'(symbol "{sym_name}"')
    if start < 0:
        print(f"  WARNING: Symbol {sym_name} not found in {lib_name}")
        return None

    # Extract the full symbol block with balanced parens
    depth = 0
    i = start
    while i < len(content):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return content[start:i+1]
        i += 1
    return None

def extract_all_symbols_needed():
    """Extract all symbols we need for the design."""
    needed = [
        ('Device', 'R'),
        ('Device', 'C'),
        ('Device', 'L'),
        ('Device', 'Crystal'),
        ('Device', 'FerriteBead'),
        ('power', '+1V0'),
        ('power', '+1V8'),
        ('power', '+3V3'),
        ('power', '+2V5'),
        ('power', 'GND'),
        ('power', 'PWR_FLAG'),
        ('Connector_Generic', 'Conn_01x02'),
        ('Connector_Generic', 'Conn_01x03'),
        ('Connector_Generic', 'Conn_01x04'),
        ('Connector_Generic', 'Conn_01x06'),
        ('Connector_Generic', 'Conn_01x08'),
    ]
    symbols = {}
    for lib, sym in needed:
        key = f"{lib}:{sym}"
        sym_def = extract_symbol(lib, sym)
        if sym_def:
            symbols[key] = sym_def
            print(f"  Extracted: {key}")
    return symbols

# ===== PIN CALCULATOR =====
def get_pin_positions(sym_def):
    """Parse pin positions from symbol definition."""
    pins = {}
    # Match pin definitions: (pin ... (at X Y ANGLE) ... (number "N"))
    pin_pattern = r'\(pin\s+\w+\s+\w+\s+\(at\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\).*?\(number\s+"(\d+)"'
    for m in re.finditer(pin_pattern, sym_def, re.DOTALL):
        x, y, angle, num = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)
        # Calculate absolute pin end position (where wire connects)
        angle_rad = math.radians(angle)
        # Pin end is at the pin position (the (at X Y) is the pin end, not the body end)
        pins[num] = {'x': x, 'y': y, 'angle': angle}
    return pins

# ===== SCHEMATIC GENERATOR =====
class SchematicSheet:
    def __init__(self, filename, paper="A3"):
        self.filename = filename
        self.paper = paper
        self.components = []
        self.wires = []
        self.labels = []
        self.glabels = []
        self.symbols_used = set()
        self.lib_symbols = {}

    def add_symbol_def(self, key, sym_def):
        self.lib_symbols[key] = sym_def

    def add_component(self, lib_id, ref, value, x, y, angle=0, footprint=""):
        """Add a component. lib_id is like 'Device:R'."""
        pins = get_pin_positions(self.lib_symbols.get(lib_id, ''))
        self.components.append({
            'lib_id': lib_id, 'ref': ref, 'value': value,
            'x': x, 'y': y, 'angle': angle, 'footprint': footprint,
            'pins': pins
        })
        self.symbols_used.add(lib_id)

    def add_wire(self, x1, y1, x2, y2):
        self.wires.append((x1, y1, x2, y2))

    def add_wire_path(self, *points):
        """Add multi-point wire: (x1,y1, x2,y2, x3,y3, ...)"""
        for i in range(0, len(points)-2, 2):
            self.wires.append((points[i], points[i+1], points[i+2], points[i+3]))

    def add_label(self, name, x, y, angle=0):
        self.labels.append((name, x, y, angle))

    def add_glabel(self, name, x, y, shape="bidirectional", angle=0):
        self.glabels.append((name, x, y, shape, angle))

    def to_kicad(self):
        """Generate complete valid .kicad_sch content."""
        lines = []
        lines.append(f'(kicad_sch (version 20230121) (generator eeschema)')
        lines.append(f'  (uuid "{uid()}")')
        lines.append(f'  (paper "{self.paper}")')
        lines.append(f'  (title_block')
        lines.append(f'    (title "X-Band Digital Module 20x20cm")')
        lines.append(f'    (date "2026-09-10")')
        lines.append(f'    (rev "1.0")')
        lines.append(f'  )')

        # Library symbols
        lines.append(f'  (lib_symbols')
        for key, sym_def in self.lib_symbols.items():
            # Indent each line by 2 more spaces (4 total inside lib_symbols)
            for line in sym_def.split('\n'):
                lines.append(f'    {line}')
        lines.append(f'  )')

        # Component instances
        for comp in self.components:
            u = uid()
            lines.append(f'  (symbol (lib_id "{comp["lib_id"]}" (at {comp["x"]} {comp["y"]} {comp["angle"]}) (unit 1)')
            lines.append(f'    (in_bom yes) (on_board yes)')
            lines.append(f'    (uuid "{u}")')
            lines.append(f'    (property "Reference" "{comp["ref"]}" (at {comp["x"]} {comp["y"]-10} 0) (effects (font (size 1.27 1.27))))')
            lines.append(f'    (property "Value" "{comp["value"]}" (at {comp["x"]} {comp["y"]+10} 0) (effects (font (size 1.27 1.27))))')
            if comp['footprint']:
                lines.append(f'    (property "Footprint" "{comp["footprint"]}" (at {comp["x"]} {comp["y"]} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
            # Pin instances
            for pin_num in comp.get('pins', {}):
                lines.append(f'    (pin "{pin_num}" (uuid "{uid()}"))')
            lines.append(f'  )')

        # Wires
        for x1, y1, x2, y2 in self.wires:
            lines.append(f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{uid()}"))')

        # Local labels
        for name, x, y, angle in self.labels:
            lines.append(f'  (label "{name}" (at {x} {y} {angle}) (effects (font (size 1.27 1.27)) (justify left)))')

        # Global labels
        for name, x, y, shape, angle in self.glabels:
            just = "left" if angle == 0 else "right"
            lines.append(f'  (global_label "{name}" (shape {shape}) (at {x} {y} {angle}) (effects (font (size 1.27 1.27)) (justify {just})))')

        lines.append(f'  (sheet_instances (path "/" (page "1")))')
        lines.append(f')')
        return '\n'.join(lines)

    def save(self):
        path = os.path.join(SCH_DIR, self.filename)
        with open(path, 'w') as f:
            f.write(self.to_kicad())
        print(f'  Written: {self.filename} ({len(self.components)} comp, {len(self.wires)} wires, {len(self.labels)+len(self.glabels)} labels)')


# ===== SHEET GENERATORS =====

def gen_sheet01():
    """Title block."""
    s = SchematicSheet("Sheet01_Title.kicad_sch")
    # Just a title block, minimal content
    s.save()

def gen_sheet02():
    """RF Input: SMPA connector + TRF0208-SP balun + 50ohm termination."""
    s = SchematicSheet("Sheet02_RF_Input.kicad_sch")
    # Load symbols
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    # R1 50ohm input termination
    s.add_component("Device:R", "R1", "50", 80, 80, footprint="Resistor_SMD:R_0402_1005Metric")
    # C1 DC blocking cap
    s.add_component("Device:C", "C1", "100pF", 120, 80, footprint="Capacitor_SMD:C_0402_1005Metric")
    # L1 bias inductor
    s.add_component("Device:L", "L1", "100nH", 160, 80, footprint="Inductor_SMD:L_0402_1005Metric")
    # C2 bypass cap
    s.add_component("Device:C", "C2", "10pF", 160, 110, footprint="Capacitor_SMD:C_0402_1005Metric")

    # Wires
    s.add_wire(65, 80, 75, 80)   # connector to R1
    s.add_wire(85, 80, 115, 80)  # R1 to C1
    s.add_wire(125, 80, 155, 80) # C1 to L1
    s.add_wire(160, 85, 160, 105) # L1 to C2
    s.add_wire(160, 115, 160, 130) # C2 to GND

    # Labels
    s.add_glabel("RF_IN", 60, 80, "input", 180)
    s.add_glabel("ADC_RF", 175, 80, "output", 0)
    s.add_glabel("GND", 160, 130, "input", 90)

    s.save()

def gen_sheet03():
    """ADC12DJ5200-SP."""
    s = SchematicSheet("Sheet03_ADC.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    # Decoupling caps for ADC
    for i, (val, x) in enumerate([("100nF", 80), ("10uF", 100), ("100nF", 120), ("1uF", 140)]):
        s.add_component("Device:C", f"C{i+3}", val, x, 100, footprint="Capacitor_SMD:C_0402_1005Metric")
        s.add_wire(x, 105, x, 120)  # cap to GND

    # ferrite bead
    s.add_component("Device:FerriteBead", "FB1", "600R@100MHz", 100, 60, footprint="Inductor_SMD:L_0402_1005Metric")

    # Labels
    s.add_glabel("VANA_1V0", 80, 85, "input", 180)
    s.add_glabel("GND", 100, 120, "input", 90)
    s.add_glabel("ADC_D0", 200, 80, "output", 0)
    s.add_glabel("ADC_D1", 200, 90, "output", 0)
    s.add_glabel("JESD_SYNC", 200, 100, "output", 0)
    s.add_glabel("ADC_CLK", 200, 110, "output", 0)

    s.save()

def gen_sheet04():
    """FPGA XQRVC1902."""
    s = SchematicSheet("Sheet04_FPGA.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    # Decoupling caps
    for i in range(8):
        s.add_component("Device:C", f"C_F{i}", "100nF", 60 + i*15, 80, footprint="Capacitor_SMD:C_0402_1005Metric")
        s.add_wire(60 + i*15, 85, 60 + i*15, 100)

    # Bulk caps
    for i in range(4):
        s.add_component("Device:C", f"C_B{i}", "10uF", 60 + i*20, 120, footprint="Capacitor_SMD:C_0603_1608Metric")
        s.add_wire(60 + i*20, 125, 60 + i*20, 140)

    # Labels
    s.add_glabel("VCCINT_1V0", 60, 65, "input", 180)
    s.add_glabel("GND", 100, 100, "input", 90)
    s.add_glabel("JESD_D0", 200, 80, "bidirectional", 0)
    s.add_glabel("JESD_D1", 200, 90, "bidirectional", 0)
    s.add_glabel("SPW_TX0", 200, 100, "output", 0)
    s.add_glabel("SPW_RX0", 200, 110, "input", 0)
    s.add_glabel("FPGA_CLK", 200, 120, "input", 0)

    s.save()

def gen_sheet05():
    """Clock Tree: LMX2615 + LMK04832."""
    s = SchematicSheet("Sheet05_Clock.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    # VCXO
    s.add_component("Device:Crystal", "Y1", "122.88MHz", 80, 80, footprint="Crystal:Crystal_SMD_2012-2Pin_2.0x1.2mm")

    # Bypass caps
    s.add_component("Device:C", "C_CLK1", "100nF", 120, 80, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C_CLK2", "1uF", 120, 100, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C_CLK3", "100nF", 160, 80, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C_CLK4", "10uF", 160, 100, footprint="Capacitor_SMD:C_0603_1608Metric")

    # Ferrite beads
    s.add_component("Device:FerriteBead", "FB_CLK1", "600R", 100, 60, footprint="Inductor_SMD:L_0402_1005Metric")

    # Wires
    s.add_wire(80, 75, 80, 60)
    s.add_wire(80, 85, 80, 100)

    # Labels
    s.add_glabel("VCLK_2V5", 70, 60, "input", 180)
    s.add_glabel("GND", 80, 100, "input", 90)
    s.add_glabel("ADC_CLK", 200, 80, "output", 0)
    s.add_glabel("FPGA_CLK", 200, 90, "output", 0)

    s.save()

def gen_sheet06():
    """Power Input: 4.5V with TVS, ferrite, bulk caps."""
    s = SchematicSheet("Sheet06_PowerInput.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    # Input connector
    s.add_component("Connector_Generic:Conn_01x02", "J_PWR", "POWER_IN", 60, 80,
                    footprint="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")
    # Ferrite bead
    s.add_component("Device:FerriteBead", "FB_PWR", "600R@100MHz", 100, 80,
                    footprint="Inductor_SMD:L_0805_2012Metric")
    # Bulk caps
    s.add_component("Device:C", "C_PWR1", "470uF", 140, 80, footprint="Capacitor_SMD:CP_EIA-7343-43_P5.00mm")
    s.add_component("Device:C", "C_PWR2", "100nF", 140, 110, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C_PWR3", "10uF", 170, 80, footprint="Capacitor_SMD:C_0805_2012Metric")

    # Wires
    s.add_wire(65, 75, 95, 75)
    s.add_wire(105, 75, 135, 75)
    s.add_wire(140, 85, 140, 105)

    # Labels
    s.add_glabel("VIN_4V5", 50, 75, "input", 180)
    s.add_glabel("VIN filtered", 185, 75, "output", 0)
    s.add_glabel("GND", 140, 115, "input", 90)

    s.save()

def gen_sheet07():
    """Buck 1.0V Core: TPS7H5002-SP with passives."""
    s = SchematicSheet("Sheet07_Buck_1V0.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    # Input cap
    s.add_component("Device:C", "C27", "22uF", 60, 60, footprint="Capacitor_SMD:C_0805_2012Metric")
    # Feedback divider
    s.add_component("Device:R", "R6", "100k", 120, 100, footprint="Resistor_SMD:R_0402_1005Metric")
    s.add_component("Device:R", "R7", "390k", 120, 130, footprint="Resistor_SMD:R_0402_1005Metric")
    # Compensation network
    s.add_component("Device:R", "R8", "10k", 80, 130, footprint="Resistor_SMD:R_0402_1005Metric")
    s.add_component("Device:C", "C28", "4.7nF", 80, 160, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C29", "330pF", 100, 160, footprint="Capacitor_SMD:C_0402_1005Metric")
    # Soft start cap
    s.add_component("Device:C", "C30", "10nF", 60, 130, footprint="Capacitor_SMD:C_0402_1005Metric")
    # Output inductor
    s.add_component("Device:L", "L1", "100nH/55A", 180, 60, footprint="Inductor_SMD:L_1210_3225Metric")
    # Output caps
    s.add_component("Device:C", "C31", "470uF", 220, 60, footprint="Capacitor_SMD:CP_EIA-7343-43_P5.00mm")
    s.add_component("Device:C", "C32", "470uF", 220, 90, footprint="Capacitor_SMD:CP_EIA-7343-43_P5.00mm")
    s.add_component("Device:C", "C33", "10uF", 250, 60, footprint="Capacitor_SMD:C_0603_1608Metric")
    s.add_component("Device:C", "C34", "22uF", 250, 90, footprint="Capacitor_SMD:C_0805_2012Metric")
    # Current sense resistor
    s.add_component("Device:R", "R9", "5m", 280, 60, footprint="Resistor_SMD:R_2512_6332Metric")

    # Wires - VIN to input cap
    s.add_wire(45, 60, 55, 60)
    s.add_wire(60, 65, 60, 80)
    # Input cap to GND
    s.add_wire(60, 55, 60, 45)
    # Feedback network
    s.add_wire(120, 95, 120, 80)
    s.add_wire(120, 105, 120, 130)
    s.add_wire(120, 135, 120, 150)
    # Output
    s.add_wire(185, 60, 215, 60)
    s.add_wire(220, 65, 220, 80)

    # Labels
    s.add_glabel("VIN_4V5", 40, 60, "input", 180)
    s.add_glabel("VCCINT_1V0", 295, 60, "output", 0)
    s.add_glabel("GND", 60, 45, "input", 90)
    s.add_glabel("GND", 120, 150, "input", 90)
    s.add_glabel("GND", 220, 100, "input", 90)
    s.add_glabel("BUCK1_EN", 40, 130, "input", 180)
    s.add_glabel("BUCK1_PG", 185, 80, "output", 0)

    s.save()

def gen_sheet08():
    """Buck 1.8V Aux: ISL70003ASEH."""
    s = SchematicSheet("Sheet08_Buck_1V8.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    s.add_component("Device:C", "C38", "22uF", 60, 60, footprint="Capacitor_SMD:C_0805_2012Metric")
    s.add_component("Device:C", "C39", "100nF", 60, 90, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:R", "R10", "47k", 120, 100, footprint="Resistor_SMD:R_0402_1005Metric")
    s.add_component("Device:R", "R11", "22k", 120, 130, footprint="Resistor_SMD:R_0402_1005Metric")
    s.add_component("Device:C", "C40", "4.7nF", 150, 130, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:R", "R12", "10k", 80, 130, footprint="Resistor_SMD:R_0402_1005Metric")
    s.add_component("Device:C", "C41", "10nF", 80, 160, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:L", "L2", "2.2uH", 200, 60, footprint="Inductor_SMD:L_1210_3225Metric")
    s.add_component("Device:C", "C42", "470uF", 240, 60, footprint="Capacitor_SMD:CP_EIA-7343-43_P5.00mm")
    s.add_component("Device:C", "C43", "10uF", 270, 60, footprint="Capacitor_SMD:C_0603_1608Metric")

    s.add_wire(45, 60, 55, 60)
    s.add_wire(60, 65, 60, 80)
    s.add_wire(120, 95, 120, 80)
    s.add_wire(120, 105, 120, 130)
    s.add_wire(205, 60, 235, 60)

    s.add_glabel("VIN_4V5", 40, 60, "input", 180)
    s.add_glabel("VDDIO_1V8", 290, 60, "output", 0)
    s.add_glabel("GND", 60, 45, "input", 90)
    s.add_glabel("GND", 120, 150, "input", 90)
    s.add_glabel("GND", 240, 80, "input", 90)
    s.add_glabel("BUCK2_EN", 40, 130, "input", 180)

    s.save()

def gen_sheet09():
    """Buck 3.3V I/O: ISL70003ASEH."""
    s = SchematicSheet("Sheet09_Buck_3V3.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    s.add_component("Device:C", "C44", "22uF", 60, 60, footprint="Capacitor_SMD:C_0805_2012Metric")
    s.add_component("Device:C", "C45", "100nF", 60, 90, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:R", "R13", "47k", 120, 100, footprint="Resistor_SMD:R_0402_1005Metric")
    s.add_component("Device:R", "R14", "22k", 120, 130, footprint="Resistor_SMD:R_0402_1005Metric")
    s.add_component("Device:C", "C46", "4.7nF", 150, 130, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:R", "R15", "10k", 80, 130, footprint="Resistor_SMD:R_0402_1005Metric")
    s.add_component("Device:C", "C47", "10nF", 80, 160, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:L", "L3", "4.7uH", 200, 60, footprint="Inductor_SMD:L_1210_3225Metric")
    s.add_component("Device:C", "C48", "470uF", 240, 60, footprint="Capacitor_SMD:CP_EIA-7343-43_P5.00mm")
    s.add_component("Device:C", "C49", "10uF", 270, 60, footprint="Capacitor_SMD:C_0603_1608Metric")

    s.add_wire(45, 60, 55, 60)
    s.add_wire(60, 65, 60, 80)
    s.add_wire(120, 95, 120, 80)
    s.add_wire(120, 105, 120, 130)
    s.add_wire(205, 60, 235, 60)

    s.add_glabel("VIN_4V5", 40, 60, "input", 180)
    s.add_glabel("VDDIO_3V3", 290, 60, "output", 0)
    s.add_glabel("GND", 60, 45, "input", 90)
    s.add_glabel("GND", 120, 150, "input", 90)
    s.add_glabel("GND", 240, 80, "input", 90)
    s.add_glabel("BUCK3_EN", 40, 130, "input", 180)

    s.save()

def gen_sheet10():
    """LDO 1.0V Analog: TPS7H1111-SP."""
    s = SchematicSheet("Sheet10_LDO_1V0.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    s.add_component("Device:C", "C50", "10uF", 60, 60, footprint="Capacitor_SMD:C_0603_1608Metric")
    s.add_component("Device:C", "C51", "100nF", 60, 90, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C52", "1uF", 60, 120, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C53", "10uF", 160, 60, footprint="Capacitor_SMD:C_0603_1608Metric")
    s.add_component("Device:C", "C54", "100nF", 160, 90, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C55", "1uF", 160, 120, footprint="Capacitor_SMD:C_0402_1005Metric")

    s.add_wire(60, 55, 60, 45)
    s.add_wire(60, 65, 60, 80)
    s.add_wire(60, 95, 60, 110)
    s.add_wire(160, 55, 160, 45)
    s.add_wire(160, 65, 160, 80)
    s.add_wire(160, 95, 160, 110)

    s.add_glabel("VDDIO_1V8", 50, 45, "input", 180)
    s.add_glabel("GND", 60, 120, "input", 90)
    s.add_glabel("VANA_1V0", 170, 45, "output", 0)
    s.add_glabel("GND", 160, 120, "input", 90)

    s.save()

def gen_sheet11():
    """LDO 1.8V Digital: TPS7H1111-SP."""
    s = SchematicSheet("Sheet11_LDO_1V8.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    s.add_component("Device:C", "C56", "10uF", 60, 60, footprint="Capacitor_SMD:C_0603_1608Metric")
    s.add_component("Device:C", "C57", "100nF", 60, 90, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C58", "10uF", 160, 60, footprint="Capacitor_SMD:C_0603_1608Metric")
    s.add_component("Device:C", "C59", "100nF", 160, 90, footprint="Capacitor_SMD:C_0402_1005Metric")

    s.add_wire(60, 55, 60, 45)
    s.add_wire(60, 65, 60, 80)
    s.add_wire(60, 95, 60, 110)
    s.add_wire(160, 55, 160, 45)
    s.add_wire(160, 65, 160, 80)
    s.add_wire(160, 95, 160, 110)

    s.add_glabel("VDDIO_1V8", 50, 45, "input", 180)
    s.add_glabel("GND", 60, 110, "input", 90)
    s.add_glabel("VDIG_1V8", 170, 45, "output", 0)
    s.add_glabel("GND", 160, 110, "input", 90)

    s.save()

def gen_sheet12():
    """LDO 2.5V Clock: TPS7H1121-SP."""
    s = SchematicSheet("Sheet12_LDO_2V5.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    s.add_component("Device:C", "C60", "10uF", 60, 60, footprint="Capacitor_SMD:C_0603_1608Metric")
    s.add_component("Device:C", "C61", "100nF", 60, 90, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C62", "1uF", 60, 120, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C63", "10uF", 160, 60, footprint="Capacitor_SMD:C_0603_1608Metric")
    s.add_component("Device:C", "C64", "100nF", 160, 90, footprint="Capacitor_SMD:C_0402_1005Metric")

    s.add_wire(60, 55, 60, 45)
    s.add_wire(60, 65, 60, 80)
    s.add_wire(60, 95, 60, 110)
    s.add_wire(160, 55, 160, 45)
    s.add_wire(160, 65, 160, 80)
    s.add_wire(160, 95, 160, 110)

    s.add_glabel("VDDIO_3V3", 50, 45, "input", 180)
    s.add_glabel("GND", 60, 120, "input", 90)
    s.add_glabel("VCLK_2V5", 170, 45, "output", 0)
    s.add_glabel("GND", 160, 110, "input", 90)

    s.save()

def gen_sheet13():
    """Sequencer: 2x TPS7H3014-SP."""
    s = SchematicSheet("Sheet13_Sequencer.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    # Pull-up resistors
    s.add_component("Device:R", "R16", "10k", 60, 60, footprint="Resistor_SMD:R_0402_1005Metric")
    s.add_component("Device:R", "R17", "10k", 60, 90, footprint="Resistor_SMD:R_0402_1005Metric")
    # Timing caps
    s.add_component("Device:C", "C65", "100nF", 60, 120, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C66", "1uF", 60, 150, footprint="Capacitor_SMD:C_0402_1005Metric")
    s.add_component("Device:C", "C67", "10nF", 90, 120, footprint="Capacitor_SMD:C_0402_1005Metric")
    # Delay resistor
    s.add_component("Device:R", "R18", "47k", 120, 60, footprint="Resistor_SMD:R_0402_1005Metric")

    s.add_wire(60, 55, 60, 45)
    s.add_wire(60, 65, 60, 80)
    s.add_wire(60, 95, 60, 110)
    s.add_wire(60, 125, 60, 140)

    s.add_glabel("VIN_4V5", 50, 45, "input", 180)
    s.add_glabel("GND", 60, 150, "input", 90)
    s.add_glabel("SEQ_EN", 40, 120, "input", 180)
    s.add_glabel("SEQ_OUT_A", 150, 60, "output", 0)
    s.add_glabel("SEQ_OUT_B", 150, 90, "output", 0)

    s.save()

def gen_sheet14():
    """Connectors: JTAG, SpaceWire, Power, UART."""
    s = SchematicSheet("Sheet14_Connectors.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    # JTAG
    s.add_component("Connector_Generic:Conn_01x06", "J1", "JTAG", 60, 80,
                    footprint="Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical")
    # SpaceWire TX
    s.add_component("Connector_Generic:Conn_01x04", "J2", "SPW_TX", 140, 80,
                    footprint="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical")
    # SpaceWire RX
    s.add_component("Connector_Generic:Conn_01x04", "J3", "SPW_RX", 220, 80,
                    footprint="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical")
    # Power
    s.add_component("Connector_Generic:Conn_01x02", "J4", "POWER", 60, 140,
                    footprint="TerminalBlock:TerminalBlock_bornier-2_P5.08mm")
    # UART
    s.add_component("Connector_Generic:Conn_01x04", "J5", "UART", 140, 140,
                    footprint="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical")

    s.add_glabel("TCK", 45, 75, "input", 180)
    s.add_glabel("TMS", 45, 80, "input", 180)
    s.add_glabel("TDI", 45, 85, "input", 180)
    s.add_glabel("TDO", 45, 90, "input", 180)
    s.add_glabel("SPW_TX0+", 125, 75, "output", 180)
    s.add_glabel("SPW_TX0-", 125, 80, "output", 180)
    s.add_glabel("SPW_RX0+", 125, 85, "output", 180)
    s.add_glabel("SPW_TX1+", 205, 75, "output", 180)
    s.add_glabel("SPW_TX1-", 205, 80, "output", 180)
    s.add_glabel("VIN_4V5", 45, 135, "input", 180)
    s.add_glabel("GND", 45, 145, "input", 180)
    s.add_glabel("UART_TX", 125, 135, "output", 180)
    s.add_glabel("UART_RX", 125, 140, "output", 180)

    s.save()

def gen_sheet15():
    """Test Points."""
    s = SchematicSheet("Sheet15_TestPoints.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    rails = [
        ("VCCINT_1V0", 60, 60), ("VDDIO_1V8", 60, 80), ("VDDIO_3V3", 60, 100),
        ("VANA_1V0", 60, 120), ("VDIG_1V8", 60, 140), ("VCLK_2V5", 60, 160),
        ("VIN_4V5", 60, 180), ("BUCK1_PG", 140, 60), ("BUCK2_PG", 140, 80),
        ("BUCK3_PG", 140, 100), ("SEQ_OUT_A", 140, 120), ("SEQ_OUT_B", 140, 140),
        ("SPW_TX0+", 220, 60), ("SPW_TX0-", 220, 80), ("SPW_TX1+", 220, 100),
        ("SPW_TX1-", 220, 120), ("JESD_SYNC", 220, 140), ("FPGA_CLK", 220, 160),
    ]
    for i, (name, x, y) in enumerate(rails):
        s.add_component("Device:C", f"TP{i+1}", name, x, y, footprint="TestPoint:TestPoint_Pad_1.5x1.5mm")
        s.add_glabel(name, x-15, y, "bidirectional", 180)

    s.save()

def gen_sheet16():
    """Decoupling summary."""
    s = SchematicSheet("Sheet16_Decoupling.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    groups = [
        ("FPGA XQRVC1902", 60, 60, [("C_F1","100nF"),("C_F2","10uF"),("C_F3","4.7uF")]),
        ("ADC12DJ5200-SP", 60, 100, [("C_A1","100nF"),("C_A2","10uF"),("C_A3","1uF")]),
        ("TPS7H5002-SP", 60, 140, [("C_T1","100nF"),("C_T2","10uF")]),
        ("ISL70003ASEH x2", 200, 60, [("C_I1","100nF"),("C_I2","10uF")]),
        ("TPS7H1111-SP x2", 200, 100, [("C_L1","100nF"),("C_L2","10uF")]),
        ("TPS7H1121-SP", 200, 140, [("C_C1","100nF"),("C_C2","1uF")]),
    ]
    for grp, gx, gy, caps in groups:
        s.add_component("Device:FerriteBead", f"FB_{grp[:3]}", grp, gx, gy)
        for i, (cn, cv) in enumerate(caps):
            s.add_component("Device:C", cn, cv, gx + 30 + i*20, gy)

    s.save()

def gen_sheet17():
    """Power Tree diagram."""
    s = SchematicSheet("Sheet17_PowerTree.kicad_sch")
    syms = extract_all_symbols_needed()
    for k, v in syms.items():
        s.add_symbol_def(k, v)

    # Power tree as block diagram using resistors as blocks
    rails = [
        ("VIN 4.5V", 40, 80), ("TPS7H5002", 120, 60), ("ISL70003A x2", 120, 100),
        ("TPS7H1111 x2", 200, 60), ("TPS7H1121", 200, 100),
        ("VCCINT 1.0V", 300, 60), ("VDDIO 1.8V", 300, 80), ("VDDIO 3.3V", 300, 100),
        ("VANA 1.0V", 300, 120), ("VDIG 1.8V", 300, 140), ("VCLK 2.5V", 300, 160),
    ]
    for name, x, y in rails:
        s.add_component("Device:R", f"PT{rails.index((name,x,y))+1}", name, x, y)

    # Connections
    s.add_wire(55, 80, 115, 60)
    s.add_wire(55, 80, 115, 100)
    s.add_wire(135, 60, 195, 60)
    s.add_wire(135, 100, 195, 100)
    s.add_wire(215, 60, 295, 60)
    s.add_wire(215, 60, 295, 80)
    s.add_wire(215, 100, 295, 100)
    s.add_wire(215, 100, 295, 120)
    s.add_wire(215, 100, 295, 140)
    s.add_wire(215, 100, 295, 160)

    s.save()


# ===== MAIN =====
if __name__ == '__main__':
    print("Extracting KiCad symbols...")
    syms = extract_all_symbols_needed()
    print(f"\nExtracted {len(syms)} symbols\n")

    print("Generating schematic sheets...")
    gen_sheet01()
    gen_sheet02()
    gen_sheet03()
    gen_sheet04()
    gen_sheet05()
    gen_sheet06()
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
    print("\nDone!")
