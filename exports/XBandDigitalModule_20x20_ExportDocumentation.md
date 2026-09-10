# XBandDigitalModule_20x20 - Export Documentation

## Document Information
| Field | Value |
|---|---|
| Document ID | XBDM-DOC-012 |
| Version | 1.0 |
| Date | 2026-09-09 |
| Classification | ITAR Restricted |

## 1. Export Files Summary

### 1.1 PDF Exports

| File | Description | Status |
|---|---|---|
| XBandDigitalModule_20x20_Schematic.pdf | Complete schematic PDF | Generated |
| XBandDigitalModule_20x20_PCB_Top.pdf | PCB top layer view | Generated |
| XBandDigitalModule_20x20_PCB_Bottom.pdf | PCB bottom layer view | Generated |
| XBandDigitalModule_20x20_PCB_Assembly.pdf | Assembly drawing | Generated |
| XBandDigitalModule_20x20_Mechanical_PDF.pdf | Mechanical drawing PDF | Generated |
| XBandDigitalModule_20x20_TechnicalDescription.pdf | Technical description | Generated |
| XBandDigitalModule_20x20_WCA.pdf | Worst-case analysis | Generated |
| XBandDigitalModule_20x20_PSA.pdf | Parts stress analysis | Generated |
| XBandDigitalModule_20x20_ICD_Mechanical.pdf | Mechanical ICD | Generated |
| XBandDigitalModule_20x20_ICD_VHDL.pdf | VHDL ICD with register map | Generated |

### 1.2 Design Files

| File | Description | Status |
|---|---|---|
| XBandDigitalModule_20x20_Schematic.kicad_sch | KiCad schematic | Generated |
| XBandDigitalModule_20x20_PCB.kicad_pcb | KiCad PCB layout | Generated |
| XBandDigitalModule_20x20_Mechanical.step | 3D mechanical model | Generated |
| XBandDigitalModule_20x20_Mechanical.3mf | 3D printable model | Generated |

### 1.3 Manufacturing Files

| File | Description | Status |
|---|---|---|
| XBandDigitalModule_20x20_Gerber.zip | Gerber files for fabrication | Generated |
| XBandDigitalModule_20x20_Drill.zip | Drill files | Generated |
| XBandDigitalModule_20x20_BOM.csv | Bill of materials | Generated |
| XBandDigitalModule_20x20_PickPlace.csv | Component placement | Generated |

### 1.4 Datasheets

| File | Component |
|---|---|
| ADC12DJ5200-SP.pdf | Texas Instruments ADC |
| XQRVC1902.pdf | AMD Versal FPGA |
| LMX2615-SP.pdf | Texas Instruments Clock Synth |
| LMK04832-SP.pdf | Texas Instruments Clock Dist |
| TPS7H5002-SP.pdf | Texas Instruments Buck Controller |
| ISL70003ASEH.pdf | Renesas Buck Regulator |
| TPS7H1111-SP.pdf | Texas Instruments LDO |
| TPS7H3014-SP.pdf | Texas Instruments Sequencer |

## 2. Schematic Description

### 2.1 Schematic Pages

| Page | Title | Description |
|---|---|---|
| 1 | Title Block | Project information, revision history |
| 2 | System Block Diagram | High-level architecture |
| 3 | RF Input | SMA, BPF, balun |
| 4 | ADC | ADC12DJ5200-SP, support circuits |
| 5 | FPGA Core | XQRVC1902, power pins |
| 6 | FPGA I/O | JESD204C, SpaceWire, GPIO |
| 7 | Clock | LMX2615-SP, LMK04832-SP |
| 8 | Power - Input | Reverse polarity, EMI filter |
| 9 | Power - Buck | TPS7H5002-SP, ISL70003ASEH |
| 10 | Power - LDO | TPS7H1111-SP, TPS7H1121-SP |
| 11 | Power - Sequencer | TPS7H3014-SP |
| 12 | Connectors | JTAG, Debug, Power, SpaceWire |
| 13 | Test Points | TP locations, debug signals |

### 2.2 Key Schematic Notes

1. **Separation**: Analog (RF, ADC, clock) separated from digital (FPGA, SpaceWire)
2. **Grounding**: Star ground topology, single point connection
3. **Decoupling**: 100nF + 10µF per power pin
4. **Impedance**: 50Ω single-ended, 100Ω differential
5. **ESD Protection**: TVS on all external connectors

## 3. PCB Layout Description

### 3.1 Layer Stackup

| Layer | Name | Function | Copper |
|---|---|---|---|
| 1 | Top Signal | Components, RF traces | 35µm |
| 2 | Ground 1 | Continuous ground plane | 35µm |
| 3 | Signal 2 | Signal routing | 35µm |
| 4 | Power 1 | 1.0V core plane | 70µm |
| 5 | Signal 3 | Signal routing | 35µm |
| 6 | Ground 2 | Continuous ground plane | 35µm |
| 7 | Ground 3 | Continuous ground plane | 35µm |
| 8 | Power 2 | 1.8V/3.3V plane | 70µm |
| 9 | Signal 4 | Signal routing | 35µm |
| 10 | Ground 4 | Continuous ground plane | 35µm |
| 11 | Signal 5 | Signal routing | 35µm |
| 12 | Bottom Signal | Components, debug | 35µm |

### 3.2 Component Placement

| Area | X (mm) | Y (mm) | Components |
|---|---|---|---|
| RF Input | 0-30 | 85-115 | SMA, BPF, balun, ADC |
| FPGA Core | 60-140 | 60-140 | XQRVC1902, DDR4, decoupling |
| Clock | 170-200 | 85-115 | LMX2615-SP, LMK04832-SP |
| Power | 80-120 | 0-30 | Buck, LDO, inductors |
| Connectors | Edges | - | SMA, power, JTAG, SpaceWire |

### 3.3 Routing Guidelines

- **RF traces**: 50Ω, no vias, guard traces
- **JESD204C**: 100Ω differential, length matched ±5 ps
- **Clock**: 100Ω differential, guarded
- **Power**: Wide traces, multiple vias to plane
- **High-speed**: Back-drilled, via stitching

## 4. Mechanical Drawing Description

### 4.1 Views

| View | Description |
|---|---|
| Top View | PCB outline, component locations, mounting holes |
| Bottom View | Bottom components, test points |
| Front View | Height profile, connector positions |
| Side View | PCB + heatsink assembly |
| Exploded View | Assembly sequence |

### 4.2 Dimensions

- **PCB**: 200mm x 200mm x 2.4mm
- **Chassis**: 205mm x 205mm x 15mm (base plate)
- **Assembly**: 205mm x 205mm x 25mm (max)

### 4.3 Mounting

- **Primary**: 4x M3 (corners, 10mm from edges)
- **Secondary**: 2x M2.5 (short sides, center)
- **Torque**: M3: 0.5 N·m, M2.5: 0.3 N·m

## 5. Datasheet Collection

### 5.1 Component Datasheets

All component datasheets have been collected and stored in:
```
exports/XBandDigitalModule_20x20_Datasheets/
├── ADC12DJ5200-SP.pdf
├── XQRVC1902.pdf
├── LMX2615-SP.pdf
├── LMK04832-SP.pdf
├── TPS7H5002-SP.pdf
├── ISL70003ASEH.pdf
├── TPS7H1111-SP.pdf
└── TPS7H3014-SP.pdf
```

## 6. Revision History

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | 2026-09-09 | Documentation Engineer | Initial release |

---
*End of Document*
