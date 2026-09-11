#!/usr/bin/env python3
"""
Fix schematic wiring: connect all component pins to nets via wires+labels.
Uses balanced-paren parsing to properly remove old labels/wires.
"""
import re, glob, uuid, os

SCHEMA_DIR = "schematic"

def uid():
    return str(uuid.uuid4()).replace("-","")[:32]

def parse_sheet(filepath):
    with open(filepath) as f:
        return f.read()

def find_lib_end(content):
    m = content.find('(lib_symbols')
    if m == -1:
        return 0
    depth = 0
    for i in range(m, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return i + 1
    return len(content)

def find_balanced_end(content, start):
    """Find end position of a balanced paren expression starting at content[start]=='('"""
    depth = 0
    for i in range(start, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return i + 1
    return start

def remove_elements_by_tag(content, tags):
    """Remove top-level elements matching given tags using balanced paren parsing.
    Tags like ('label', 'wire', 'global_label', 'junction', 'no_connect').
    Preserves everything inside (lib_symbols ...) and (symbol (lib_id ...))."""
    lib_end = find_lib_end(content)
    before = content[:lib_end]
    
    # Parse the section after lib_symbols
    rest = content[lib_end:]
    result = []
    i = 0
    
    while i < len(rest):
        # Check if we're at a tag to remove
        skip = False
        for tag in tags:
            tag_str = f'({tag} '
            if rest[i:i+len(tag_str)] == tag_str:
                # Find balanced end and skip
                end = find_balanced_end(rest, i)
                # Also skip leading whitespace
                while i > 0 and rest[i-1] in (' ', '\n', '\t'):
                    i -= 1
                i = end
                skip = True
                break
        
        if not skip:
            result.append(rest[i])
            i += 1
    
    return before + ''.join(result)

def extract_all_pin_info(content):
    """Get all pin positions from lib_symbols + instance positions."""
    lib_end = find_lib_end(content)
    lib_text = content[:lib_end]
    
    all_pin_defs = {}
    
    for sym_m in re.finditer(r'\(symbol\s+"([^"]+)"', lib_text):
        sym_name = sym_m.group(1)
        end = find_balanced_end(lib_text, sym_m.start())
        section = lib_text[sym_m.start():end]
        
        pins = {}
        for pm in re.finditer(
            r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\)\s+\(length\s+([-\d.]+)\)'
            r'.*?\(name\s+"([^"]+)".*?\(number\s+"([^"]+)"',
            section, re.DOTALL
        ):
            pins[pm.group(7)] = {
                'x': float(pm.group(2)), 'y': float(pm.group(3)),
                'angle': int(pm.group(4)), 'len': float(pm.group(5)),
                'name': pm.group(6), 'type': pm.group(1)
            }
        all_pin_defs[sym_name] = pins
    
    instances = []
    for m in re.finditer(
        r'\(symbol\s+\(lib_id\s+"([^"]+)"\)\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\)',
        content[lib_end:]
    ):
        lib_id = m.group(1)
        sx, sy = float(m.group(2)), float(m.group(3))
        angle = int(m.group(4))
        
        abs_start = lib_end + m.start()
        end = find_balanced_end(content, abs_start)
        block = content[abs_start:end]
        
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', block)
        ref = ref_m.group(1) if ref_m else "?"
        val = val_m.group(1) if val_m else "?"
        pin_nums = re.findall(r'\(pin\s+"([^"]+)"\s+\(uuid', block)
        
        instances.append({
            'lib_id': lib_id, 'x': sx, 'y': sy,
            'angle': angle, 'ref': ref, 'value': val, 'pin_nums': pin_nums
        })
    
    return instances, all_pin_defs

def get_net_name(pname, ref, value):
    """Determine net name from pin name."""
    pn = pname.upper().strip()
    
    # Power pins - use standard KiCad power symbol names
    if pn in ('VA11',): return '+1V0_ANA'
    if pn in ('VA19',): return '+1V9_ANA'
    if pn in ('VD11',): return '+1V1_DIG'
    if pn in ('AGND', 'DGND', 'GND', 'PGND', 'AVSS', 'SGND', 'DAP', 'HEATSHINK'): return 'GND'
    if pn.startswith('PGND'): return 'GND'
    if pn.startswith('PVIN') or pn == 'VIN': return 'VIN'
    if pn in ('VCCDIG', 'VCCCP', 'VCCMASH', 'VCCBUF', 'VCCVCO', 'VCCVCO2'): return '+3V3'
    if pn.startswith('VCC'): return '+3V3'
    if pn in ('V+', 'VDD', 'BIAS', 'VREFA', 'VREF_OUTS', 'VREFD', 'DVDD', 'AVDD'): return '+3V3'
    if pn.startswith('LX') or pn.startswith('BST'): return f'{value}_{pn}'
    if pn in ('LDOBYP1', 'LDOBYP2'): return '+3V3'
    
    # ADC signals
    if pn in ('INA+',): return 'RF_IN_P'
    if pn in ('INA-',): return 'RF_IN_N'
    if pn in ('INB+',): return 'RF_INB_P'
    if pn in ('INB-',): return 'RF_INB_N'
    if pn in ('CLK+',): return 'ADC_CLK_P'
    if pn in ('CLK-',): return 'ADC_CLK_N'
    if pn in ('SYSREF+',): return 'ADC_SYSREF_P'
    if pn in ('SYSREF-',): return 'ADC_SYSREF_N'
    if pn in ('TMSTP+',): return 'ADC_SYNC_P'
    if pn in ('TMSTP-',): return 'ADC_SYNC_N'
    if pn in ('NCOA0', 'NCOA1', 'NCOB0', 'NCOB1', 'SYNCSE'): return 'GND'
    if pn == 'SCS': return 'SPI_CS_ADC'
    if pn == 'SCLK': return 'SPI_SCK'
    if pn == 'SDI': return 'SPI_MOSI'
    if pn == 'SDO': return 'SPI_MISO'
    if pn == 'PD': return 'ADC_PD'
    if pn == 'BG': return 'ADC_VBG'
    if pn == 'CALTRIG': return 'FPGA_CAL_TRIG'
    if pn == 'CALSTAT': return 'FPGA_CAL_STAT'
    if pn in ('TDIODE+',): return 'TEMP_DIODE_P'
    if pn in ('TDIODE-',): return 'TEMP_DIODE_N'
    if pn in ('ORA0',): return 'FPGA_ORA0'
    if pn in ('ORA1',): return 'FPGA_ORA1'
    if pn in ('ORB0',): return 'FPGA_ORB0'
    if pn in ('ORB1',): return 'FPGA_ORB1'
    
    for i in range(8):
        if pn == f'DA{i}+': return f'JESD_DA{i}_P'
        if pn == f'DA{i}-': return f'JESD_DA{i}_N'
        if pn == f'DB{i}+': return f'JESD_DB{i}_P'
        if pn == f'DB{i}-': return f'JESD_DB{i}_N'
    
    # Clock
    if pn in ('OSCINP', 'OSCIN'): return 'CLK_OSCIN_P'
    if pn in ('OSCINM',): return 'CLK_OSCIN_N'
    if pn in ('RFOUTAP',): return 'CLK_RFOUTA_P'
    if pn in ('RFOUTAM',): return 'CLK_RFOUTA_N'
    if pn in ('RFOUTBP',): return 'CLK_RFOUTB_P'
    if pn in ('RFOUTBM',): return 'CLK_RFOUTB_N'
    if pn in ('CPout', 'CPOUT', 'CPOUT1'): return 'PLL_CPOUT1'
    if pn == 'CPOUT2': return 'PLL_CPOUT2'
    if pn == 'VTUNE': return 'PLL_VTUNE'
    if pn == 'MUXout': return 'PLL_LOCK'
    if pn == 'CSB': return 'SPI_CS_LMX'
    if pn == 'SCK': return 'SPI_SCK'
    if pn == 'CAL': return 'LMX_CAL'
    if pn == 'SYNC': return 'LMX_SYNC'
    if pn in ('SYSREFREQ', 'SYNC/SYSREF_REQ'): return 'LMK_SYNC'
    if pn in ('RECAL_EN',): return 'GND'
    
    clk_names = {}
    for i in range(8):
        clk_names[f'CLKOUT{i}'] = f'LMK_CLK{i}_P'
        clk_names[f'CLKOUT{i}*'] = f'LMK_CLK{i}_N'
    if pn in clk_names: return clk_names[pn]
    if pn in ('CS*',): return 'SPI_CS_LMK'
    if pn == 'SDIO': return 'SPI_SDIO'
    if pn in ('RESET/GPO', 'RESET'): return 'LMK_RESET'
    
    # TPS power ICs
    if pn == 'EN': return f'EN_{ref}'
    if pn == 'OUTA': return f'{value}_OUTA'
    if pn == 'OUTB': return f'{value}_OUTB'
    if pn == 'SRA': return f'{value}_SRA'
    if pn == 'SRB': return f'{value}_SRB'
    if pn == 'VLDO': return f'{value}_VLDO'
    if pn == 'CS_ILIM': return f'{value}_CS'
    if pn == 'FAULT': return f'{value}_FAULT'
    if pn == 'REFCAP': return f'{value}_REFCAP'
    if pn == 'SS': return f'{value}_SS'
    if pn == 'VSENSE': return f'{value}_VSENSE'
    if pn == 'COMP': return f'{value}_COMP'
    if pn == 'RT': return f'{value}_RT'
    if pn == 'LEB': return f'{value}_LEB'
    if pn == 'HICC': return f'{value}_HICC'
    if pn == 'DCL': return f'{value}_DCL'
    if pn == 'PG': return f'{value}_PG'
    
    if pn == 'IN': return '+3V3'
    if pn == 'OUT': return f'{value}_OUT'
    if pn == 'OUTS': return f'{value}_OUT'
    if pn == 'FB_PG': return f'{value}_FB'
    if pn == 'FB': return f'{value}_FB'
    if pn == 'CLM': return f'{value}_CLM'
    if pn == 'CL': return f'{value}_CL'
    if pn == 'REF': return f'{value}_REF'
    if pn == 'SS_SET': return f'{value}_SS'
    if pn == 'STAB': return f'{value}_STAB'
    
    if pn.startswith('SENSE'): return f'{value}_{pn}'
    if pn == 'UP': return f'{value}_UP'
    if pn == 'DOWN': return f'{value}_DOWN'
    if pn in ('PULL_UP1', 'PULL_UP2'): return '+3V3'
    if pn == 'DLY_TMR': return f'{value}_DLY'
    if pn == 'REG_TMR': return f'{value}_REG'
    if pn == 'HYS': return f'{value}_HYS'
    if pn == 'FAULT_SEQ': return f'{value}_FAULT'
    if pn == 'PWRGD': return f'{value}_PWRGD'
    if pn == 'SEQ_DONE': return f'{value}_SEQ_DONE'
    
    if pn in ('NI',): return f'{value}_NI'
    if pn == 'VERR': return f'{value}_VERR'
    if pn == 'OR_VIN': return f'OR_{ref}'
    if pn == 'ENABLE': return f'EN_{ref}'
    if pn == 'FSEL': return '+3V3'
    if pn == 'SS_CAP': return f'{value}_SS'
    if pn == 'IMON': return f'{value}_IMON'
    if pn == 'PGOOD': return f'{value}_PGOOD'
    if pn == 'BUFOUT': return f'{value}_BUFOUT'
    if pn in ('BUFIN+',): return f'{value}_BUFIN_P'
    if pn in ('BUFIN-',): return f'{value}_BUFIN_N'
    if pn in ('SEL1', 'SEL2', 'DE', 'DESEL'): return '+3V3'
    if pn == 'OCSETA': return f'{value}_OCSETA'
    if pn == 'OCSETB': return f'{value}_OCSETB'
    
    if pn in ('IN+',): return 'ISENSE_P'
    if pn in ('IN-',): return 'ISENSE_N'
    
    if pn == 'VCONTROL': return 'VCXO_VCTRL'
    
    return pn.replace('/', '_').replace('*', '_N').replace('+', '_P').replace('-', '_N')

# Standard KiCad power symbol lib_symbols to add if needed
PWR_SYM_DEFS = {
    'GND': '    (symbol "power:GND" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes) (property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) hide)) (property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27)))) (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) (symbol "GND_0_1" (polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type none)))) (symbol "GND_1_1" (pin power_in line (at 0 0 270) (length 0) (name "GND" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))))',
    '+1V0': '    (symbol "power:+1V0" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes) (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide)) (property "Value" "+1V0" (at 0 3.81 0) (effects (font (size 1.27 1.27)))) (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) (symbol "+1V0_0_1" (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none)))) (symbol "+1V0_1_1" (pin power_in line (at 0 0 90) (length 0) (name "+1V0" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))))',
    '+1V8': '    (symbol "power:+1V8" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes) (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide)) (property "Value" "+1V8" (at 0 3.81 0) (effects (font (size 1.27 1.27)))) (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) (symbol "+1V8_0_1" (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none)))) (symbol "+1V8_1_1" (pin power_in line (at 0 0 90) (length 0) (name "+1V8" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))))',
    '+3V3': '    (symbol "power:+3V3" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes) (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide)) (property "Value" "+3V3" (at 0 3.81 0) (effects (font (size 1.27 1.27)))) (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) (symbol "+3V3_0_1" (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none)))) (symbol "+3V3_1_1" (pin power_in line (at 0 0 90) (length 0) (name "+3V3" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))))',
    '+2V5': '    (symbol "power:+2V5" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes) (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide)) (property "Value" "+2V5" (at 0 3.81 0) (effects (font (size 1.27 1.27)))) (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) (symbol "+2V5_0_1" (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none)))) (symbol "+2V5_1_1" (pin power_in line (at 0 0 90) (length 0) (name "+2V5" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))))',
    '+4V5': '    (symbol "power:+4V5" (power) (pin_names (offset 0)) (in_bom yes) (on_board yes) (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide)) (property "Value" "+4V5" (at 0 3.81 0) (effects (font (size 1.27 1.27)))) (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide)) (symbol "+4V5_0_1" (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none)))) (symbol "+4V5_1_1" (pin power_in line (at 0 0 90) (length 0) (name "+4V5" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))))',
}

PWR_SYMBOL_MAP = {
    'GND': 'GND', '+1V0': '+1V0', '+1V0_ANA': '+1V0', '+1V1_DIG': '+1V0',
    '+1V8': '+1V8', '+1V9_ANA': '+1V8', '+3V3': '+3V3', '+2V5': '+2V5',
    '+4V5': '+4V5', 'VIN': '+4V5',
}

def process_sheet(filepath):
    content = parse_sheet(filepath)
    instances, all_pin_defs = extract_all_pin_info(content)
    
    if not instances:
        return content, 0, set()
    
    lib_end = find_lib_end(content)
    
    # Step 1: Remove ALL labels, global_labels, wires, junctions, no_connects
    # from the section after lib_symbols (but keep symbol instances)
    clean_content = remove_elements_by_tag(
        content,
        ['label', 'global_label', 'wire', 'junction', 'no_connect']
    )
    
    # Step 2: For each pin, calculate absolute position and create wire + label
    new_elements = []
    connected_count = 0
    needed_power = set()
    
    for inst in instances:
        lib_id = inst['lib_id']
        if lib_id in all_pin_defs:
            pins = all_pin_defs[lib_id]
        elif lib_id.split(":")[-1] in all_pin_defs:
            pins = all_pin_defs[lib_id.split(":")[-1]]
        else:
            continue
        sx, sy = inst['x'], inst['y']
        
        for pnum, pin in pins.items():
            # Use ALL pins from lib_symbols, not just instance pin_nums
            px, py = pin['x'], pin['y']
            angle = pin['angle']
            pname = pin['name']
            ptype = pin['type']
            
            # Absolute pin endpoint (KiCad inverts Y: library Y=schematic Y)
            ex, ey = sx + px, sy - py
            net_name = get_net_name(pname, inst['ref'], inst['value'])
            
            # Wire goes outward from pin (away from symbol body)
            # KiCad Y-inversion: angle 90 wire goes +Y (down), 270 goes -Y (up)
            wire_len = 7.62
            if angle == 0:
                lx, ly = ex - wire_len, ey
            elif angle == 180:
                lx, ly = ex + wire_len, ey
            elif angle == 90:
                lx, ly = ex, ey + wire_len
            elif angle == 270:
                lx, ly = ex, ey - wire_len
            else:
                lx, ly = ex - wire_len, ey
            
            new_elements.append(
                f'(wire (pts (xy {ex:.4f} {ey:.4f}) (xy {lx:.4f} {ly:.4f})) '
                f'(stroke (width 0) (type default)) (uuid "{uid()}"))'
            )
            
            # Use label for ALL pins (power symbols don't connect via wires in netlist)
            new_elements.append(
                f'(label "{net_name}" (at {lx:.4f} {ly:.4f} 0) '
                f'(effects (font (size 1.27 1.27))) (uuid "{uid()}"))'
            )
            
            connected_count += 1
    
    # Step 3: Check which power lib_symbols are needed but missing
    lib_section = clean_content[:find_lib_end(clean_content)]
    defined_pwr = set(re.findall(r'\(symbol "power:([^"]+)"', lib_section))
    missing_pwr = needed_power - defined_pwr
    
    if missing_pwr:
        insert_at = find_lib_end(clean_content)
        insert_at -= 1  # Before the closing ) of lib_symbols
        add_text = ""
        for pw in missing_pwr:
            if pw in PWR_SYM_DEFS:
                add_text += "\n" + PWR_SYM_DEFS[pw]
        clean_content = clean_content[:insert_at] + add_text + clean_content[insert_at:]
    
    # Step 4: Insert new elements before (sheet_instances
    insert_pos = clean_content.rfind('(sheet_instances')
    if insert_pos == -1:
        insert_pos = len(clean_content) - 2
    
    insert_text = '\n  ' + '\n  '.join(new_elements) + '\n  '
    new_content = clean_content[:insert_pos] + insert_text + clean_content[insert_pos:]
    
    return new_content, connected_count, needed_power

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    sheets = sorted(glob.glob(os.path.join(SCHEMA_DIR, "Sheet*.kicad_sch")))
    print(f"Processing {len(sheets)} sheets...\n")
    
    total = 0
    for sheet in sheets:
        name = os.path.basename(sheet)
        new_content, count, needed_pwr = process_sheet(sheet)
        if count > 0:
            with open(sheet, 'w') as f:
                f.write(new_content)
            print(f"  {name}: {count} pins connected, power: {sorted(needed_pwr)}")
            total += count
        else:
            print(f"  {name}: no changes")
    
    print(f"\nTotal: {total} pin connections")
    
    # Verify
    print("\nVerifying with KiCad CLI...")
    for sheet in sheets:
        name = os.path.basename(sheet)
        out = f"/tmp/verify3_{name.replace('.kicad_sch','.pdf')}"
        result = os.popen(f'kicad-cli sch export pdf --output "{out}" "{sheet}" 2>&1').read()
        status = "OK" if "Done" in result else f"FAIL: {result.strip()[:80]}"
        print(f"  {name}: {status}")

if __name__ == "__main__":
    main()
