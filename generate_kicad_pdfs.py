#!/usr/bin/env python3
"""Generate PDF exports from KiCad schematic and PCB files."""
import os
import re
import math
from fpdf import FPDF

BASE = "/opt/cryptobot/XBandDigitalModule_20x20"
SCHEMATIC_DIR = os.path.join(BASE, "schematic")
PCB_PATH = os.path.join(BASE, "pcb", "XBandDigitalModule.kicad_pcb")
OUTPUT = os.path.join(BASE, "exports")

# Colors
BLACK = (0, 0, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 180)
GREEN = (0, 140, 0)
GRAY = (160, 160, 160)
LIGHT_GRAY = (220, 220, 220)
YELLOW = (255, 200, 0)
CYAN = (0, 180, 180)
MAGENTA = (180, 0, 180)
ORANGE = (200, 120, 0)


class KiCadSchematicPDF(FPDF):
    """PDF renderer for KiCad schematics."""

    def __init__(self, sheet_name):
        super().__init__(orientation='L', unit='mm', format='A3')
        self.sheet_name = sheet_name
        self.set_auto_page_break(auto=False)

    def draw_title_block(self, title, subtitle=""):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(*BLUE)
        self.cell(0, 8, f"X-Band Digital Module - {title}", 0, 1, 'L')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*GRAY)
        self.cell(0, 5, subtitle, 0, 1, 'L')
        self.ln(2)
        # Border
        self.set_draw_color(*BLUE)
        self.rect(5, 5, 400, 280)

    def draw_component(self, ref, value, x, y, w=20, h=12, color=BLACK):
        """Draw a component box."""
        self.set_draw_color(*color)
        self.set_fill_color(255, 255, 240)
        self.rect(x, y, w, h, 'DF')
        self.set_font('Helvetica', 'B', 7)
        self.set_text_color(*BLACK)
        self.text(x + 1, y + 4, ref)
        self.set_font('Helvetica', '', 6)
        self.text(x + 1, y + 8, value[:15])

    def draw_ic(self, ref, value, x, y, w=30, h=40, pins_left=0, pins_right=0, color=BLUE):
        """Draw an IC with pins."""
        self.set_draw_color(*color)
        self.set_fill_color(230, 240, 255)
        self.rect(x, y, w, h, 'DF')
        # Notch
        self.set_fill_color(*color)
        self.ellipse(x + w/2 - 2, y, 4, 2, 'F')
        # Labels
        self.set_font('Helvetica', 'B', 7)
        self.set_text_color(*BLACK)
        self.text(x + w/2 - 8, y + h/2, ref)
        self.set_font('Helvetica', '', 5)
        self.text(x + 2, y + h/2 + 4, value[:20])
        # Pins
        pin_len = 3
        for i in range(pins_left):
            py = y + h * (i + 1) / (pins_left + 1)
            self.set_draw_color(*RED)
            self.line(x - pin_len, py, x, py)
        for i in range(pins_right):
            py = y + h * (i + 1) / (pins_right + 1)
            self.set_draw_color(*RED)
            self.line(x + w, py, x + w + pin_len, py)

    def draw_resistor(self, x, y, value="", vertical=False):
        self.set_draw_color(*ORANGE)
        if vertical:
            self.line(x, y, x, y + 2)
            self.rect(x - 1, y + 2, 2, 4)
            self.line(x, y + 6, x, y + 8)
            self.set_font('Helvetica', '', 4)
            self.text(x + 2, y + 5, value)
        else:
            self.line(x, y, x + 2, y)
            self.rect(x + 2, y - 1, 4, 2)
            self.line(x + 6, y, x + 8, y)
            self.set_font('Helvetica', '', 4)
            self.text(x + 2, y - 2, value)

    def draw_capacitor(self, x, y, value=""):
        self.set_draw_color(*CYAN)
        self.line(x, y, x + 2, y)
        self.line(x + 2, y - 2, x + 2, y + 2)
        self.line(x + 3, y - 2, x + 3, y + 2)
        self.line(x + 3, y, x + 5, y)
        self.set_font('Helvetica', '', 4)
        self.text(x + 1, y - 3, value)

    def draw_wire(self, x1, y1, x2, y2, color=GREEN):
        self.set_draw_color(*color)
        self.line(x1, y1, x2, y2)

    def draw_net_label(self, x, y, name):
        self.set_font('Helvetica', '', 5)
        self.set_text_color(*MAGENTA)
        self.text(x, y, name)

    def draw_gnd(self, x, y):
        self.set_draw_color(*BLACK)
        self.line(x, y, x, y + 2)
        self.line(x - 2, y + 2, x + 2, y + 2)
        self.line(x - 1, y + 3, x + 1, y + 3)

    def draw_vcc(self, x, y, net_name=""):
        self.set_draw_color(*RED)
        self.line(x, y, x, y - 2)
        self.set_font('Helvetica', 'B', 5)
        self.set_text_color(*RED)
        self.text(x - 3, y - 3, net_name)

    def draw_connector(self, ref, x, y, pins=2, label=""):
        self.set_draw_color(*MAGENTA)
        w = 8
        h = pins * 3 + 2
        self.rect(x, y, w, h)
        self.set_font('Helvetica', 'B', 5)
        self.text(x + 1, y + 4, ref)
        if label:
            self.set_font('Helvetica', '', 4)
            self.text(x + 1, y + 8, label)


def parse_schematic_sheet(filepath):
    """Parse a KiCad .kicad_sch file and extract components and wires."""
    components = []
    wires = []
    labels = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return components, wires, labels

    # Extract symbols (components)
    # Pattern: (symbol (lib_id "LIB:SYMBOL") (at X Y ANGLE) ...
    sym_pattern = r'\(symbol\s+\(lib_id\s+"([^"]+)"\)\s+\(at\s+([\d.]+)\s+([\d.]+)\s+[\d.]+\)'
    for m in re.finditer(sym_pattern, content):
        lib_id = m.group(1)
        x = float(m.group(2))
        y = float(m.group(3))
        # Extract reference and value
        ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', content[m.start():m.start()+500])
        val_match = re.search(r'\(property\s+"Value"\s+"([^"]+)"', content[m.start():m.start()+500])
        ref = ref_match.group(1) if ref_match else "?"
        val = val_match.group(1) if val_match else ""
        components.append({'lib_id': lib_id, 'ref': ref, 'value': val, 'x': x, 'y': y})

    # Extract wires
    wire_pattern = r'\(wire\s+\(pts\s+\(xy\s+([\d.]+)\s+([\d.]+)\)\s+\(xy\s+([\d.]+)\s+([\d.]+)\)\)'
    for m in re.finditer(wire_pattern, content):
        wires.append((float(m.group(1)), float(m.group(2)),
                      float(m.group(3)), float(m.group(4))))

    # Extract labels
    label_pattern = r'\(label\s+"([^"]+)"\s+\(at\s+([\d.]+)\s+([\d.]+)'
    for m in re.finditer(label_pattern, content):
        labels.append({'name': m.group(1), 'x': float(m.group(2)), 'y': float(m.group(3))})

    # Global labels
    glabel_pattern = r'\(global_label\s+"([^"]+)"\s+\(shape\s+[^)]+\)\s+\(at\s+([\d.]+)\s+([\d.]+)'
    for m in re.finditer(glabel_pattern, content):
        labels.append({'name': m.group(1), 'x': float(m.group(2)), 'y': float(m.group(3))})

    return components, wires, labels


def render_schematic_to_pdf(sheet_file, pdf_file, title):
    """Render a KiCad schematic sheet to PDF."""
    components, wires, labels = parse_schematic_sheet(sheet_file)

    pdf = KiCadSchematicPDF(title)
    pdf.add_page()
    pdf.draw_title_block(title, f"File: {os.path.basename(sheet_file)}")

    if not components and not wires:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(*GRAY)
        pdf.text(50, 50, "Schematic sheet (open in KiCad for full rendering)")
        pdf.text(50, 60, f"Components: {len(components)}, Wires: {len(wires)}")
    else:
        # Scale factor (KiCad uses mm, PDF uses mm)
        scale = 0.35
        offset_x = 15
        offset_y = 20

        # Draw wires first
        for x1, y1, x2, y2 in wires:
            pdf.draw_wire(x1 * scale + offset_x, y1 * scale + offset_y,
                         x2 * scale + offset_x, y2 * scale + offset_y)

        # Draw components
        for comp in components:
            x = comp['x'] * scale + offset_x
            y = comp['y'] * scale + offset_y
            lib = comp['lib_id'].split(':')[-1] if ':' in comp['lib_id'] else comp['lib_id']

            if 'R' in comp['ref'] and comp['ref'][0] == 'R':
                pdf.draw_resistor(x, y, comp['value'])
            elif 'C' in comp['ref'] and comp['ref'][0] == 'C':
                pdf.draw_capacitor(x, y, comp['value'])
            elif any(ic in lib.upper() for ic in ['ADC', 'FPGA', 'TPS', 'ISL', 'LMX', 'LMK', 'INA', 'TRF']):
                pdf.draw_ic(comp['ref'], comp['value'], x - 10, y - 15, 30, 30)
            elif 'J' in comp['ref']:
                pdf.draw_connector(comp['ref'], x, y, 4, comp['value'])
            elif 'L' in comp['ref'] and comp['ref'][0] == 'L':
                pdf.draw_resistor(x, y, comp['value'])
            elif 'FB' in comp['ref']:
                pdf.draw_resistor(x, y, comp['value'])
            else:
                pdf.draw_component(comp['ref'], comp['value'], x - 5, y - 3)

        # Draw labels
        for lbl in labels:
            x = lbl['x'] * scale + offset_x
            y = lbl['y'] * scale + offset_y
            pdf.draw_net_label(x, y, lbl['name'])

    # Info box
    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(*GRAY)
    pdf.text(15, 270, f"Sheet: {os.path.basename(sheet_file)} | "
             f"Components: {len(components)} | Wires: {len(wires)} | "
             f"Labels: {len(labels)} | Generated from KiCad s-expression")

    pdf.output(pdf_file)
    return len(components)


def parse_pcb_layers(filepath):
    """Parse KiCad PCB file and extract layer info."""
    layers = {}
    footprints = []
    tracks = []
    zones = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return layers, footprints, tracks, zones

    # Parse layers
    layer_pattern = r'\((\d+)\s+"([^"]+)"\s+(signal|power|user)\)'
    for m in re.finditer(layer_pattern, content):
        layers[int(m.group(1))] = {'name': m.group(2), 'type': m.group(3)}

    # Parse footprints
    fp_pattern = r'\(footprint\s+"([^"]+)"\s+\(layer\s+"([^"]+)"\)\s+\(at\s+([\d.-]+)\s+([\d.-]+)'
    for m in re.finditer(fp_pattern, content):
        footprints.append({
            'footprint': m.group(1),
            'layer': m.group(2),
            'x': float(m.group(3)),
            'y': float(m.group(4))
        })

    # Parse tracks
    track_pattern = r'\(segment\s+\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)\s+\(width\s+([\d.]+)\)\s+\(layer\s+"([^"]+)"\)'
    for m in re.finditer(track_pattern, content):
        tracks.append({
            'x1': float(m.group(1)), 'y1': float(m.group(2)),
            'x2': float(m.group(3)), 'y2': float(m.group(4)),
            'width': float(m.group(5)),
            'layer': m.group(6)
        })

    # Parse zones
    zone_pattern = r'\(zone\s+\(net\s+(\d+)\)\s+\(net_name\s+"([^"]+)"\)\s+\(layer\s+"([^"]+)"\)'
    for m in re.finditer(zone_pattern, content):
        zones.append({'net': int(m.group(1)), 'name': m.group(2), 'layer': m.group(3)})

    return layers, footprints, tracks, zones


def render_pcb_layer_pdf(pcb_file, pdf_file, layer_name, layer_num, color):
    """Render a single PCB layer to PDF."""
    layers, footprints, tracks, zones = parse_pcb_layers(pcb_file)

    pdf = FPDF(orientation='L', unit='mm', format='A3')
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # Title
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 8, f"X-Band Digital Module - PCB Layer: {layer_name}", 0, 1, 'L')
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 5, f"Layer {layer_num} | 200mm x 200mm | 12-layer Megtron6 stackup", 0, 1, 'L')
    pdf.ln(2)

    # Board outline
    scale = 1.35  # Scale 200mm to fit A3 landscape
    ox, oy = 15, 15

    # Draw board outline
    pdf.set_draw_color(*BLACK)
    pdf.set_line_width(0.5)
    pdf.rect(ox, oy, 200 * scale, 200 * scale)

    # Draw mounting holes
    for mx, my in [(10, 10), (10, 190), (190, 10), (190, 190)]:
        pdf.set_draw_color(*GRAY)
        pdf.set_line_width(0.3)
        cx = mx * scale + ox
        cy = my * scale + oy
        pdf.ellipse(cx - 2, cy - 2, 4, 4)

    # Draw tracks on this layer
    layer_tracks = [t for t in tracks if t['layer'] == layer_name]
    if layer_tracks:
        pdf.set_draw_color(*color)
        for t in layer_tracks[:500]:  # Limit for performance
            w = max(0.1, t['width'] * 0.3)
            pdf.set_line_width(w)
            pdf.line(t['x1'] * scale + ox, t['y1'] * scale + oy,
                    t['x2'] * scale + ox, t['y2'] * scale + oy)

    # Draw footprints on this layer
    layer_fps = [f for f in footprints if f['layer'] == layer_name or
                 (f['layer'] == 'F.Cu' and layer_name in ('F.Cu', 'F.SilkS', 'F.Mask')) or
                 (f['layer'] == 'B.Cu' and layer_name in ('B.Cu', 'B.SilkS', 'B.Mask'))]
    for fp in layer_fps[:200]:
        x = fp['x'] * scale + ox
        y = fp['y'] * scale + oy
        pdf.set_draw_color(*color)
        pdf.set_line_width(0.15)
        pdf.rect(x - 3, y - 3, 6, 6)

    # Legend
    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(*GRAY)
    pdf.text(15, 280, f"Layer: {layer_name} | Tracks: {len(layer_tracks)} | "
             f"Footprints: {len(layer_fps)} | Generated from KiCad PCB file")

    pdf.output(pdf_file)
    return len(layer_tracks)


def generate_3d_step_pdf(step_file, pdf_file):
    """Generate a 3D visualization PDF from STEP file."""
    pdf = FPDF(orientation='L', unit='mm', format='A3')
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # Title
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 8, "X-Band Digital Module - 3D Mechanical Model", 0, 1, 'L')
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 5, "STEP AP214 Format | Open in FreeCAD/CadQuery for 3D rendering", 0, 1, 'L')
    pdf.ln(5)

    # Read STEP file and extract dimensions
    try:
        with open(step_file, 'r', encoding='utf-8', errors='replace') as f:
            step_content = f.read()

        # Count entities
        entity_count = step_content.count('#')
        product_count = step_content.count('PRODUCT(')
        face_count = step_content.count('ADVANCED_FACE')
        edge_count = step_content.count('EDGE_CURVE')
        vertex_count = step_content.count('VERTEX_POINT')

        # Draw 3D isometric view (simplified representation)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*BLACK)
        pdf.text(20, 35, "Isometric View (Simplified)")

        # PCB base plate (isometric projection)
        cx, cy = 150, 160
        s = 0.8  # scale

        # PCB plate
        pdf.set_draw_color(*GREEN)
        pdf.set_fill_color(200, 230, 200)
        pdf.set_line_width(0.5)
        # Top face
        pts = [(0, 0, 200*s, 0, 200*s, 200*s, 0, 200*s)]  # x1,y1,x2,y2,x3,y3,x4,y4
        # Draw as parallelogram (isometric)
        iso_pts = []
        for px, py in [(0, 0), (200, 0), (200, 200), (0, 200)]:
            ix = cx + (px - py) * 0.5 * s
            iy = cy + (px + py) * 0.3 * s - 40
            iso_pts.append((ix, iy))
        # Fill
        pdf.set_fill_color(180, 220, 180)
        pdf.polygon(iso_pts, 'F')
        pdf.polygon(iso_pts, 'D')

        # Thickness
        pdf.set_fill_color(140, 180, 140)
        side_pts = [iso_pts[0], iso_pts[1],
                   (iso_pts[1][0], iso_pts[1][1] + 3),
                   (iso_pts[0][0], iso_pts[0][1] + 3)]
        pdf.polygon(side_pts, 'F')
        pdf.polygon(side_pts, 'D')

        side_pts2 = [iso_pts[1], iso_pts[2],
                    (iso_pts[2][0], iso_pts[2][1] + 3),
                    (iso_pts[1][0], iso_pts[1][1] + 3)]
        pdf.polygon(side_pts2, 'F')
        pdf.polygon(side_pts2, 'D')

        # Shielding box (wireframe)
        pdf.set_draw_color(*GRAY)
        pdf.set_line_width(0.3)
        shield_pts = []
        for px, py in [(-3, -3), (203, -3), (203, 203), (-3, 203)]:
            ix = cx + (px - py) * 0.5 * s
            iy = cy + (px + py) * 0.3 * s - 55
            shield_pts.append((ix, iy))
        pdf.polygon(shield_pts, 'D')

        # Top of shield
        shield_top = []
        for px, py in [(-3, -3), (203, -3), (203, 203), (-3, 203)]:
            ix = cx + (px - py) * 0.5 * s
            iy = cy + (px + py) * 0.3 * s - 85
            shield_top.append((ix, iy))
        pdf.polygon(shield_top, 'D')
        # Connect corners
        for i in range(4):
            pdf.line(shield_pts[i][0], shield_pts[i][1],
                    shield_top[i][0], shield_top[i][1])

        # FPGA chip (center)
        pdf.set_fill_color(100, 100, 200)
        fpga_pts = []
        for px, py in [(80, 80), (130, 80), (130, 130), (80, 130)]:
            ix = cx + (px - py) * 0.5 * s
            iy = cy + (px + py) * 0.3 * s - 42
            fpga_pts.append((ix, iy))
        pdf.polygon(fpga_pts, 'FD')

        # Connectors on right edge
        pdf.set_fill_color(80, 80, 80)
        for cy_pos in [80, 100, 120, 140]:
            conn_pts = []
            for px, py in [(195, cy_pos-5), (205, cy_pos-5), (205, cy_pos+5), (195, cy_pos+5)]:
                ix = cx + (px - py) * 0.5 * s
                iy = cy + (px + py) * 0.3 * s - 42
                conn_pts.append((ix, iy))
            pdf.polygon(conn_pts, 'FD')

        # Mounting holes
        pdf.set_draw_color(*BLACK)
        for mx, my in [(10, 10), (10, 190), (190, 10), (190, 190)]:
            ix = cx + (mx - my) * 0.5 * s
            iy = cy + (mx + my) * 0.3 * s - 40
            pdf.ellipse(ix - 1.5, iy - 1.5, 3, 3)

        # Dimension annotations
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(*BLACK)
        pdf.text(20, 50, f"PCB: 200 x 200 x 2 mm")
        pdf.text(20, 56, f"Shield: 206 x 206 x 15 mm")
        pdf.text(20, 62, f"Standoffs: M3 x 6 mm (4x)")
        pdf.text(20, 68, f"Total height: ~28 mm")

        # STEP file info
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*BLUE)
        pdf.cell(0, 6, "STEP File Information", 0, 1, 'L')
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(*BLACK)
        info = [
            f"File: {os.path.basename(step_file)}",
            f"Size: {os.path.getsize(step_file):,} bytes",
            f"Entities: {entity_count:,}",
            f"Products: {product_count}",
            f"Faces: {face_count}",
            f"Edges: {edge_count}",
            f"Vertices: {vertex_count}",
            f"Format: ISO-10303-21 AP214",
        ]
        for line in info:
            pdf.cell(0, 5, line, 0, 1, 'L')

        # Component list
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*BLUE)
        pdf.cell(0, 6, "Modeled Components", 0, 1, 'L')
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(*BLACK)
        components = [
            "PCB Base Plate: 200 x 200 x 2 mm (FR4)",
            "Shielding Box: 206 x 206 x 15 mm (Aluminum)",
            "Standoffs: M3 x 6 mm (4x Aluminum)",
            "SMA Connectors: 6mm dia x 12mm (4x Gold)",
            "SpaceWire Connectors: 15 x 10 x 8 mm (2x)",
            "Power Connector: 12 x 8 x 6 mm (1x)",
            "JTAG Connector: 12 x 5 x 4 mm (1x)",
            "FPGA XQRVC1902: 35 x 35 x 3 mm",
            "ADC12DJ5200-SP: 10 x 10 x 2 mm",
            "Heatsink: 40 x 40 x 2 mm (under PCB)",
        ]
        for comp in components:
            pdf.cell(0, 5, f"  - {comp}", 0, 1, 'L')

    except Exception as e:
        pdf.set_font('Helvetica', '', 10)
        pdf.text(20, 40, f"Error reading STEP file: {e}")

    pdf.output(pdf_file)


def main():
    os.makedirs(OUTPUT, exist_ok=True)
    print("Generating schematic PDFs...")

    # Get all schematic sheets
    sheets = sorted([f for f in os.listdir(SCHEMATIC_DIR)
                    if f.startswith('Sheet') and f.endswith('.kicad_sch')])

    for sheet_file in sheets:
        sheet_path = os.path.join(SCHEMATIC_DIR, sheet_file)
        pdf_name = sheet_file.replace('.kicad_sch', '.pdf')
        pdf_path = os.path.join(OUTPUT, pdf_name)
        title = sheet_file.replace('.kicad_sch', '').replace('_', ' ')

        try:
            count = render_schematic_to_pdf(sheet_path, pdf_path, title)
            print(f"  -> {pdf_name} ({os.path.getsize(pdf_path):,} bytes, {count} components)")
        except Exception as e:
            print(f"  ERROR {sheet_file}: {e}")

    # Main schematic
    main_sch = os.path.join(SCHEMATIC_DIR, "XBandDigitalModule.kicad_sch")
    if os.path.exists(main_sch):
        pdf_path = os.path.join(OUTPUT, "XBand_Schematic_Main.pdf")
        try:
            render_schematic_to_pdf(main_sch, pdf_path, "Main Schematic - Hierarchical Sheets")
            print(f"  -> XBand_Schematic_Main.pdf ({os.path.getsize(pdf_path):,} bytes)")
        except Exception as e:
            print(f"  ERROR main schematic: {e}")

    print("\nGenerating PCB layer PDFs...")
    # Generate PDFs for key layers
    layer_configs = [
        ("F.Cu", 0, RED),
        ("B.Cu", 31, BLUE),
        ("In1.Cu", 1, (180, 0, 0)),
        ("In2.Cu", 2, (0, 100, 0)),
        ("In4.Cu", 4, (0, 0, 150)),
        ("In7.Cu", 7, (100, 0, 100)),
        ("F.SilkS", 37, (200, 200, 0)),
        ("B.SilkS", 36, (0, 180, 180)),
        ("Edge.Cuts", 44, BLACK),
    ]

    for layer_name, layer_num, color in layer_configs:
        pdf_name = f"XBand_PCB_{layer_name.replace('.', '_')}.pdf"
        pdf_path = os.path.join(OUTPUT, pdf_name)
        try:
            count = render_pcb_layer_pdf(PCB_PATH, pdf_path, layer_name, layer_num, color)
            print(f"  -> {pdf_name} ({os.path.getsize(pdf_path):,} bytes, {count} tracks)")
        except Exception as e:
            print(f"  ERROR {layer_name}: {e}")

    # 3D STEP PDF
    print("\nGenerating 3D mechanical PDF...")
    step_file = os.path.join(BASE, "mechanical", "XBandDigitalModule_20x20_Mechanical.step")
    pdf_3d = os.path.join(OUTPUT, "XBand_Mechanical_3D.pdf")
    try:
        generate_3d_step_pdf(step_file, pdf_3d)
        print(f"  -> XBand_Mechanical_3D.pdf ({os.path.getsize(pdf_3d):,} bytes)")
    except Exception as e:
        print(f"  ERROR 3D PDF: {e}")

    print("\nDone!")


if __name__ == '__main__':
    main()
