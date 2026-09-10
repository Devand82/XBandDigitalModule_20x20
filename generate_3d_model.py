#!/usr/bin/env python3
"""Generate enhanced 3D mechanical model with build123d."""
import os
from build123d import *

BASE = "/opt/cryptobot/XBandDigitalModule_20x20"
OUT_DIR = os.path.join(BASE, "exports/kicad_3d")
os.makedirs(OUT_DIR, exist_ok=True)

def create_mechanical_assembly():
    """Create complete 20x20cm module mechanical assembly."""
    # PCB dimensions (200mm x 200mm x 1.6mm Megtron6)
    pcb_w, pcb_h, pcb_t = 200, 200, 1.6

    with BuildPart() as assembly:
        # === PCB Board ===
        with BuildSketch(Plane.XY):
            Rectangle(pcb_w, pcb_h)
        extrude(amount=pcb_t)

        # === Standoffs (4x M3, 5mm height) ===
        standoff_positions = [
            (10, 10), (190, 10), (10, 190), (190, 190)
        ]
        for sx, sy in standoff_positions:
            with Locations([Location((sx, sy, pcb_t))]):
                Cylinder(radius=1.5, height=5)

        # === Mounting holes (4x M3) ===
        for sx, sy in standoff_positions:
            with Locations([Location((sx, sy, -0.1))]):
                Cylinder(radius=1.7, height=pcb_t + 0.2)

        # === RF Shield (15x15mm, 3mm height, around ADC area) ===
        with Locations([Location((50, 100, pcb_t))]):
            Box(15, 15, 3)

        # === FPGA XQRVC1902 (35x35mm BGA, 2.4mm height) ===
        with Locations([Location((100, 100, pcb_t))]):
            Box(35, 35, 2.4)

        # === ADC12DJ5200-SP (10x10mm QFN, 1.2mm height) ===
        with Locations([Location((50, 100, pcb_t))]):
            Box(10, 10, 1.2)

        # === Clock oscillators ===
        # Crystek CVHD-950 (5x3.2mm, 1.2mm)
        with Locations([Location((150, 30, pcb_t))]):
            Box(5, 3.2, 1.2)

        # === Power ICs ===
        # TPS7H5002-SP (8x8mm QFN, 1mm)
        with Locations([Location((30, 30, pcb_t))]):
            Box(8, 8, 1)

        # ISL70003ASEH (6x6mm QFN, 1mm) x2
        with Locations([Location((30, 50, pcb_t))]):
            Box(6, 6, 1)
        with Locations([Location((30, 70, pcb_t))]):
            Box(6, 6, 1)

        # === Inductors ===
        # 100nH/55A power inductor (12x12x8mm)
        with Locations([Location((45, 30, pcb_t))]):
            Box(12, 12, 8)

        # 2.2uH inductor
        with Locations([Location((45, 50, pcb_t))]):
            Box(8, 8, 5)

        # 4.7uH inductor
        with Locations([Location((45, 70, pcb_t))]):
            Box(8, 8, 5)

        # === Heatsink (50x50x15mm finned) ===
        with Locations([Location((100, 100, pcb_t + 2.4))]):
            Box(50, 50, 2)
            # Fins
            for i in range(5):
                with Locations([Location((-20 + i*10, 0, 2))]):
                    Box(2, 48, 13)

        # === Connectors ===
        # JTAG header (10-pin, 2.54mm pitch)
        with Locations([Location((10, 190, pcb_t))]):
            Box(5, 10, 3)

        # SpaceWire connectors x2
        with Locations([Location((190, 180, pcb_t))]):
            Box(8, 6, 4)
        with Locations([Location((190, 165, pcb_t))]):
            Box(8, 6, 4)

        # Power connector (terminal block)
        with Locations([Location((10, 10, pcb_t))]):
            Box(8, 12, 8)

        # UART header
        with Locations([Location((10, 175, pcb_t))]):
            Box(4, 8, 3)

        # === Decoupling capacitors (array) ===
        cap_positions = [
            (85, 95), (85, 105), (90, 95), (90, 105),
            (110, 95), (110, 105), (115, 95), (115, 105),
            (95, 85), (105, 85), (95, 115), (105, 115),
        ]
        for cx, cy in cap_positions:
            with Locations([Location((cx, cy, pcb_t))]):
                Box(2, 1.25, 0.8)

        # === Bottom cover (aluminum, 200x200x1mm) ===
        with Locations([Location((0, 0, -2))]):
            Box(pcb_w, pcb_h, 1)

        # === Thermal pad between PCB and bottom cover ===
        with Locations([Location((0, 0, -0.5))]):
            Box(100, 100, 0.5)

    return assembly


def create_single_view():
    """Create simpler isometric view for PDF rendering."""
    pcb_w, pcb_h, pcb_t = 200, 200, 1.6

    with BuildPart() as model:
        # PCB
        with BuildSketch(Plane.XY):
            Rectangle(pcb_w, pcb_h)
        extrude(amount=pcb_t)

        # Standoffs
        for sx, sy in [(10,10),(190,10),(10,190),(190,190)]:
            with Locations([Location((sx, sy, pcb_t))]):
                Cylinder(radius=1.5, height=5)

        # FPGA
        with Locations([Location((100, 100, pcb_t))]):
            Box(35, 35, 2.4)

        # ADC
        with Locations([Location((50, 100, pcb_t))]):
            Box(10, 10, 1.2)

        # Heatsink
        with Locations([Location((100, 100, pcb_t + 2.4))]):
            Box(50, 50, 2)
            for i in range(5):
                with Locations([Location((-20 + i*10, 0, 2))]):
                    Box(2, 48, 13)

        # Power section
        with Locations([Location((30, 30, pcb_t))]):
            Box(8, 8, 1)
        with Locations([Location((45, 30, pcb_t))]):
            Box(12, 12, 8)

        # Connectors
        with Locations([Location((190, 180, pcb_t))]):
            Box(8, 6, 4)
        with Locations([Location((190, 165, pcb_t))]):
            Box(8, 6, 4)
        with Locations([Location((10, 10, pcb_t))]):
            Box(8, 12, 8)

        # Bottom cover
        with Locations([Location((0, 0, -2))]):
            Box(pcb_w, pcb_h, 1)

    return model


if __name__ == '__main__':
    print("Generating enhanced 3D mechanical model...")

    # Full assembly STEP
    print("  Creating full assembly...")
    assembly = create_mechanical_assembly()
    step_path = os.path.join(OUT_DIR, "XBand_Mechanical_Assembly.step")
    export_step(assembly.part, step_path)
    sz = os.path.getsize(step_path)
    print(f"  -> XBand_Mechanical_Assembly.step ({sz:,} bytes)")

    # Simple model STEP
    print("  Creating simple model...")
    model = create_single_view()
    step_path2 = os.path.join(OUT_DIR, "XBand_Mechanical_Simple.step")
    export_step(model.part, step_path2)
    sz2 = os.path.getsize(step_path2)
    print(f"  -> XBand_Mechanical_Simple.step ({sz2:,} bytes)")

    # Also merge with PCB STEP from KiCad
    print("  Done!")
