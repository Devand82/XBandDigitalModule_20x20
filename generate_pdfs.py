#!/usr/bin/env python3
"""Generate PDFs from markdown documentation for X-Band Digital Module."""
import os
import re
from fpdf import FPDF

BASE = "/opt/cryptobot/XBandDigitalModule_20x20"
OUTPUT = os.path.join(BASE, "exports")

class DocPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'X-Band Digital Module 20x20cm - Space-Grade RF Acquisition', 0, 0, 'L')
        self.cell(0, 8, 'Rev 1.0', 0, 1, 'R')
        self.line(10, 15, 200, 15)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 12, sanitize(title), 0, 1, 'L')
        self.set_draw_color(0, 51, 102)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(0, 80, 140)
        self.cell(0, 10, sanitize(title), 0, 1, 'L')
        self.ln(2)

    def subsection_title(self, title):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(60, 60, 60)
        self.cell(0, 8, sanitize(title), 0, 1, 'L')
        self.ln(1)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, sanitize(text))
        self.ln(2)

    def code_block(self, text):
        self.set_font('Courier', '', 8)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 4, sanitize(text), 1, 'L', True)
        self.ln(2)

    def table_row(self, cells, widths, bold=False, fill=False):
        style = 'B' if bold else ''
        self.set_font('Helvetica', style, 7)
        if fill:
            self.set_fill_color(220, 230, 245)
        h = 5
        try:
            for i, (cell, w) in enumerate(zip(cells, widths)):
                txt = sanitize(str(cell))
                # Truncate to fit cell width
                max_chars = max(3, int(w / 1.6))
                if len(txt) > max_chars:
                    txt = txt[:max_chars-1] + '~'
                self.cell(w, h, txt, 1, 0, 'L', fill)
            self.ln()
        except Exception:
            # Fallback: write as multi_cell
            for i, (cell, w) in enumerate(zip(cells, widths)):
                txt = sanitize(str(cell))[:20]
                self.cell(w, h, txt, 1, 0, 'L', fill)
            self.ln()


def sanitize(text):
    """Replace Unicode chars with ASCII equivalents for Helvetica font."""
    replacements = {
        '\u2014': '--', '\u2013': '-', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2022': '*', '\u2192': '->',
        '\u2190': '<-', '\u2265': '>=', '\u2264': '<=', '\u2260': '!=',
        '\u2500': '-', '\u2502': '|', '\u250c': '+', '\u2510': '+',
        '\u2514': '+', '\u2518': '+', '\u251c': '+', '\u2524': '+',
        '\u2534': '+', '\u252c': '+', '\u253c': '+',
        '\u2714': '[OK]', '\u2716': '[X]', '\u2713': '[OK]',
        '\u2794': '->', '\u279c': '~>', '\u27a1': '->',
        '\u25cf': '*', '\u25cb': 'o', '\u25a0': '#', '\u25a1': '#',
        '\u2605': '*', '\u2606': 'o', '\u2610': '[ ]', '\u2611': '[x]',
        '\u2612': '[x]', '\u2026': '...', '\u00b0': ' deg',
        '\u00d7': 'x', '\u00f7': '/',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Remove any remaining non-latin1 chars
    result = []
    for ch in text:
        if ord(ch) < 256:
            result.append(ch)
        else:
            result.append('?')
    return ''.join(result)


def md_to_pdf(md_path, pdf_path, title):
    """Convert a markdown file to PDF using a robust approach."""
    try:
        with open(md_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        content = sanitize(content)
    except Exception as e:
        print(f"  ERROR reading {md_path}: {e}")
        return False

    pdf = DocPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title
    pdf.chapter_title(title)

    lines = content.split('\n')
    in_code = False
    code_buf = []

    for line in lines:
        stripped = line.strip()

        # Code blocks
        if stripped.startswith('```'):
            if in_code:
                try:
                    code_text = '\n'.join(code_buf[:50])  # limit code block size
                    pdf.set_font('Courier', '', 7)
                    pdf.set_fill_color(240, 240, 240)
                    pdf.multi_cell(0, 3.5, code_text, 1, 'L', True)
                    pdf.ln(2)
                except Exception:
                    pass
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_buf.append(line[:200])  # limit line length
            continue

        # Empty line
        if not stripped:
            pdf.ln(2)
            continue

        # Headers
        if stripped.startswith('# '):
            pdf.chapter_title(stripped[2:])
            continue
        if stripped.startswith('## '):
            pdf.section_title(stripped[3:])
            continue
        if stripped.startswith('### '):
            pdf.subsection_title(stripped[4:])
            continue

        # Table rows - simplified
        if '|' in stripped and stripped.startswith('|'):
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if all(set(c) <= set('- :') for c in cells):
                continue
            try:
                w = 190 / max(len(cells), 1)
                pdf.set_font('Courier', '', 6)
                row_text = ' | '.join(sanitize(c)[:15] for c in cells)
                pdf.cell(190, 4, row_text, 1, 1, 'L')
            except Exception:
                pass
            continue

        # Lists
        if stripped.startswith('- ') or stripped.startswith('* '):
            try:
                pdf.set_font('Helvetica', '', 9)
                txt = sanitize(stripped[2:])[:180]
                pdf.cell(4, 4, '-', 0, 0)
                pdf.multi_cell(0, 4, txt)
            except Exception:
                pass
            continue

        # Numbered lists
        m = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if m:
            try:
                pdf.set_font('Helvetica', '', 9)
                pdf.cell(6, 4, f'{m.group(1)}.', 0, 0)
                txt = sanitize(m.group(2))[:180]
                pdf.multi_cell(0, 4, txt)
            except Exception:
                pass
            continue

        # Regular text - sanitize and limit length
        try:
            text = sanitize(stripped)[:200]
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            text = re.sub(r'`(.*?)`', r'\1', text)
            pdf.set_font('Helvetica', '', 9)
            pdf.multi_cell(0, 4, text)
        except Exception:
            pass

    try:
        pdf.output(pdf_path)
        print(f"  -> {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
        return True
    except Exception as e:
        print(f"  ERROR writing {pdf_path}: {e}")
        return False


def main():
    os.makedirs(OUTPUT, exist_ok=True)

    docs = [
        ("docs/XBandDigitalModule_20x20_SystemArchitecture.md",
         "XBand_SystemArchitecture.pdf",
         "System Architecture"),
        ("docs/XBandDigitalModule_20x20_TechnicalDescription.md",
         "XBand_TechnicalDescription.pdf",
         "Technical Description"),
        ("docs/XBandDigitalModule_20x20_PowerTree.md",
         "XBand_PowerTree.pdf",
         "Power Tree"),
        ("docs/XBandDigitalModule_20x20_ClockTree.md",
         "XBand_ClockTree.pdf",
         "Clock Tree"),
        ("docs/XBandDigitalModule_20x20_RiskAssessment.md",
         "XBand_RiskAssessment.pdf",
         "Risk Assessment"),
        ("docs/XBandDigitalModule_20x20_ICD_VHDL.md",
         "XBand_ICD_VHDL.pdf",
         "ICD - VHDL Interface"),
        ("docs/XBandDigitalModule_20x20_ICD_Mechanical.md",
         "XBand_ICD_Mechanical.pdf",
         "ICD - Mechanical"),
        ("docs/XBandDigitalModule_20x20_WCA.md",
         "XBand_WCA.pdf",
         "Worst-Case Analysis"),
        ("docs/XBandDigitalModule_20x20_PSA.md",
         "XBand_PSA.pdf",
         "Power Section Analysis"),
        ("analysis/XBandDigitalModule_20x20_WCA.md",
         "XBand_WCA_Analysis.pdf",
         "Worst-Case Analysis (Detail)"),
        ("analysis/XBandDigitalModule_20x20_PSA.md",
         "XBand_PSA_Analysis.pdf",
         "Power Section Analysis (Detail)"),
        ("analysis/XBandDigitalModule_20x20_FeasibilityAnalysis.md",
         "XBand_Feasibility.pdf",
         "Feasibility Analysis"),
        ("analysis/XBandDigitalModule_20x20_ArchitectureComparison.md",
         "XBand_ArchComparison.pdf",
         "Architecture Comparison"),
        ("bom/XBandDigitalModule_20x20_BOM_Alternatives.md",
         "XBand_BOM_Alternatives.pdf",
         "BOM Alternatives"),
        ("bom/XBandDigitalModule_20x20_CostAnalysis.md",
         "XBand_CostAnalysis.pdf",
         "Cost Analysis"),
    ]

    print("Generating PDFs...")
    for rel_path, pdf_name, title in docs:
        md_path = os.path.join(BASE, rel_path)
        pdf_path = os.path.join(OUTPUT, pdf_name)
        if os.path.exists(md_path):
            try:
                md_to_pdf(md_path, pdf_path, title)
            except Exception as e:
                print(f"  ERROR {rel_path}: {e}")
        else:
            print(f"  SKIP {rel_path} (not found)")

    # Also generate a master summary PDF
    print("\nGenerating master summary...")
    pdf = DocPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Cover page
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(0, 51, 102)
    pdf.ln(40)
    pdf.cell(0, 20, 'X-BAND DIGITAL MODULE', 0, 1, 'C')
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, '20x20cm Space-Grade', 0, 1, 'C')
    pdf.cell(0, 12, 'Direct RF Sampling Acquisition System', 0, 1, 'C')
    pdf.ln(15)
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, 'Complete Design Package', 0, 1, 'C')
    pdf.cell(0, 8, 'Revision 1.0 | 2026-09-10', 0, 1, 'C')
    pdf.ln(15)

    # Table of contents
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, 'DOCUMENT PACKAGE CONTENTS', 0, 1, 'L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    toc = [
        ("1", "System Architecture", "High-level architecture and block diagrams"),
        ("2", "Technical Description", "Detailed technical specifications"),
        ("3", "Power Tree", "Power distribution network design"),
        ("4", "Clock Tree", "Clock distribution and jitter analysis"),
        ("5", "Risk Assessment", "Risk identification and mitigation"),
        ("6", "ICD - VHDL", "VHDL interface control document"),
        ("7", "ICD - Mechanical", "Mechanical interface control document"),
        ("8", "Worst-Case Analysis", "Rail-by-rail tolerance analysis"),
        ("9", "Power Section Analysis", "Power budget and thermal analysis"),
        ("10", "Feasibility Analysis", "Technical feasibility assessment"),
        ("11", "Architecture Comparison", "Architecture trade study"),
        ("12", "BOM Alternatives", "Component alternatives analysis"),
        ("13", "Cost Analysis", "Cost breakdown and projections"),
    ]

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(30, 30, 30)
    for num, name, desc in toc:
        pdf.cell(10, 7, num + '.', 0, 0, 'R')
        pdf.cell(60, 7, '  ' + name, 0, 0, 'L')
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 7, ' - ' + desc, 0, 1, 'L')
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(30, 30, 30)

    pdf.ln(10)

    # Specifications summary
    pdf.section_title('KEY SPECIFICATIONS')
    specs = [
        ("Architecture", "Direct RF Sampling"),
        ("ADC", "ADC12DJ5200-SP (10.4 GSPS, 12-bit, rad-hard)"),
        ("FPGA", "XQRVC1902 (rad-hard, 1760-pin BGA)"),
        ("RF Bandwidth", "500 MHz (8-12 GHz X-band)"),
        ("DDC Channels", "8 independent channels"),
        ("Data Output", "SpaceWire (2 links, 100 Mbps each)"),
        ("Power Input", "4.5V DC (space bus)"),
        ("Power Rails", "6 rails (1.0V, 1.8V, 3.3V, 1.0V, 1.8V, 2.5V)"),
        ("Total Power", "61.8W input, 50.3W output (81.4% efficiency)"),
        ("Board Size", "200mm x 200mm x 28mm"),
        ("Layers", "12-layer Megtron6 stackup"),
        ("Temperature", "-55C to +125C (MIL-STD-883)"),
        ("Radiation", "100 krad(Si) TID, SEL immune"),
        ("MTBF", "259,000 hours (29.6 years)"),
        ("Mass", "< 1.2 kg (estimated)"),
    ]

    widths = [45, 145]
    for i, (k, v) in enumerate(specs):
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(widths[0], 6, k, 1, 0, 'L', (i % 2 == 0))
        pdf.set_font('Helvetica', '', 9)
        pdf.cell(widths[1], 6, v, 1, 1, 'L', (i % 2 == 0))

    pdf.ln(10)

    # Power budget summary
    pdf.section_title('POWER BUDGET SUMMARY')
    pwidths = [30, 25, 25, 25, 30, 30, 25]
    headers = ['Rail', 'Vout', 'Ityp', 'Imax', 'Ptyp', 'Pmax', 'Type']
    pdf.table_row(headers, pwidths, bold=True, fill=True)
    rails = [
        ('VCCINT', '1.0V', '30A', '44A', '30W', '44W', 'Buck'),
        ('VCCAUX', '1.8V', '4A', '6A', '7.2W', '10.8W', 'Buck'),
        ('VCCO', '3.3V', '2A', '3A', '6.6W', '9.9W', 'Buck'),
        ('AVDD', '1.0V', '1A', '1.5A', '1W', '1.5W', 'LDO'),
        ('DVDD', '1.8V', '1A', '1.5A', '1.8W', '2.7W', 'LDO'),
        ('VCLK', '2.5V', '1.5A', '2A', '3.75W', '5W', 'LDO'),
    ]
    for i, row in enumerate(rails):
        pdf.table_row(row, pwidths, fill=(i % 2 == 0))

    pdf.ln(10)

    # Component count
    pdf.section_title('COMPONENT SUMMARY')
    cwidths = [50, 30, 40, 70]
    pdf.table_row(['Category', 'Count', 'Cost (USD)', 'Notes'], cwidths, bold=True, fill=True)
    components = [
        ('ICs (Rad-Hard)', '14', '$101,620', 'ADC, FPGA, Clock, Power'),
        ('Oscillator', '1', '$185', 'Crystek CVHD-950 VCXO'),
        ('Resistors', '50', '$1', '0402/0603, 1%/0.1%'),
        ('Capacitors', '168', '$49', 'C0G/X7R/X5R/Tantalum'),
        ('Inductors', '3', '$17.50', '100nH/2.2uH/4.7uH'),
        ('Ferrite Beads', '11', '$0.55', 'Power filtering'),
        ('Protection', '6', '$1.40', 'TVS, ESD diodes'),
        ('Connectors', '9', '$109.50', 'SMA, SpaceWire, JTAG'),
        ('Mechanical', '10', '$161', 'Standoffs, shield, HS'),
        ('TOTAL', '272', '$102,144', ''),
    ]
    for i, row in enumerate(components):
        bold = (i == len(components) - 1)
        pdf.table_row(row, cwidths, bold=bold, fill=(i % 2 == 0))

    master_path = os.path.join(OUTPUT, "XBand_DigitalModule_Master.pdf")
    pdf.output(master_path)
    print(f"  -> {master_path} ({os.path.getsize(master_path)} bytes)")
    print("\nDone! All PDFs generated in exports/")


if __name__ == '__main__':
    main()
