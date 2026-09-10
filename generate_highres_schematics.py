#!/usr/bin/env python3
"""Generate schematic PDFs using Pillow for high-res rendering, then embed in PDF."""
import os, re, glob
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

BASE = "/opt/cryptobot/XBandDigitalModule_20x20"
SCH = os.path.join(BASE, "schematic")
EXPORTS = os.path.join(BASE, "exports")
os.makedirs(EXPORTS, exist_ok=True)

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 70, 180)
RED = (200, 0, 0)
GREEN = (0, 140, 0)
ORANGE = (200, 120, 0)
CYAN = (0, 150, 180)
MAGENTA = (180, 0, 180)
GRAY = (120, 120, 120)
LIGHT_BLUE = (220, 235, 255)
LIGHT_YELLOW = (255, 255, 240)
WHITE = (255, 255, 255)
DARK_GREEN = (0, 100, 0)


def parse_sheet(filepath):
    """Parse KiCad schematic and return components, wires, labels."""
    with open(filepath, 'r') as f:
        content = f.read()

    components = []
    pattern = r'\(symbol \(lib_id "([^"]+)" \(at (-?[\d.]+) (-?[\d.]+) (-?[\d.]+)\)'
    for m in re.finditer(pattern, content):
        lib_id, x, y, angle = m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4))
        block = content[m.start():min(m.start()+800, len(content))]
        ref_m = re.search(r'\(property "Reference" "([^"]+)"', block)
        val_m = re.search(r'\(property "Value" "([^"]+)"', block)
        ref = ref_m.group(1) if ref_m else "?"
        val = val_m.group(1) if val_m else ""
        components.append({'lib': lib_id.split(':')[-1] if ':' in lib_id else lib_id,
                          'ref': ref, 'value': val, 'x': x, 'y': y, 'angle': angle})

    wires = []
    wm = r'\(wire \(pts \(xy (-?[\d.]+) (-?[\d.]+)\) \(xy (-?[\d.]+) (-?[\d.]+)\)\)'
    for m in re.finditer(wm, content):
        wires.append((float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))))

    labels = []
    for m in re.finditer(r'\(label "([^"]+)" \(at (-?[\d.]+) (-?[\d.]+)', content):
        labels.append({'name': m.group(1), 'x': float(m.group(2)), 'y': float(m.group(3)), 'type': 'local'})
    for m in re.finditer(r'\(global_label "([^"]+)" \(shape [^)]+\) \(at (-?[\d.]+) (-?[\d.]+)', content):
        labels.append({'name': m.group(1), 'x': float(m.group(2)), 'y': float(m.group(3)), 'type': 'global'})

    return components, wires, labels


def render_sheet_image(components, wires, labels, title, subtitle="", dpi=200):
    """Render schematic to PIL Image."""
    # A3 landscape at dpi
    W_px = int(420 / 25.4 * dpi)  # 420mm wide
    H_px = int(297 / 25.4 * dpi)  # 297mm tall
    scale_px = dpi / 25.4  # pixels per mm

    img = Image.new('RGB', (W_px, H_px), WHITE)
    draw = ImageDraw.Draw(img)

    # Try to load fonts
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(14 * scale_px / 2.54))
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(10 * scale_px / 2.54))
        font_ref = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(8 * scale_px / 2.54))
        font_val = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(6 * scale_px / 2.54))
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(7 * scale_px / 2.54))
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(5 * scale_px / 2.54))
    except:
        font_title = font_sub = font_ref = font_val = font_label = font_small = ImageFont.load_default()

    # Title block
    draw.rectangle([10, 10, W_px - 10, H_px - 10], outline=BLUE, width=max(2, int(scale_px * 0.3)))
    draw.rectangle([10, 10, W_px - 10, int(50 * scale_px / 25.4)], fill=(230, 240, 255), outline=BLUE)
    draw.text((20, int(15 * scale_px / 25.4)), f"X-Band Digital Module - {title}", fill=BLUE, font=font_title)
    draw.text((20, int(30 * scale_px / 25.4)), subtitle, fill=GRAY, font=font_sub)

    if not components and not wires:
        draw.text((int(50 * scale_px / 25.4), int(80 * scale_px / 25.4)), "No components in this sheet", fill=GRAY, font=font_sub)
        return img

    # Calculate bounds and scaling
    if components:
        min_x = min(c['x'] for c in components) - 25
        max_x = max(c['x'] for c in components) + 25
        min_y = min(c['y'] for c in components) - 25
        max_y = max(c['y'] for c in components) + 25
    else:
        min_x, max_x, min_y, max_y = 0, 200, 0, 200

    range_x = max_x - min_x
    range_y = max_y - min_y
    draw_area_w = W_px - int(40 * scale_px / 25.4)
    draw_area_h = H_px - int(70 * scale_px / 25.4)
    sx = draw_area_w / (range_x * scale_px / 25.4) if range_x > 0 else 1
    sy = draw_area_h / (range_y * scale_px / 25.4) if range_y > 0 else 1
    s = min(sx, sy, 4.0)
    ox = int(20 * scale_px / 25.4) - min_x * (scale_px / 25.4) * s
    oy = int(55 * scale_px / 25.4) - min_y * (scale_px / 25.4) * s

    def to_px(kx, ky):
        px = kx * (scale_px / 25.4) * s + ox
        py = ky * (scale_px / 25.4) * s + oy
        return int(px), int(py)

    lw = max(1, int(0.3 * scale_px / 25.4 * s))

    # Draw wires
    for x1, y1, x2, y2 in wires:
        p1 = to_px(x1, y1)
        p2 = to_px(x2, y2)
        draw.line([p1, p2], fill=GREEN, width=lw)

    # Draw components
    for comp in components:
        px, py = to_px(comp['x'], comp['y'])
        lib = comp['lib']
        ref = comp['ref']
        val = comp['value']

        # Determine component type and draw accordingly
        if any(ic in lib for ic in ['TPS7H', 'ISL7', 'ADC', 'LMX', 'LMK', 'INA', 'TRF', 'XQRVC']):
            # IC: draw rectangle with pins
            iw = int(20 * scale_px / 25.4 * s)
            ih = int(25 * scale_px / 25.4 * s)
            draw.rectangle([px - iw//2, py - ih//2, px + iw//2, py + ih//2],
                          fill=LIGHT_BLUE, outline=BLUE, width=max(1, lw))
            # Draw pin stubs
            pin_len = int(3 * scale_px / 25.4 * s)
            for i in range(5):
                pin_y = py - ih//2 + ih * (i + 1) // 6
                draw.line([px - iw//2 - pin_len, pin_y, px - iw//2, pin_y], fill=RED, width=max(1, lw-1))
                draw.line([px + iw//2, pin_y, px + iw//2 + pin_len, pin_y], fill=RED, width=max(1, lw-1))
            # Notch
            nw = int(2 * scale_px / 25.4 * s)
            draw.arc([px - nw, py - ih//2 - 1, px + nw, py - ih//2 + 3], 0, 180, fill=BLUE, width=max(1, lw))
            # Labels
            draw.text((px - iw//2 + int(2 * scale_px / 25.4 * s), py - ih//4), ref, fill=BLACK, font=font_ref)
            draw.text((px - iw//2 + int(2 * scale_px / 25.4 * s), py), val[:18], fill=BLACK, font=font_val)

        elif 'Resistor' in lib:
            # Resistor: zigzag
            rw = int(6 * scale_px / 25.4 * s)
            rh = int(2 * scale_px / 25.4 * s)
            draw.line([px - rw, py, px - rw//2, py], fill=DARK_GREEN, width=lw)
            # Zigzag
            for i in range(4):
                x_off = px - rw//2 + rw * i // 4
                y_dir = rh if i % 2 == 0 else -rh
                draw.line([x_off, py, x_off + rw//8, py + y_dir], fill=DARK_GREEN, width=lw)
            draw.line([px + rw//2, py, px + rw, py], fill=DARK_GREEN, width=lw)
            draw.text((px - rw//2, py - rh - int(4 * scale_px / 25.4 * s)), val, fill=BLACK, font=font_val)

        elif 'Capacitor' in lib:
            # Capacitor: parallel plates
            cw = int(1.5 * scale_px / 25.4 * s)
            ch = int(3 * scale_px / 25.4 * s)
            gap = int(1 * scale_px / 25.4 * s)
            draw.line([px, py - ch - gap, px, py - gap], fill=CYAN, width=lw)
            draw.line([px - ch, py - gap, px + ch, py - gap], fill=CYAN, width=max(2, lw))
            draw.line([px - ch, py + gap, px + ch, py + gap], fill=CYAN, width=max(2, lw))
            draw.line([px, py + gap, px, py + ch + gap], fill=CYAN, width=lw)
            draw.text((px + ch + int(2 * scale_px / 25.4 * s), py - int(2 * scale_px / 25.4 * s)),
                     val, fill=BLACK, font=font_val)

        elif 'Inductor' in lib:
            # Inductor: coil shape
            lw2 = int(3 * scale_px / 25.4 * s)
            draw.line([px - lw2, py, px - lw2//2, py], fill=DARK_GREEN, width=lw)
            for i in range(3):
                cx = px - lw2//2 + lw2 * i // 3
                draw.arc([cx, py - lw2//4, cx + lw2//3, py + lw2//4], 0, 180, fill=DARK_GREEN, width=lw)
            draw.line([px + lw2//2, py, px + lw2, py], fill=DARK_GREEN, width=lw)
            draw.text((px - lw2//2, py - lw2//2 - int(4 * scale_px / 25.4 * s)), val, fill=BLACK, font=font_val)

        elif ref.startswith('J'):
            # Connector
            jw = int(8 * scale_px / 25.4 * s)
            jh = int(12 * scale_px / 25.4 * s)
            draw.rectangle([px - jw//2, py - jh//2, px + jw//2, py + jh//2],
                          fill=LIGHT_YELLOW, outline=MAGENTA, width=max(1, lw))
            draw.text((px - jw//2 + int(1 * scale_px / 25.4 * s), py - jh//2 + int(2 * scale_px / 25.4 * s)),
                     ref, fill=BLACK, font=font_ref)
            draw.text((px - jw//2 + int(1 * scale_px / 25.4 * s), py), val[:12], fill=BLACK, font=font_val)

        elif ref.startswith('Y'):
            # Crystal
            yw = int(5 * scale_px / 25.4 * s)
            yh = int(3 * scale_px / 25.4 * s)
            draw.rectangle([px - yw//2, py - yh//2, px + yw//2, py + yh//2],
                          fill=LIGHT_YELLOW, outline=ORANGE, width=max(1, lw))
            draw.line([px - yw//2 - int(2*scale_px/25.4*s), py, px - yw//2, py], fill=ORANGE, width=lw)
            draw.line([px + yw//2, py, px + yw//2 + int(2*scale_px/25.4*s), py], fill=ORANGE, width=lw)
            draw.text((px - yw//2, py - yh//2 - int(4 * scale_px / 25.4 * s)), val, fill=BLACK, font=font_val)

        elif ref.startswith('FB'):
            # Ferrite bead
            fbw = int(4 * scale_px / 25.4 * s)
            draw.line([px - fbw, py, px + fbw, py], fill=DARK_GREEN, width=max(2, lw))
            draw.text((px - fbw//2, py - int(4 * scale_px / 25.4 * s)), val[:12], fill=BLACK, font=font_val)

        elif ref.startswith('TP'):
            # Test point
            tpr = int(1.5 * scale_px / 25.4 * s)
            draw.ellipse([px - tpr, py - tpr, px + tpr, py + tpr], outline=RED, width=max(1, lw))
            draw.text((px + tpr + int(1 * scale_px / 25.4 * s), py - int(2 * scale_px / 25.4 * s)),
                     val[:15], fill=RED, font=font_val)

        else:
            # Generic
            gw = int(6 * scale_px / 25.4 * s)
            gh = int(4 * scale_px / 25.4 * s)
            draw.rectangle([px - gw//2, py - gh//2, px + gw//2, py + gh//2],
                          fill=LIGHT_YELLOW, outline=GRAY, width=max(1, lw))
            draw.text((px - gw//2 + int(1*scale_px/25.4*s), py - gh//2 + int(1*scale_px/25.4*s)),
                     ref, fill=BLACK, font=font_ref)

    # Draw labels
    for lbl in labels:
        px, py = to_px(lbl['x'], lbl['y'])
        color = MAGENTA if lbl['type'] == 'global' else (0, 100, 200)
        # Draw label background
        bbox = font_label.getbbox(lbl['name'])
        tw = bbox[2] - bbox[0] if bbox else len(lbl['name']) * int(5 * scale_px / 25.4 * s)
        th = bbox[3] - bbox[1] if bbox else int(6 * scale_px / 25.4 * s)
        draw.rectangle([px - 1, py - th - 1, px + tw + 2, py + 2], fill=WHITE)
        draw.text((px, py - th), lbl['name'], fill=color, font=font_label)

    # Info footer
    info = f"Components: {len(components)} | Wires: {len(wires)} | Labels: {len(labels)}"
    draw.text((int(15 * scale_px / 25.4), H_px - int(15 * scale_px / 25.4)), info, fill=GRAY, font=font_small)

    return img


def img_to_pdf(img, pdf_path, title=""):
    """Convert PIL Image to PDF using fpdf2."""
    # Save image as temp PNG
    tmp_png = pdf_path.replace('.pdf', '_tmp.png')
    img.save(tmp_png, 'PNG', dpi=(200, 200))

    pdf = FPDF(orientation='L', unit='mm', format='A3')
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    pdf.image(tmp_png, x=0, y=0, w=420, h=297)
    pdf.output(pdf_path)
    os.remove(tmp_png)


def generate_all():
    """Generate all schematic PDFs."""
    # Get sheet files in order
    sheets = sorted(glob.glob(os.path.join(SCH, "Sheet*.kicad_sch")))
    # Also include main sheet
    main_sheet = os.path.join(SCH, "XBandDigitalModule.kicad_sch")
    if os.path.exists(main_sheet):
        sheets.append(main_sheet)

    print(f"Found {len(sheets)} schematic sheets")

    for sheet_path in sheets:
        basename = os.path.basename(sheet_path).replace('.kicad_sch', '')
        pdf_path = os.path.join(EXPORTS, f"{basename}.pdf")

        print(f"  Rendering {basename}...")
        components, wires, labels = parse_sheet(sheet_path)

        # Get title from file
        with open(sheet_path) as f:
            content = f.read()
        title_m = re.search(r'\(comment 1 "([^"]+)"', content)
        title = title_m.group(1) if title_m else basename
        sub_m = re.search(r'\(comment 2 "([^"]+)"', content)
        subtitle = sub_m.group(1) if sub_m else ""

        img = render_sheet_image(components, wires, labels, title, subtitle)
        img_to_pdf(img, pdf_path)
        sz = os.path.getsize(pdf_path)
        print(f"    -> {basename}.pdf ({sz:,} bytes, {len(components)} comp, {len(wires)} wires)")

    # Now merge all into unified schematic PDF
    print("\n  Creating unified schematic PDF...")
    cover = create_cover()
    img_to_pdf(cover, os.path.join(EXPORTS, '_cover_tmp.pdf'))

    merger_pdf = FPDF(orientation='L', unit='mm', format='A3')
    merger_pdf.set_auto_page_break(auto=False)

    # Cover page
    merger_pdf.add_page()
    cover_path = os.path.join(EXPORTS, '_cover_tmp.png')
    cover.save(cover_path, 'PNG', dpi=(200, 200))
    merger_pdf.image(cover_path, x=0, y=0, w=420, h=297)

    # Each sheet
    for sheet_path in sheets:
        basename = os.path.basename(sheet_path).replace('.kicad_sch', '')
        pdf_path = os.path.join(EXPORTS, f"{basename}.pdf")
        if os.path.exists(pdf_path):
            # Extract page from individual PDF
            tmp_png = pdf_path.replace('.pdf', '_tmp2.png')
            # Re-render for merged PDF
            components, wires, labels = parse_sheet(sheet_path)
            with open(sheet_path) as f:
                content = f.read()
            title_m = re.search(r'\(comment 1 "([^"]+)"', content)
            title = title_m.group(1) if title_m else basename
            sub_m = re.search(r'\(comment 2 "([^"]+)"', content)
            subtitle = sub_m.group(1) if sub_m else ""
            img = render_sheet_image(components, wires, labels, title, subtitle)
            img.save(tmp_png, 'PNG', dpi=(200, 200))
            merger_pdf.add_page()
            merger_pdf.image(tmp_png, x=0, y=0, w=420, h=297)
            os.remove(tmp_png)

    out_path = os.path.join(EXPORTS, 'XBand_Schematic_Complete.pdf')
    merger_pdf.output(out_path)

    # Cleanup
    cover_tmp = os.path.join(EXPORTS, '_cover_tmp.png')
    if os.path.exists(cover_tmp):
        os.remove(cover_tmp)
    cover_pdf = os.path.join(EXPORTS, '_cover_tmp.pdf')
    if os.path.exists(cover_pdf):
        os.remove(cover_pdf)

    sz = os.path.getsize(out_path)
    print(f"\n  Unified PDF: {out_path} ({sz:,} bytes)")


def create_cover():
    """Create cover page image."""
    W_px = int(420 / 25.4 * 200)
    H_px = int(297 / 25.4 * 200)
    s = 200 / 25.4

    img = Image.new('RGB', (W_px, H_px), (0, 30, 60))
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(36 * s / 25.4))
        font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(18 * s / 25.4))
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(12 * s / 25.4))
        font_xs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(9 * s / 25.4))
    except:
        font_big = font_med = font_sm = font_xs = ImageFont.load_default()

    cy = int(60 * s / 25.4)
    draw.text((W_px//2 - int(120*s/25.4), cy), "X-BAND DIGITAL MODULE", fill=WHITE, font=font_big)
    cy += int(30 * s / 25.4)
    draw.text((W_px//2 - int(80*s/25.4), cy), "Complete Schematic Package", fill=(180, 210, 255), font=font_med)
    cy += int(20 * s / 25.4)
    draw.text((W_px//2 - int(60*s/25.4), cy), "20 x 20 cm Space-Grade PCB", fill=(180, 210, 255), font=font_med)

    cy += int(40 * s / 25.4)
    specs = [
        "ADC: ADC12DJ5200-SP (10.4 GSPS, 12-bit, Rad-Hard)",
        "FPGA: XQRVC1902 (Rad-Hard, 1760-pin BGA)",
        "Clock: LMX2615-SP + LMK04832-SP (45fs jitter)",
        "Power: 6 rails, TPS7H5002-SP buck controller",
        "Output: SpaceWire 2x 100 Mbps",
        "Stackup: 12-layer Megtron6",
    ]
    for spec in specs:
        draw.text((W_px//2 - int(80*s/25.4), cy), spec, fill=(180, 210, 255), font=font_sm)
        cy += int(14 * s / 25.4)

    cy += int(20 * s / 25.4)
    draw.line([(W_px//2 - int(100*s/25.4), cy), (W_px//2 + int(100*s/25.4), cy)], fill=(100, 150, 255), width=max(1, int(0.5*s/25.4)))
    cy += int(15 * s / 25.4)

    sheets = [
        "01 - Title Block          07 - Buck 1.0V Core       13 - Sequencer",
        "02 - RF Input             08 - Buck 1.8V Aux        14 - Connectors",
        "03 - ADC12DJ5200-SP       09 - Buck 3.3V I/O        15 - Test Points",
        "04 - FPGA XQRVC1902       10 - LDO 1.0V Analog      16 - Decoupling",
        "05 - Clock Tree           11 - LDO 1.8V Digital     17 - Power Tree",
        "06 - Power Input          12 - LDO 2.5V Clock",
    ]
    for line in sheets:
        draw.text((W_px//2 - int(100*s/25.4), cy), line, fill=(150, 170, 200), font=font_xs)
        cy += int(12 * s / 25.4)

    cy += int(15 * s / 25.4)
    draw.text((W_px//2 - int(40*s/25.4), cy), "Revision 1.0 | 2026-09-10", fill=(255, 200, 100), font=font_sm)

    return img


if __name__ == '__main__':
    generate_all()
    print("\nDone!")
