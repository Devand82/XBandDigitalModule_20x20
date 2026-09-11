#!/usr/bin/env python3
"""Add wire connections to all schematic sheets - version 2 with proper debugging."""
import re, glob, uuid, os

SCHEMA_DIR = "schematic"
WIRE_LEN = 5.08  # 200 mil stub wires

def uid():
    return str(uuid.uuid4()).replace("-","")[:32]

def extract_lib_symbols(content):
    """Extract lib_symbols section text."""
    m = content.find('(lib_symbols')
    if m == -1:
        return "", 0, 0
    depth = 0
    for i in range(m, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return content[m:i+1], m, i+1
    return "", 0, 0

def extract_symbol_pins(lib_text, sym_name):
    """Extract pins from a specific symbol in lib_symbols."""
    # Find the symbol definition
    pat = re.compile(r'\(symbol\s+"' + re.escape(sym_name) + r'"')
    m = pat.search(lib_text)
    if not m:
        return {}
    
    # Find the extent of this symbol definition
    depth = 0
    start = m.start()
    end = start
    for i in range(start, len(lib_text)):
        if lib_text[i] == '(':
            depth += 1
        elif lib_text[i] == ')':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    
    section = lib_text[start:end]
    pins = {}
    
    # Match pin definitions
    for pm in re.finditer(
        r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\)\s+\(length\s+([-\d.]+)\)'
        r'.*?\(name\s+"([^"]+)".*?\(number\s+"([^"]+)"',
        section, re.DOTALL
    ):
        ptype = pm.group(1)
        px, py = float(pm.group(2)), float(pm.group(3))
        angle = int(pm.group(4))
        plen = float(pm.group(5))
        pname = pm.group(6)
        pnum = pm.group(7)
        pins[pnum] = {'x': px, 'y': py, 'angle': angle, 'len': plen, 'type': ptype, 'name': pname}
    
    return pins

def find_symbol_instances(content):
    """Find all symbol instances in the schematic (not lib_symbols)."""
    instances = []
    # Find the end of lib_symbols first
    _, _, lib_end = extract_lib_symbols(content)
    search_content = content[lib_end:]
    offset = lib_end
    
    for m in re.finditer(
        r'\(symbol\s+\(lib_id\s+"([^"]+)"\)\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\)',
        search_content
    ):
        lib_id = m.group(1)
        x, y = float(m.group(2)), float(m.group(3))
        angle = int(m.group(4))
        
        # Get the full instance block
        abs_start = offset + m.start()
        depth = 0
        for i in range(abs_start, len(content)):
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
                if depth == 0:
                    break
        block = content[abs_start:i+1]
        
        # Extract reference and pin list
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', block)
        ref = ref_m.group(1) if ref_m else "?"
        val = val_m.group(1) if val_m else "?"
        pin_nums = re.findall(r'\(pin\s+"([^"]+)"\s+\(uuid', block)
        
        instances.append({
            'lib_id': lib_id, 'x': x, 'y': y, 'angle': angle,
            'ref': ref, 'value': val, 'pin_nums': pin_nums
        })
    
    return instances

def find_existing_labels(content):
    """Find all labels, global_labels, and power symbols."""
    labels = set()
    for m in re.finditer(r'\(label\s+"([^"]+)"', content):
        labels.add(m.group(1))
    for m in re.finditer(r'\(global_label\s+"([^"]+)"', content):
        labels.add(m.group(1))
    return labels

def get_net_name(pin_name, ref, value):
    """Determine net name from pin name, reference and value."""
    pn = pin_name.upper().strip()
    val = value.upper().strip()
    ref_u = ref.upper().strip()
    
    # Power supply pins
    power_map = {
        'VA11': '+1V0_ANA', 'VA19': '+1V9_ANA', 'VD11': '+1V1_DIG',
        'AGND': 'GND', 'DGND': 'GND', 'GND': 'GND', 'PGND': 'GND',
        'AVSS': 'GND', 'SGND': 'GND',
        'VIN': 'VIN', 'PVIN': 'VIN',
        'VCCDIG': '+3V3', 'VCCCP': '+3V3', 'VCCMASH': '+3V3', 'VCCBUF': '+3V3',
        'VCCVCO': '+3V3', 'VCCVCO2': '+3V3',
        'VCC1_VCO': '+3V3', 'VCC2_CG1': '+3V3', 'VCC3_SYSREF': '+3V3',
        'VCC4_CG2': '+3V3', 'VCC5_DIG': '+3V3', 'VCC6_PLL1': '+3V3',
        'VCC7_OSCOUT': '+3V3', 'VCC8_OSCIN': '+3V3', 'VCC9_CP2': '+3V3',
        'VCC10_PLL2': '+3V3', 'VCC11_CG3': '+3V3', 'VCC12_CG0': '+3V3',
        'V+': '+3V3', 'VREF': '+3V3', 'VDD': '+3V3', 'BIAS': '+3V3',
        'VREFA': '+3V3', 'VREF_OUTS': '+3V3', 'VREFD': '+3V3',
        'DVDD': '+3V3', 'AVDD': '+3V3',
    }
    if pn in power_map:
        return power_map[pn]
    
    # PVINx -> VIN
    if pn.startswith('PVIN'):
        return 'VIN'
    # LXx -> inductor node
    if pn.startswith('LX'):
        return f'{val}_{pn}'
    # PGNDx -> GND
    if pn.startswith('PGND'):
        return 'GND'
    
    # ADC12DJ5200-SP specific
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
    
    # JESD204C lanes
    for i in range(8):
        if pn == f'DA{i}+': return f'JESD_DA{i}_P'
        if pn == f'DA{i}-': return f'JESD_DA{i}_N'
        if pn == f'DB{i}+': return f'JESD_DB{i}_P'
        if pn == f'DB{i}-': return f'JESD_DB{i}_N'
    
    # Clock IC pins
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
    if pn == 'SDI': return 'SPI_MOSI'
    if pn == 'CAL': return 'LMX_CAL'
    if pn == 'SYNC': return 'LMX_SYNC'
    if pn in ('SYSREFREQ', 'SYNC/SYSREF_REQ'): return 'LMK_SYNC'
    if pn in ('RECAL_EN',): return 'GND'
    
    # LMK04832 outputs
    clk_map = {
        'CLKOUT0': 'LMK_CLK0_P', 'CLKOUT0*': 'LMK_CLK0_N',
        'CLKOUT1': 'LMK_CLK1_P', 'CLKOUT1*': 'LMK_CLK1_N',
        'CLKOUT2': 'LMK_CLK2_P', 'CLKOUT2*': 'LMK_CLK2_N',
        'CLKOUT3': 'LMK_CLK3_P', 'CLKOUT3*': 'LMK_CLK3_N',
        'CLKOUT4': 'LMK_CLK4_P', 'CLKOUT4*': 'LMK_CLK4_N',
        'CLKOUT5': 'LMK_CLK5_P', 'CLKOUT5*': 'LMK_CLK5_N',
        'CLKOUT6': 'LMK_CLK6_P', 'CLKOUT6*': 'LMK_CLK6_N',
        'CLKOUT7': 'LMK_CLK7_P', 'CLKOUT7*': 'LMK_CLK7_N',
        'CLKOUT8': 'LMK_CLK8_P', 'CLKOUT8*': 'LMK_CLK8_N',
        'CLKOUT9': 'LMK_CLK9_P', 'CLKOUT9*': 'LMK_CLK9_N',
        'CLKOUT10': 'LMK_CLK10_P', 'CLKOUT10*': 'LMK_CLK10_N',
        'CLKOUT11': 'LMK_CLK11_P', 'CLKOUT11*': 'LMK_CLK11_N',
        'CLKOUT12': 'LMK_CLK12_P', 'CLKOUT12*': 'LMK_CLK12_N',
        'CLKOUT13': 'LMK_CLK13_P', 'CLKOUT13*': 'LMK_CLK13_N',
    }
    if pn in clk_map:
        return clk_map[pn]
    if pn in ('CS*',): return 'SPI_CS_LMK'
    if pn == 'SDIO': return 'SPI_SDIO'
    if pn in ('RESET/GPO', 'RESET'): return 'LMK_RESET'
    if pn == 'STATUS_LD1': return 'LMK_LD1'
    if pn == 'STATUS_LD2': return 'LMK_LD2'
    if pn in ('FIN0', 'FIN0*'): return 'CLK_FIN0'
    if pn in ('FIN1', 'FIN1*', 'CLKIN1', 'CLKIN1*'): return 'CLK_FIN1'
    if pn in ('CLKIN0', 'CLKIN0*'): return 'CLK_REFIN'
    if pn in ('OSCCOUT', 'OSCCOUT*'): return 'LMK_OSCOUT'
    if pn in ('CLKIN_SEL0', 'CLKIN_SEL1'): return 'GND'
    if pn in ('LDOBYP1',): return 'LMK_LDOBYP1'
    if pn in ('LDOBYP2',): return 'LMK_LDOBYP2'
    
    # TPS7H500x
    if pn == 'EN': return f'EN_{ref}'
    if pn == 'RT': return f'{val}_RT'
    if pn in ('PS',): return f'{val}_PS'
    if pn in ('SP',): return f'{val}_SP'
    if pn == 'LEB': return f'{val}_LEB'
    if pn == 'HICC': return f'{val}_HICC'
    if pn == 'SYNC_TPS': return f'{val}_SYNC'
    if pn == 'DCL': return f'{val}_DCL'
    if pn == 'OUTA': return f'{val}_OUTA'
    if pn == 'OUTB': return f'{val}_OUTB'
    if pn == 'SRA': return f'{val}_SRA'
    if pn == 'SRB': return f'{val}_SRB'
    if pn == 'VLDO': return f'{val}_VLDO'
    if pn == 'CS_ILIM': return f'{val}_CS'
    if pn == 'FAULT': return f'{val}_FAULT'
    if pn == 'REFCAP': return f'{val}_REFCAP'
    if pn == 'RSC': return f'{val}_RSC'
    if pn == 'SS': return f'{val}_SS'
    if pn == 'VSENSE': return f'{val}_VSENSE'
    if pn == 'COMP': return f'{val}_COMP'
    
    # ISL70003ASEH
    if pn == 'NI': return f'{val}_NI'
    if pn == 'FB': return f'{val}_FB'
    if pn == 'VERR': return f'{val}_VERR'
    if pn == 'OR_VIN': return f'OR_{ref}'
    if pn == 'ENABLE': return f'EN_{ref}'
    if pn == 'FSEL': return '+3V3'
    if pn == 'SYNC_ISL': return f'{val}_SYNC'
    if pn == 'SS_CAP': return f'{val}_SS'
    if pn == 'IMON': return f'{val}_IMON'
    if pn == 'PGOOD': return f'{val}_PGOOD'
    if pn == 'BUFOUT': return f'{val}_BUFOUT'
    if pn in ('BUFIN+',): return f'{val}_BUFIN_P'
    if pn in ('BUFIN-',): return f'{val}_BUFIN_N'
    if pn in ('SEL1', 'SEL2', 'DE'): return '+3V3'
    if pn == 'DESEL': return '+3V3'
    if pn == 'OCSETA': return f'{val}_OCSETA'
    if pn == 'OCSETB': return f'{val}_OCSETB'
    
    # TPS7H1111-SP
    if pn == 'IN': return '+3V3'
    if pn == 'OUT': return f'{val}_OUT'
    if pn == 'OUTS': return f'{val}_OUT_SENSE'
    if pn == 'FB_PG': return f'{val}_FB'
    if pn == 'CLM': return f'{val}_CLM'
    if pn == 'REF': return f'{val}_REF'
    if pn == 'SS_SET': return f'{val}_SS'
    if pn == 'STAB': return f'{val}_STAB'
    
    # TPS7H1121-SP
    if pn == 'CL': return f'{val}_CL'
    
    # TPS7H3014-SP
    if pn.startswith('SENSE'): return f'{val}_{pn}'
    if pn == 'UP': return f'{val}_UP'
    if pn == 'DOWN': return f'{val}_DOWN'
    if pn in ('PULL_UP1', 'PULL_UP2'): return '+3V3'
    if pn == 'DLY_TMR': return f'{val}_DLY'
    if pn == 'REG_TMR': return f'{val}_REG'
    if pn == 'HYS': return f'{val}_HYS'
    if pn == 'FAULT_SEQ': return f'{val}_FAULT'
    if pn == 'PWRGD': return f'{val}_PWRGD'
    if pn == 'SEQ_DONE': return f'{val}_SEQ_DONE'
    if pn == 'REFCAP': return f'{val}_REFCAP'
    if pn == 'VLDO': return f'{val}_VLDO'
    
    # INA214
    if pn in ('IN+',): return 'ISENSE_P'
    if pn in ('IN-',): return 'ISENSE_N'
    if pn == 'OUT': return 'ISENSE_OUT'
    if pn == 'REF': return 'GND'
    
    # CVHD-950
    if pn == 'VCONTROL': return 'VCXO_VCTRL'
    if pn == 'OUT': return 'VCXO_OUT'
    
    # XQRVC1902 FPGA
    if 'JESD' in pn.upper() or 'TX' in pn.upper() or 'RX' in pn.upper():
        return pn.replace('/', '_').replace('*', '_N')
    if 'SPW' in pn.upper():
        return pn.replace('/', '_').replace('*', '_N')
    if 'GPIO' in pn.upper():
        return pn.replace('/', '_').replace('*', '_N')
    
    # Default: clean up pin name
    return pn.replace('/', '_').replace('*', '_N').replace('+', '_P').replace('-', '_N')

def make_power_sym(name, x, y):
    """Generate power symbol text."""
    # Try to use existing power symbols from lib_symbols
    pwr_symbols = {
        'GND': 'GND', '+1V0': '+1V0', '+1V0_ANA': '+1V0', '+1V1_DIG': '+1V0',
        '+1V8': '+1V8', '+1V8_DIG': '+1V8', '+3V3': '+3V3', '+2V5': '+2V5',
        '+4V5': '+4V5', 'VIN': '+4V5', '+1V9_ANA': '+1V8',
    }
    pwr_val = pwr_symbols.get(name, name)
    if pwr_val not in pwr_symbols.values() and not pwr_val.startswith('+'):
        pwr_val = 'GND'
    
    ref_id = uid()
    pin_id = uid()
    return (
        f'(symbol (lib_id "power:{pwr_val}") (at {x:.2f} {y:.2f} 0) (unit 1)\n'
        f'      (in_bom yes) (on_board yes) (dnp no)\n'
        f'      (uuid "{ref_id}")\n'
        f'      (property "Reference" "#PWR{uid()[:3]}" (at {x:.2f} {y-3.81:.2f} 0) (effects (font (size 1.27 1.27)) hide))\n'
        f'      (property "Value" "{pwr_val}" (at {x:.2f} {y+3.81:.2f} 0) (effects (font (size 1.27 1.27))))\n'
        f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
        f'      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
        f'      (pin "1" (uuid "{pin_id}"))\n'
        f'    )'
    )

def process_sheet(filepath):
    """Add wires and labels to a sheet."""
    with open(filepath) as f:
        content = f.read()
    
    lib_text, _, lib_end = extract_lib_symbols(content)
    instances = find_symbol_instances(content)
    
    if not instances:
        return content, 0
    
    new_elements = []
    wire_count = 0
    
    for inst in instances:
        lib_id = inst['lib_id']
        sym_name = lib_id.split(":")[-1] if ":" in lib_id else lib_id
        full_name = lib_id
        sx, sy = inst['x'], inst['y']
        
        # Extract pins from lib_symbols
        pins = extract_symbol_pins(lib_text, full_name)
        if not pins:
            pins = extract_symbol_pins(lib_text, sym_name)
        
        for pnum in inst['pin_nums']:
            if pnum not in pins:
                continue
            
            pin = pins[pnum]
            px, py = pin['x'], pin['y']
            angle = pin['angle']
            plen = pin['len']
            ptype = pin['type']
            pname = pin['name']
            
            # Absolute pin endpoint (where wire connects)
            ex, ey = sx + px, sy + py
            
            # Determine net name
            net_name = get_net_name(pname, inst['ref'], inst['value'])
            
            # Calculate wire stub endpoint
            if angle == 0:    # pin extends right into symbol body
                lx, ly = ex - WIRE_LEN, ey  # wire goes LEFT from pin
            elif angle == 180:  # pin extends left into symbol body
                lx, ly = ex + WIRE_LEN, ey  # wire goes RIGHT from pin
            elif angle == 90:   # pin extends up into symbol body
                lx, ly = ex, ey - WIRE_LEN  # wire goes DOWN
            elif angle == 270:  # pin extends down into symbol body
                lx, ly = ex, ey + WIRE_LEN  # wire goes UP
            else:
                lx, ly = ex + WIRE_LEN, ey
            
            # Add wire
            new_elements.append(
                f'(wire (pts (xy {ex:.2f} {ey:.2f}) (xy {lx:.2f} {ly:.2f})) '
                f'(stroke (width 0) (type default)) (uuid "{uid()}"))'
            )
            wire_count += 1
            
            # Add net label or power symbol
            if ptype == 'power_in':
                new_elements.append(make_power_sym(net_name, lx, ly))
            else:
                # Check if we need a global label (跨sheet signals)
                global_nets = {
                    'RF_IN_P', 'RF_IN_N', 'ADC_CLK_P', 'ADC_CLK_N', 'ADC_SYSREF_P', 'ADC_SYSREF_N',
                    'SPI_CS_ADC', 'SPI_SCK', 'SPI_MOSI', 'SPI_MISO', 'ADC_PD',
                    'FPGA_CAL_TRIG', 'FPGA_CAL_STAT', 'ADC_SYNC_P', 'ADC_SYNC_N',
                    'FPGA_ORA0', 'FPGA_ORA1', 'FPGA_ORB0', 'FPGA_ORB1',
                    'LMK_CLK0_P', 'LMK_CLK0_N', 'LMK_CLK1_P', 'LMK_CLK1_N',
                    'LMK_CLK2_P', 'LMK_CLK2_N', 'LMK_CLK4_P', 'LMK_CLK4_N',
                    'SPI_CS_LMK', 'SPI_CS_LMX', 'SPI_SDIO',
                    'LMK_RESET', 'LMK_SYNC', 'LMX_CAL', 'LMX_SYNC',
                    'PLL_LOCK', 'CLK_OSCIN_P', 'CLK_OSCIN_N',
                    'CLK_RFOUTA_P', 'CLK_RFOUTA_N',
                }
                # JESD lanes
                for i in range(8):
                    global_nets.add(f'JESD_DA{i}_P')
                    global_nets.add(f'JESD_DA{i}_N')
                    global_nets.add(f'JESD_DB{i}_P')
                    global_nets.add(f'JESD_DB{i}_N')
                # SpaceWire
                for i in range(1,3):
                    global_nets.add(f'SPW_TX{i}_P')
                    global_nets.add(f'SPW_TX{i}_N')
                    global_nets.add(f'SPW_RX{i}_P')
                    global_nets.add(f'SPW_RX{i}_N')
                
                if net_name in global_nets:
                    just = 'left' if angle in (0, 270) else 'right'
                    new_elements.append(
                        f'(global_label "{net_name}" (shape bidirectional) '
                        f'(at {lx:.2f} {ly:.2f} 0) '
                        f'(effects (font (size 1.27 1.27)) (justify {just})) '
                        f'(uuid "{uid()}"))'
                    )
                else:
                    new_elements.append(
                        f'(label "{net_name}" (at {lx:.2f} {ly:.2f} 0) '
                        f'(effects (font (size 1.27 1.27))) (uuid "{uid()}"))'
                    )
    
    if new_elements:
        # Find insertion point (before sheet_instances)
        insert_pos = content.rfind('(sheet_instances')
        if insert_pos == -1:
            insert_pos = len(content) - 2
        
        insert_text = '\n  ' + '\n  '.join(new_elements) + '\n  '
        content = content[:insert_pos] + insert_text + content[insert_pos:]
    
    return content, wire_count

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    sheets = sorted(glob.glob(os.path.join(SCHEMA_DIR, "Sheet*.kicad_sch")))
    print(f"Processing {len(sheets)} sheets...\n")
    
    total_wires = 0
    for sheet in sheets:
        name = os.path.basename(sheet)
        new_content, wire_count = process_sheet(sheet)
        
        if wire_count > 0:
            with open(sheet, 'w') as f:
                f.write(new_content)
            print(f"  {name}: +{wire_count} wires")
            total_wires += wire_count
        else:
            print(f"  {name}: no changes")
    
    print(f"\nTotal: {total_wires} wires added")
    
    # Verify
    print("\nVerifying with KiCad CLI...")
    for sheet in sheets:
        name = os.path.basename(sheet)
        out = f"/tmp/verify_{name.replace('.kicad_sch','.pdf')}"
        result = os.popen(f'kicad-cli sch export pdf --output "{out}" "{sheet}" 2>&1').read()
        status = "OK" if "Done" in result else f"FAIL: {result.strip()[:80]}"
        print(f"  {name}: {status}")

if __name__ == "__main__":
    main()
