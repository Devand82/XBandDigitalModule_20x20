#!/usr/bin/env python3
"""
Generate Custom_ICs.kicad_sym with correct datasheet pin numbers.

Output: schematic/Custom_ICs.kicad_sym

Pin numbers match physical package pinouts from manufacturer datasheets:
- BGA packages use ball coordinates (e.g. "A4", "F1")
- CFP/CQFP/QFP packages use numeric pin numbers (e.g. "1", "64")
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(SCRIPT_DIR, "schematic", "Custom_ICs.kicad_sym")


# ---------------------------------------------------------------------------
# KiCad S-expression helpers
# ---------------------------------------------------------------------------

def _pin(name, number, ptype, x, y, angle=0, length=150):
    """Generate a single KiCad pin S-expression."""
    return (
        f'      (pin {ptype} line (at {x} {y} {angle}) (length {length})'
        f' (name "{name}" (effects (font (size 40 40))))'
        f' (number "{number}" (effects (font (size 40 40)))))'
    )


def _sym(name, ref, footprint, datasheet, bw, bh, left, right,
          bottom=None, top=None):
    """Build a complete symbol block.

    Parameters
    ----------
    name, ref, footprint, datasheet : str
    bw, bh : int - half-width / half-height of the rectangle (mil)
    left, right : list of (pin_name, pin_number, pin_type)
    bottom, top : optional list of (pin_name, pin_number, pin_type)
    """
    lines = [
        f'  (symbol "{name}"',
        f'    (property "Reference" "{ref}" (at 0 {bh + 100} 0)'
        f' (effects (font (size 50 50))))',
        f'    (property "Value" "{name}" (at 0 -{bh + 100} 0)'
        f' (effects (font (size 50 50))))',
        f'    (property "Footprint" "{footprint}" (at 0 0 0)'
        f' (effects (font (size 50 50)) hide))',
        f'    (property "Datasheet" "{datasheet}" (at 0 0 0)'
        f' (effects (font (size 50 50)) hide))',
        f'    (symbol "{name}_0_1"',
        f'      (rectangle (start -{bw} {bh}) (end {bw} -{bh})'
        f' (stroke (width 10) (type default)) (fill (type background)))',
        f'    )',
        f'    (symbol "{name}_1_1"',
    ]

    # ---- left pins (top to bottom) ----
    y = bh - 50
    for pname, pnum, ptype in left:
        lines.append(_pin(pname, str(pnum), ptype, -(bw + 100), y, 0))
        y -= 50

    # ---- right pins (top to bottom) ----
    y = bh - 50
    for pname, pnum, ptype in right:
        lines.append(_pin(pname, str(pnum), ptype, bw + 100, y, 180))
        y -= 50

    # ---- top pins (left to right) ----
    if top:
        x = -((len(top) - 1) * 50) // 2
        for pname, pnum, ptype in top:
            lines.append(_pin(pname, str(pnum), ptype, x, bh + 100, 270))
            x += 50

    # ---- bottom pins (multi-row, 20 per row) ----
    if bottom:
        row_sz = 20
        rows = [bottom[i:i + row_sz] for i in range(0, len(bottom), row_sz)]
        for ri, row in enumerate(rows):
            y_pos = -(bh + 150 + ri * 50)
            x = -((len(row) - 1) * 50) // 2
            for pname, pnum, ptype in row:
                lines.append(_pin(pname, str(pnum), ptype, x, y_pos, 90))
                x += 50

    lines.append('    )')
    lines.append('  )')
    return '\n'.join(lines)


# =========================================================================
# 1. ADC12DJ5200-SP  (144-BGA, 12x12, ball coordinates as pin numbers)
# =========================================================================

def _adc12dj5200_sp():
    left = [
        ("INA+",    "A4", "input"),
        ("INA-",    "A5", "input"),
        ("INB+",    "L4", "input"),
        ("INB-",    "L5", "input"),
        ("CLK+",    "F1", "input"),
        ("CLK-",    "G1", "input"),
        ("SYSREF+", "K1", "input"),
        ("SYSREF-", "L1", "input"),
        ("CS",      "E8", "input"),
        ("SCLK",    "F8", "input"),
        ("SDI",     "G8", "input"),
        ("SDO",     "H8", "output"),
        ("PD",      "K6", "input"),
        ("TMSTP+",  "B1", "input"),
        ("TMSTP-",  "C1", "input"),
        ("SYNCSE",  "C2", "input"),
        ("NCOA0",   "C7", "input"),
        ("NCOA1",   "D7", "input"),
        ("NCOB0",   "K7", "input"),
        ("NCOB1",   "J7", "input"),
        ("CALTRIG", "E7", "input"),
        ("CALSTAT", "F7", "output"),
        ("ORA0",    "C8", "output"),
        ("ORA1",    "D8", "output"),
        ("ORB0",    "K8", "output"),
        ("ORB1",    "J8", "output"),
        ("BG",      "C3", "output"),
        ("TDIODE+", "K2", "passive"),
        ("TDIODE-", "K3", "passive"),
    ]

    right = [
        ("DA0+", "E12", "output"), ("DA0-", "F12", "output"),
        ("DA1+", "C12", "output"), ("DA1-", "D12", "output"),
        ("DA2+", "A10", "output"), ("DA2-", "A11", "output"),
        ("DA3+", "A8",  "output"), ("DA3-", "A9",  "output"),
        ("DA4+", "E11", "output"), ("DA4-", "F11", "output"),
        ("DA5+", "C11", "output"), ("DA5-", "D11", "output"),
        ("DA6+", "B10", "output"), ("DA6-", "B11", "output"),
        ("DA7+", "B8",  "output"), ("DA7-", "B9",  "output"),
        ("DB0+", "H12", "output"), ("DB0-", "G12", "output"),
        ("DB1+", "K12", "output"), ("DB1-", "J12", "output"),
        ("DB2+", "L10", "output"), ("DB2-", "L11", "output"),
        ("DB3+", "L8",  "output"), ("DB3-", "L9",  "output"),
        ("DB4+", "H11", "output"), ("DB4-", "G11", "output"),
        ("DB5+", "K11", "output"), ("DB5-", "J11", "output"),
    ]

    bottom = []
    for b in ["C5","D2","D3","D5","E5","F5","G5","H5","J2","J3","J5","K5"]:
        bottom.append(("VA11", b, "power_in"))
    for b in ["C4","D4","E2","E3","E4","F4","G4","H2","H3","H4","J4","K4"]:
        bottom.append(("VA19", b, "power_in"))
    for b in ["C9","C10","E9","E10","G7","H7","H9","H10","K9","K10"]:
        bottom.append(("VD11", b, "power_in"))
    for b in ["A1","A2","A3","A6","A7","B2","B3","B4","B5","B6","B7",
              "C6","D1","D6","E1","E6","F2","F3","F6","G2","G3","G6",
              "H1","H6","J1","J6","L2","L3","L6","L7",
              "M1","M2","M3","M6","M7"]:
        bottom.append(("AGND", b, "power_in"))
    for b in ["A12","B12","D9","D10","F9","F10","G9","G10","J9","J10","L12","M12"]:
        bottom.append(("DGND", b, "power_in"))

    return _sym(
        "ADC12DJ5200-SP", "U",
        "Package_BGA:BGA-144_12x12_8.0x8.0mm_P0.65mm",
        "https://www.ti.com/lit/ds/symlink/adc12dj5200-sp.pdf",
        700, 900, left, right, bottom,
    )


# =========================================================================
# 2. TPS7H5001-SP  (22-pin CFP, dual-output buck)
# =========================================================================

def _tps7h5001_sp():
    left = [
        ("RT",     1,  "input"),
        ("PS",     2,  "input"),
        ("SP",     3,  "input"),
        ("LEB",    4,  "input"),
        ("HICC",   5,  "input"),
        ("SYNC",   6,  "input"),
        ("DCL",    7,  "input"),
        ("EN",     8,  "input"),
    ]
    right = [
        ("VIN",    9,  "power_in"),
        ("OUTA",  10,  "power_out"),
        ("OUTB",  11,  "power_out"),
        ("SRB",   12,  "passive"),
        ("SRA",   13,  "passive"),
    ]
    bottom = [
        ("AVSS",   14, "power_in"),
        ("VLDO",   15, "passive"),
        ("CS_ILIM",16, "input"),
        ("FAULT",  17, "output"),
        ("REFCAP", 18, "passive"),
        ("RSC",    19, "passive"),
        ("SS",     20, "input"),
        ("VSENSE", 21, "input"),
        ("COMP",   22, "input"),
    ]
    return _sym(
        "TPS7H5001-SP", "U",
        "Package_CFP:CFP-22",
        "https://www.ti.com/lit/ds/symlink/tps7h5001-sp.pdf",
        500, 400, left, right, bottom,
    )


# =========================================================================
# 3. TPS7H5002-SP  (22-pin CFP, single-output buck)
# =========================================================================

def _tps7h5002_sp():
    left = [
        ("RT",     1,  "input"),
        ("PS",     2,  "input"),
        ("SP",     3,  "input"),
        ("LEB",    4,  "input"),
        ("HICC",   5,  "input"),
        ("SYNC",   6,  "input"),
        ("DCL",    7,  "input"),
        ("EN",     8,  "input"),
    ]
    right = [
        ("VIN",    9,  "power_in"),
        ("OUTA",  10,  "power_out"),
        ("NC",    11,  "passive"),
        ("NC",    12,  "passive"),
        ("SRA",   13,  "passive"),
    ]
    bottom = [
        ("AVSS",   14, "power_in"),
        ("VLDO",   15, "passive"),
        ("CS_ILIM",16, "input"),
        ("FAULT",  17, "output"),
        ("REFCAP", 18, "passive"),
        ("RSC",    19, "passive"),
        ("SS",     20, "input"),
        ("VSENSE", 21, "input"),
        ("COMP",   22, "input"),
    ]
    return _sym(
        "TPS7H5002-SP", "U",
        "Package_CFP:CFP-22",
        "https://www.ti.com/lit/ds/symlink/tps7h5002-sp.pdf",
        500, 400, left, right, bottom,
    )


# =========================================================================
# 4. LMK04832-SP  (64-pin CFP + DAP)
# =========================================================================

def _lmk04832_sp():
    left = [
        ("CLKin0",                 37, "input"),
        ("CLKin0*",                38, "input"),
        ("CLKin1/FBCLKin/Fin1",   34, "input"),
        ("CLKin1*/FBCLKin*/Fin1*", 35, "input"),
        ("OSCin",                  43, "input"),
        ("OSCin*",                 44, "input"),
        ("FIN0",                    8, "input"),
        ("FIN0*",                   9, "input"),
        ("SYNC/SYSREF_REQ",         6, "input"),
        ("RESET/GPO",               5, "input"),
        ("CS*",                    18, "input"),
        ("SCK",                    19, "input"),
        ("SDIO",                   20, "bidirectional"),
        ("CLKin_SEL0",             58, "input"),
        ("CLKin_SEL1",             59, "input"),
    ]

    right = [
        ("CLKout0",   1, "output"), ("CLKout0*",   2, "output"),
        ("CLKout1",   3, "output"), ("CLKout1*",   4, "output"),
        ("CLKout2",  15, "output"), ("CLKout2*",  16, "output"),
        ("CLKout3",  13, "output"), ("CLKout3*",  14, "output"),
        ("CLKout4",  24, "output"), ("CLKout4*",  25, "output"),
        ("CLKout5",  22, "output"), ("CLKout5*",  23, "output"),
        ("CLKout6",  27, "output"), ("CLKout6*",  28, "output"),
        ("CLKout7",  29, "output"), ("CLKout7*",  30, "output"),
        ("CLKout8",  51, "output"), ("CLKout8*",  52, "output"),
        ("CLKout9",  49, "output"), ("CLKout9*",  50, "output"),
        ("CLKout10", 54, "output"), ("CLKout10*", 55, "output"),
        ("CLKout11", 56, "output"), ("CLKout11*", 57, "output"),
        ("CLKout12", 62, "output"), ("CLKout12*", 63, "output"),
        ("CLKout13", 60, "output"), ("CLKout13*", 61, "output"),
        ("OSCout",   40, "output"), ("OSCout*",   41, "output"),
    ]

    bottom = [
        ("Vcc1_VCO",    10, "power_in"),
        ("Vcc2_CG1",    17, "power_in"),
        ("Vcc3_SYSREF", 21, "power_in"),
        ("Vcc4_CG2",    26, "power_in"),
        ("Vcc5_DIG",    33, "power_in"),
        ("Vcc6_PLL1",   36, "power_in"),
        ("Vcc7_OSCout", 39, "power_in"),
        ("Vcc8_OSCin",  42, "power_in"),
        ("Vcc9_CP2",    45, "power_in"),
        ("Vcc10_PLL2",  47, "power_in"),
        ("Vcc11_CG3",   53, "power_in"),
        ("Vcc12_CG0",   64, "power_in"),
        ("LDObyp1",     11, "passive"),
        ("LDObyp2",     12, "passive"),
        ("CPout1",      32, "output"),
        ("CPout2",      46, "output"),
        ("Status_LD1",  31, "output"),
        ("Status_LD2",  48, "output"),
        ("GND",          7, "power_in"),
        ("DAP",         65, "power_in"),
    ]
    return _sym(
        "LMK04832-SP", "U",
        "Package_CFP:CQFP-64",
        "https://www.ti.com/lit/ds/symlink/lmk04832-sp.pdf",
        700, 900, left, right, bottom,
    )


# =========================================================================
# 5. LMX2615-SP  (64-pin CQFP + DAP)
# =========================================================================

def _lmx2615_sp():
    left = [
        ("FS0",        3, "input"),
        ("FS1",        4, "input"),
        ("FS2",       15, "input"),
        ("FS3",       16, "input"),
        ("FS4",       17, "input"),
        ("FS5",       18, "input"),
        ("FS6",       19, "input"),
        ("FS7",       20, "input"),
        ("CAL",        5, "input"),
        ("SYNC",       9, "input"),
        ("SCK",       26, "input"),
        ("SDI",       27, "input"),
        ("CSB",       39, "input"),
        ("MUXout",    32, "output"),
        ("SysRefReq", 43, "input"),
        ("RECAL_EN",  45, "input"),
    ]

    right = [
        ("RFoutAP",  37, "output"),
        ("RFoutAM",  36, "output"),
        ("RFoutBP",  30, "output"),
        ("RFoutBM",  29, "output"),
        ("VccDIG",   11, "power_in"),
        ("VccCP",    21, "power_in"),
        ("VccMASH",  25, "power_in"),
        ("VccBUF",   34, "power_in"),
        ("VccVCO",   57, "power_in"),
        ("VccVCO2",  41, "power_in"),
        ("VregIN",   14, "power_in"),
        ("VregVCO",  59, "power_in"),
    ]

    top = [
        ("OSCinP", 12, "input"),
        ("OSCinM", 13, "input"),
    ]

    bottom = [
        ("GND",         6, "power_in"),
        ("GND",         8, "power_in"),
        ("GND",        10, "power_in"),
        ("GND",        23, "power_in"),
        ("GND",        24, "power_in"),
        ("GND",        28, "power_in"),
        ("GND",        31, "power_in"),
        ("GND",        35, "power_in"),
        ("GND",        38, "power_in"),
        ("GND",        40, "power_in"),
        ("GND",        51, "power_in"),
        ("GND",        54, "power_in"),
        ("GND",        60, "power_in"),
        ("GND",        61, "power_in"),
        ("VbiasVCO",    7, "passive"),
        ("VbiasVCO2",  42, "passive"),
        ("VbiasVARAC", 53, "passive"),
        ("VrefVCO",    56, "passive"),
        ("VrefVCO2",   44, "passive"),
        ("Vtune",      55, "passive"),
        ("CPout",      22, "output"),
        ("NC",          1, "passive"),
        ("NC",          2, "passive"),
        ("NC",         33, "passive"),
        ("NC",         46, "passive"),
        ("NC",         47, "passive"),
        ("NC",         48, "passive"),
        ("NC",         49, "passive"),
        ("NC",         50, "passive"),
        ("NC",         52, "passive"),
        ("NC",         58, "passive"),
        ("NC",         62, "passive"),
        ("NC",         63, "passive"),
        ("NC",         64, "passive"),
        ("DAP",        65, "power_in"),
    ]
    return _sym(
        "LMX2615-SP", "U",
        "Package_CFP:CQFP-64",
        "https://www.ti.com/lit/ds/symlink/lmx2615-sp.pdf",
        600, 800, left, right, bottom, top,
    )


# =========================================================================
# 6. TPS7H1111-SP  (14-pin CFP)
# =========================================================================

def _tps7h1111_sp():
    left = [
        ("BIAS",  1, "input"),
        ("EN",    2, "input"),
        ("IN",    3, "power_in"),
        ("IN",    4, "power_in"),
        ("CLM",   5, "input"),
    ]
    right = [
        ("PG",    7, "output"),
        ("REF",   8, "output"),
        ("OUT",  11, "power_out"),
        ("OUT",  12, "power_out"),
        ("OUTS", 13, "output"),
    ]
    bottom = [
        ("GND",     6, "power_in"),
        ("SS_SET",  9, "input"),
        ("STAB",   10, "passive"),
        ("FB_PG",  14, "input"),
    ]
    return _sym(
        "TPS7H1111-SP", "U",
        "Package_CFP:CFP-14",
        "https://www.ti.com/lit/ds/symlink/tps7h1111-sp.pdf",
        450, 350, left, right, bottom,
    )


# =========================================================================
# 7. TPS7H1121-SP  (22-pin CFP)
# =========================================================================

def _tps7h1121_sp():
    left = [
        ("EN",  1, "input"),
        ("IN",  2, "power_in"),
        ("IN",  3, "power_in"),
        ("IN",  4, "power_in"),
        ("IN",  5, "power_in"),
        ("IN",  6, "power_in"),
        ("IN",  7, "power_in"),
    ]
    right = [
        ("CL",  10, "output"),
        ("OUT", 16, "power_out"),
        ("OUT", 17, "power_out"),
        ("OUT", 18, "power_out"),
        ("OUT", 19, "power_out"),
        ("OUT", 20, "power_out"),
        ("OUT", 21, "power_out"),
        ("PG",  22, "output"),
    ]
    bottom = [
        ("SS",    8, "input"),
        ("GND",   9, "power_in"),
        ("STAB", 11, "passive"),
        ("FB",   12, "input"),
        ("GND",  13, "power_in"),
        ("GND",  14, "power_in"),
        ("VLDO", 15, "passive"),
    ]
    return _sym(
        "TPS7H1121-SP", "U",
        "Package_CFP:CFP-22",
        "https://www.ti.com/lit/ds/symlink/tps7h1121-sp.pdf",
        500, 400, left, right, bottom,
    )


# =========================================================================
# 8. TPS7H3014-SP  (22-pin CFP)
# =========================================================================

def _tps7h3014_sp():
    left = [
        ("IN",      9, "power_in"),
        ("SENSE1",  1, "input"),
        ("SENSE2",  2, "input"),
        ("SENSE3",  3, "input"),
        ("SENSE4",  4, "input"),
        ("HYS",    13, "input"),
    ]
    right = [
        ("EN1",      5, "input"),
        ("EN2",      6, "input"),
        ("EN3",      7, "input"),
        ("EN4",      8, "input"),
        ("UP",      16, "input"),
        ("DOWN",    17, "input"),
        ("FAULT",   14, "output"),
        ("PWRGD",   15, "output"),
        ("SEQ_DONE",22, "output"),
    ]
    bottom = [
        ("REFCAP",  10, "passive"),
        ("VLDO",    11, "passive"),
        ("GND",     12, "power_in"),
        ("PULL_UP1",18, "passive"),
        ("PULL_UP2",19, "passive"),
        ("DLY_TMR", 20, "input"),
        ("REG_TMR", 21, "input"),
    ]
    return _sym(
        "TPS7H3014-SP", "U",
        "Package_CFP:CFP-22",
        "https://www.ti.com/lit/ds/symlink/tps7h3014-sp.pdf",
        500, 400, left, right, bottom,
    )


# =========================================================================
# 9. INA214-SP  (6-pin SC70)
# =========================================================================

def _ina214_sp():
    left = [
        ("REF", 1, "input"),
        ("GND", 2, "power_in"),
        ("V+",  3, "power_in"),
        ("IN+", 4, "input"),
        ("IN-", 5, "input"),
    ]
    right = [
        ("OUT", 6, "output"),
    ]
    return _sym(
        "INA214-SP", "U",
        "Package_TO_SOT_SMD:SOT-363",
        "https://www.ti.com/lit/ds/symlink/ina214-sp.pdf",
        350, 300, left, right,
    )


# =========================================================================
# 10. CVHD-950  (4-pin VCXO oscillator)
# =========================================================================

def _cvhd_950():
    left = [
        ("Vdd", 4, "power_in"),
    ]
    right = [
        ("OUT", 3, "output"),
    ]
    bottom = [
        ("Vcontrol", 1, "input"),
        ("GND",      2, "power_in"),
    ]
    return _sym(
        "Crystek_CVHD-950", "Y",
        "Oscillator:Oscillator_SMD_5032_5x3.2mm",
        "https://www.crystek.com/content/cvhd-950-datasheet",
        350, 250, left, right, bottom,
    )


# =========================================================================
# 11. ISL70003ASEH  (64-pin CQFP + DAP)
# =========================================================================

def _isl70003aseh():
    left = [
        ("NI",      1, "input"),
        ("FB",      2, "input"),
        ("VERR",    3, "input"),
        ("OR_VIN",  4, "input"),
        ("VREFA",   5, "output"),
        ("ENABLE", 12, "input"),
        ("RT/CT",  13, "input"),
        ("FSEL",   14, "input"),
        ("SYNC",   15, "input"),
        ("SS_CAP", 16, "input"),
        ("OCSETA", 17, "input"),
        ("OCSETB", 34, "input"),
        ("BUFIN-", 35, "input"),
        ("BUFIN+", 36, "input"),
        ("BUFOUT", 37, "output"),
        ("REF",    38, "output"),
        ("IMON",   32, "output"),
        ("DE",     31, "input"),
        ("DESEL",  52, "input"),
        ("SEL1",   29, "input"),
        ("SEL2",   30, "input"),
    ]

    right = [
        ("AVDD",     6, "power_in"),
        ("AGND",     7, "power_in"),
        ("DGND",     8, "power_in"),
        ("VREF_OUTS",9, "output"),
        ("DVDD",    10, "power_in"),
        ("VREFD",   11, "output"),
        ("PVIN1",   18, "power_in"),
        ("LX1",     19, "passive"),
        ("PVIN2",   23, "power_in"),
        ("LX2",     22, "passive"),
        ("PVIN3",   28, "power_in"),
        ("LX3",     24, "passive"),
        ("PVIN4",   39, "power_in"),
        ("LX4",     27, "passive"),
        ("PVIN5",   44, "power_in"),
        ("LX5",     40, "passive"),
        ("PVIN6",   49, "power_in"),
        ("LX6",     43, "passive"),
        ("PVIN7",   53, "power_in"),
        ("LX7",     45, "passive"),
        ("PVIN8",   58, "power_in"),
        ("LX8",     48, "passive"),
        ("PVIN9",   59, "power_in"),
        ("LX9",     54, "passive"),
        ("PVIN10",  60, "power_in"),
        ("LX10",    57, "passive"),
        ("HS",      50, "passive"),
        ("PGOOD",   51, "output"),
    ]

    bottom = [
        ("PGND1",   20, "power_in"),
        ("PGND2",   21, "power_in"),
        ("PGND3",   25, "power_in"),
        ("PGND4",   26, "power_in"),
        ("PGND5",   41, "power_in"),
        ("PGND6",   42, "power_in"),
        ("PGND7",   46, "power_in"),
        ("PGND8",   47, "power_in"),
        ("PGND9",   55, "power_in"),
        ("PGND10",  56, "power_in"),
        ("SGND",    33, "power_in"),
        ("NC",      61, "passive"),
        ("NC",      62, "passive"),
        ("NC",      63, "passive"),
        ("NC",      64, "passive"),
    ]
    return _sym(
        "ISL70003ASEH", "U",
        "Package_CFP:CQFP-64",
        "https://www.renesas.com/us/en/document/dst/isl70003aseh-datasheet",
        700, 800, left, right, bottom,
    )


# =========================================================================
# Main
# =========================================================================

def main():
    generators = [
        _adc12dj5200_sp,
        _tps7h5001_sp,
        _tps7h5002_sp,
        _lmk04832_sp,
        _lmx2615_sp,
        _tps7h1111_sp,
        _tps7h1121_sp,
        _tps7h3014_sp,
        _ina214_sp,
        _cvhd_950,
        _isl70003aseh,
    ]

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

    parts = []
    parts.append('(kicad_symbol_lib (version 20230121) (generator generate_ic_symbols)')
    parts.append('')

    for gen_fn in generators:
        parts.append(gen_fn())
        parts.append('')

    parts.append(')')
    content = '\n'.join(parts)

    with open(OUTPUT, 'w') as f:
        f.write(content)

    # Validate parenthesis balance
    opens = content.count('(')
    closes = content.count(')')
    if opens != closes:
        print(f"ERROR: Parenthesis mismatch: {opens} opens vs {closes} closes", file=sys.stderr)
        sys.exit(1)

    print(f"Generated {OUTPUT}")
    print(f"  {len(generators)} symbols")
    print(f"  Parentheses balanced: {opens} pairs")

    # Show symbol names
    for gen_fn in generators:
        name = gen_fn.__doc__ or gen_fn.__name__
        print(f"  - {name}")


if __name__ == '__main__':
    main()
