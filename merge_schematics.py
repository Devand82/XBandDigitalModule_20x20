#!/usr/bin/env python3
"""Merge all schematic PDFs into a single unified schematic PDF."""
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from fpdf import FPDF

BASE = "/opt/cryptobot/XBandDigitalModule_20x20"
EXPORTS = os.path.join(BASE, "exports")

def create_cover_page(output_path):
    """Create a cover page for the unified schematic PDF."""
    pdf = FPDF(orientation='L', unit='mm', format='A3')
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # Background
    pdf.set_fill_color(0, 30, 60)
    pdf.rect(0, 0, 420, 297, 'F')

    # Title
    pdf.set_font('Helvetica', 'B', 36)
    pdf.set_text_color(255, 255, 255)
    pdf.ln(40)
    pdf.cell(0, 20, 'X-BAND DIGITAL MODULE', 0, 1, 'C')

    pdf.set_font('Helvetica', '', 18)
    pdf.set_text_color(180, 210, 255)
    pdf.cell(0, 12, 'Complete Schematic Package', 0, 1, 'C')
    pdf.cell(0, 12, '20 x 20 cm Space-Grade PCB', 0, 1, 'C')

    pdf.ln(10)
    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(200, 200, 200)
    pdf.cell(0, 8, 'Direct RF Sampling Acquisition System', 0, 1, 'C')
    pdf.cell(0, 8, '8-12 GHz X-Band | 500 MHz Bandwidth', 0, 1, 'C')

    pdf.ln(15)
    pdf.set_draw_color(100, 150, 255)
    pdf.set_line_width(0.5)
    pdf.line(100, pdf.get_y(), 320, pdf.get_y())
    pdf.ln(10)

    # Key specs
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(180, 210, 255)
    specs = [
        'ADC: ADC12DJ5200-SP (10.4 GSPS, 12-bit, Rad-Hard)',
        'FPGA: XQRVC1902 (Rad-Hard, 1760-pin BGA)',
        'Clock: LMX2615-SP + LMK04832-SP (45fs jitter)',
        'Power: 6 rails (1.0V/1.8V/3.3V/2.5V), TPS7H5002-SP buck',
        'Output: SpaceWire 2x 100 Mbps',
        'Stackup: 12-layer Megtron6',
        'Size: 200 x 200 mm',
    ]
    for spec in specs:
        pdf.cell(0, 7, spec, 0, 1, 'C')

    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(255, 200, 100)
    pdf.cell(0, 8, 'Revision 1.0 | 2026-09-10', 0, 1, 'C')

    # Table of contents
    pdf.ln(10)
    pdf.set_draw_color(100, 150, 255)
    pdf.line(100, pdf.get_y(), 320, pdf.get_y())
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, 'SCHEMATIC SHEETS', 0, 1, 'C')
    pdf.ln(3)

    sheets = [
        ("01", "Title Block", "System overview and block diagram"),
        ("02", "RF Input", "SMPA, TRF0208-SP balun, 50ohm termination"),
        ("03", "ADC12DJ5200-SP", "12-bit 10.4GSPS ADC, JESD204C, power bypass"),
        ("04", "FPGA XQRVC1902", "Rad-hard FPGA, JESD RX, SpaceWire, SPI, I2C"),
        ("05", "Clock Tree", "LMX2615-SP, LMK04832-SP, VCXO 122.88MHz"),
        ("06", "Power Input", "4.5V input, TVS, ferrite, bulk caps"),
        ("07", "Buck 1.0V Core", "TPS7H5002-SP, 44A, 100nH, all passives"),
        ("08", "Buck 1.8V Aux", "ISL70003ASEH, 6A, 2.2uH, all passives"),
        ("09", "Buck 3.3V I/O", "ISL70003ASEH, 3A, 4.7uH, all passives"),
        ("10", "LDO 1.0V Analog", "TPS7H1111-SP, AVDD for ADC"),
        ("11", "LDO 1.8V Digital", "TPS7H1111-SP, DVDD"),
        ("12", "LDO 2.5V Clock", "TPS7H1121-SP, VCLK"),
        ("13", "Sequencer", "2x TPS7H3014-SP daisy-chain, 5-rail sensing"),
        ("14", "Connectors", "JTAG, SpaceWire, Power, UART"),
        ("15", "Test Points", "All rails and signals"),
        ("16", "Decoupling", "Capacitor summary table"),
        ("17", "Power Tree", "Power block diagram, budget, sequencing"),
    ]

    pdf.set_font('Helvetica', '', 8)
    for num, name, desc in sheets:
        pdf.set_text_color(180, 210, 255)
        pdf.cell(15, 5, num, 0, 0, 'R')
        pdf.set_text_color(255, 255, 255)
        pdf.cell(60, 5, f'  {name}', 0, 0, 'L')
        pdf.set_text_color(150, 170, 200)
        pdf.cell(0, 5, f'  {desc}', 0, 1, 'L')

    pdf.output(output_path)


def merge_all():
    """Merge cover + all schematic PDFs into one file."""
    cover_path = os.path.join(EXPORTS, "_cover_temp.pdf")
    output_path = os.path.join(EXPORTS, "XBand_Schematic_Complete.pdf")

    print("Creating cover page...")
    create_cover_page(cover_path)

    merger = PdfMerger()

    # Add cover
    merger.append(cover_path)
    print(f"  Cover page added")

    # Add each schematic sheet in order
    for i in range(1, 18):
        filename = f"Sheet{i:02d}_*.pdf"
        import glob
        matches = glob.glob(os.path.join(EXPORTS, filename))
        if matches:
            pdf_file = matches[0]
            name = os.path.basename(pdf_file).replace('.pdf', '')
            merger.append(pdf_file)
            print(f"  Added: {name}")

    # Add main schematic
    main_pdf = os.path.join(EXPORTS, "XBand_Schematic_Main.pdf")
    if os.path.exists(main_pdf):
        merger.append(main_pdf)
        print(f"  Added: XBand_Schematic_Main")

    # Write output
    merger.write(output_path)
    merger.close()

    # Cleanup temp
    os.remove(cover_path)

    size = os.path.getsize(output_path)
    print(f"\nUnified schematic PDF: {output_path}")
    print(f"Size: {size:,} bytes ({size/1024:.1f} KB)")
    return output_path


if __name__ == '__main__':
    merge_all()
