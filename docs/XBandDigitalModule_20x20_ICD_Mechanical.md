# XBandDigitalModule_20x20 - ICD Mechanical

## Document Information
| Field | Value |
|---|---|
| Document ID | XBDM-DOC-008 |
| Version | 1.0 |
| Date | 2026-09-09 |
| Classification | ITAR Restricted |
| Status | Preliminary Design Review |

## 1. General Dimensions

### 1.1 Module Outline

| Parameter | Nominal | Tolerance | Unit |
|---|---|---|---|
| Length | 200.00 | ±0.10 | mm |
| Width | 200.00 | ±0.10 | mm |
| Height (max) | 25.00 | ±0.50 | mm |
| PCB Thickness | 2.40 | ±0.15 | mm |
| Weight (max) | 500 | - | g |

### 1.2 Mechanical Drawing Reference

```
                    ┌────────────────────────────────────────────┐
                    │            200.00 ± 0.10                   │
                    │◄──────────────────────────────────────────►│
                    │                                            │
    ┌───────────────┼────────────────────────────────────────────┼───────────────┐ ▲
    │               │                                            │               │ │
    │   ┌───────┐   │                                            │   ┌───────┐   │ │
    │   │ F1    │   │                                            │   │ F2    │   │ │
    │   │ M3    │   │                                            │   │ M3    │   │ │
    │   └───────┘   │                                            │   └───────┘   │ │
    │               │                                            │               │ │
    │               │                                            │               │ │
    │               │                                            │               │ │
    │               │            XBAND DIGITAL MODULE            │               │ │
    │               │                 20x20 cm                   │               │ 200.00
    │               │                                            │               │ ± 0.10
    │               │                                            │               │ │
    │               │                                            │               │ │
    │               │                                            │               │ │
    │               │                                            │               │ │
    │   ┌───────┐   │                                            │   ┌───────┐   │ │
    │   │ F3    │   │                                            │   │ F4    │   │ │
    │   │ M3    │   │                                            │   │ M3    │   │ │
    │   └───────┘   │                                            │   └───────┘   │ │
    │               │                                            │               │ │
    └───────────────┼────────────────────────────────────────────┼───────────────┘ ▼
                    │                                            │
                    └────────────────────────────────────────────┘
```

## 2. Mounting Holes

### 2.1 Primary Mounting Holes (4x M3)

| Hole | X Position | Y Position | Diameter | Type | Plating |
|---|---|---|---|---|---|
| F1 | 10.00 ± 0.05 | 10.00 ± 0.05 | 3.20 +0.10/-0.00 | Through | Copper |
| F2 | 190.00 ± 0.05 | 10.00 ± 0.05 | 3.20 +0.10/-0.00 | Through | Copper |
| F3 | 10.00 ± 0.05 | 190.00 ± 0.05 | 3.20 +0.10/-0.00 | Through | Copper |
| F4 | 190.00 ± 0.05 | 190.00 ± 0.05 | 3.20 +0.10/-0.00 | Through | Copper |

### 2.2 Secondary Mounting Holes (2x M2.5)

| Hole | X Position | Y Position | Diameter | Type | Plating |
|---|---|---|---|---|---|
| F5 | 100.00 ± 0.10 | 5.00 ± 0.10 | 2.70 +0.10/-0.00 | Through | Copper |
| F6 | 100.00 ± 0.10 | 195.00 ± 0.10 | 2.70 +0.10/-0.00 | Through | Copper |

### 2.3 Mounting Hole Keep-Out

| Hole | Keep-Out Radius | Layers | Notes |
|---|---|---|---|
| F1-F4 | 5.00 mm | All | No components, traces, or vias |
| F5-F6 | 4.00 mm | All | No components, traces, or vias |

## 3. Connector Locations

### 3.1 RF Connector (SMA)

| Parameter | Value | Tolerance |
|---|---|---|
| Type | SMA female, edge mount | - |
| Position X | 5.00 mm | ±0.10 mm |
| Position Y | 100.00 mm | ±0.10 mm |
| Orientation | Horizontal, left edge | - |
| Impedance | 50Ω | - |
| Frequency Range | DC - 18 GHz | - |

### 3.2 Power Connector (MIL-DTL-38999)

| Parameter | Value | Tolerance |
|---|---|---|
| Type | MIL-DTL-38999 Series I | - |
| Position X | 100.00 mm | ±0.10 mm |
| Position Y | 5.00 mm | ±0.10 mm |
| Orientation | Vertical, bottom edge | - |
| Pin Count | 4 (VIN, GND, GND, EP) | - |
| Current Rating | 75A per contact | - |

### 3.3 JTAG Connector

| Parameter | Value | Tolerance |
|---|---|---|
| Type | Box header, 14-pin | - |
| Position X | 195.00 mm | ±0.10 mm |
| Position Y | 180.00 mm | ±0.10 mm |
| Orientation | Horizontal, right edge | - |
| Pinout | Standard JTAG (TDI, TDO, TMS, TCK, TRST, GND) | - |

### 3.4 SpaceWire Connector

| Parameter | Value | Tolerance |
|---|---|---|
| Type | MIL-DTL-38999 Series I | - |
| Position X | 195.00 mm | ±0.10 mm |
| Position Y | 100.00 mm | ±0.10 mm |
| Orientation | Vertical, right edge | - |
| Pin Count | 8 (2 links: Data+, Data-, Strobe+, Strobe-, GND) | - |
| Data Rate | 100 Mbps | - |

### 3.5 Debug Connector

| Parameter | Value | Tolerance |
|---|---|---|
| Type | Box header, 10-pin | - |
| Position X | 195.00 mm | ±0.10 mm |
| Position Y | 20.00 mm | ±0.10 mm |
| Orientation | Horizontal, right edge | - |
| Signals | UART (TX, RX), SPI (MOSI, MISO, SCK, CS), I2C (SDA, SCL), GND | - |

## 4. Keep-Out Zones

### 4.1 RF Input Keep-Out

| Parameter | Value |
|---|---|
| Area | X: 0-30 mm, Y: 85-115 mm |
| Layers | All layers |
| Purpose | Isolate RF input from digital noise |
| Components | Only RF components allowed |
| Traces | Only RF traces (50Ω controlled impedance) |

### 4.2 Clock Keep-Out

| Parameter | Value |
|---|---|
| Area | X: 170-200 mm, Y: 85-115 mm |
| Layers | All layers |
| Purpose | Isolate clock from digital noise |
| Components | Only clock components allowed |
| Traces | Only clock traces (100Ω differential) |

### 4.3 Power Keep-Out

| Parameter | Value |
|---|---|
| Area | X: 80-120 mm, Y: 0-30 mm |
| Layers | All layers |
| Purpose | Isolate power from sensitive circuits |
| Components | Only power components allowed |
| Traces | Only power traces (wide, low impedance) |

### 4.4 FPGA Keep-Out

| Parameter | Value |
|---|---|
| Area | X: 60-140 mm, Y: 60-140 mm |
| Layers | Top 4 layers (signal), Bottom 4 layers (ground) |
| Purpose | FPGA core area |
| Components | Only FPGA and decoupling capacitors |
| Traces | High-speed signals only |

## 5. PCB Stackup

### 5.1 Layer Structure (12 Layer)

| Layer | Name | Thickness | Material | Purpose |
|---|---|---|---|---|
| 1 | Top Signal | 0.035 mm | Copper | Component placement, high-speed signals |
| 2 | Ground 1 | 0.035 mm | Copper | Continuous ground plane |
| 3 | Signal 2 | 0.035 mm | Copper | Signal routing |
| 4 | Power 1 | 0.035 mm | Copper | 1.0V core plane |
| 5 | Signal 3 | 0.035 mm | Copper | Signal routing |
| 6 | Ground 2 | 0.035 mm | Copper | Continuous ground plane |
| 7 | Ground 3 | 0.035 mm | Copper | Continuous ground plane |
| 8 | Power 2 | 0.035 mm | Copper | 1.8V/3.3V plane |
| 9 | Signal 4 | 0.035 mm | Copper | Signal routing |
| 10 | Ground 4 | 0.035 mm | Copper | Continuous ground plane |
| 11 | Signal 5 | 0.035 mm | Copper | Signal routing |
| 12 | Bottom Signal | 0.035 mm | Copper | Component placement, low-speed signals |

### 5.2 Stackup Drawing

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Top Signal (35µm Cu)                               │
├─────────────────────────────────────────────────────────────┤
│ Prepreg 2116 (0.10mm)                                       │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Ground 1 (35µm Cu)                                 │
├─────────────────────────────────────────────────────────────┤
│ Core (0.20mm)                                                │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: Signal 2 (35µm Cu)                                 │
├─────────────────────────────────────────────────────────────┤
│ Prepreg 2116 (0.10mm)                                       │
├─────────────────────────────────────────────────────────────┤
│ Layer 4: Power 1 (35µm Cu)                                  │
├─────────────────────────────────────────────────────────────┤
│ Core (0.20mm)                                                │
├─────────────────────────────────────────────────────────────┤
│ Layer 5: Signal 3 (35µm Cu)                                 │
├─────────────────────────────────────────────────────────────┤
│ Prepreg 2116 (0.10mm)                                       │
├─────────────────────────────────────────────────────────────┤
│ Layer 6: Ground 2 (35µm Cu)                                 │
├─────────────────────────────────────────────────────────────┤
│ Core (0.20mm)                                                │
├─────────────────────────────────────────────────────────────┤
│ Layer 7: Ground 3 (35µm Cu)                                 │
├─────────────────────────────────────────────────────────────┤
│ Prepreg 2116 (0.10mm)                                       │
├─────────────────────────────────────────────────────────────┤
│ Layer 8: Power 2 (35µm Cu)                                  │
├─────────────────────────────────────────────────────────────┤
│ Core (0.20mm)                                                │
├─────────────────────────────────────────────────────────────┤
│ Layer 9: Signal 4 (35µm Cu)                                 │
├─────────────────────────────────────────────────────────────┤
│ Prepreg 2116 (0.10mm)                                       │
├─────────────────────────────────────────────────────────────┤
│ Layer 10: Ground 4 (35µm Cu)                                │
├─────────────────────────────────────────────────────────────┤
│ Core (0.20mm)                                                │
├─────────────────────────────────────────────────────────────┤
│ Layer 11: Signal 5 (35µm Cu)                                │
├─────────────────────────────────────────────────────────────┤
│ Prepreg 2116 (0.10mm)                                       │
├─────────────────────────────────────────────────────────────┤
│ Layer 12: Bottom Signal (35µm Cu)                           │
└─────────────────────────────────────────────────────────────┘

Total Thickness: 2.40mm ± 0.15mm
```

### 5.3 Impedance Control

| Trace Type | Impedance | Tolerance | Layer | Width |
|---|---|---|---|---|
| Single-ended 50Ω | 50Ω | ±5% | 1, 12 | 0.15 mm |
| Differential 100Ω | 100Ω | ±5% | 1, 12 | 0.12 mm (gap: 0.12 mm) |
| Single-ended 75Ω | 75Ω | ±5% | 3, 5, 9, 11 | 0.10 mm |

## 6. Thermal Requirements

### 6.1 Thermal Interface

| Parameter | Value |
|---|---|
| Material | Bergquist HI-6003 |
| Thickness | 0.254 mm (10 mil) |
| Thermal Conductivity | 3 W/mK |
| Compression | 10-30% |

### 6.2 Thermal Via Pattern

| Component | Via Diameter | Via Pitch | Pattern |
|---|---|---|---|
| FPGA BGA | 0.30 mm | 1.00 mm | Grid |
| ADC FCBGA | 0.25 mm | 0.80 mm | Grid |
| Power MOSFETs | 0.30 mm | 1.20 mm | Array |

### 6.3 Heat Sink Requirements

| Parameter | Value |
|---|---|
| Type | Passive, aluminum |
| Height | 5-10 mm |
| Fin Count | 10-20 fins |
| Attachment | Thermal epoxy + screws |
| Thermal Resistance | < 1.0 °C/W |

## 7. Material Specifications

### 7.1 PCB Material

| Parameter | Value |
|---|---|
| Base Material | Megtron6 (Mektron) |
| Dielectric Constant | 3.4 @ 1 GHz |
| Loss Tangent | 0.002 @ 1 GHz |
| Tg | 200°C |
| CTE (x, y) | 14 ppm/°C |
| CTE (z) | 45 ppm/°C |
| Copper Weight | 2 oz (70µm) on power layers, 1 oz (35µm) on signal layers |

### 7.2 Chassis Material

| Parameter | Value |
|---|---|
| Material | Aluminum 6061-T6 |
| Finish | Hard anodize (Type III, Class 1) |
| Thickness | 2.5 mm (base plate) |
| Thermal Conductivity | 167 W/mK |
| CTE | 23.6 ppm/°C |

### 7.3 Fastener Material

| Parameter | Value |
|---|---|
| Material | Stainless Steel A2 (304) |
| Thread | M3 x 0.5, M2.5 x 0.45 |
| Torque | M3: 0.5 N·m, M2.5: 0.3 N·m |
| Locking | Nylon patch or lock washer |

## 8. Environmental Requirements

### 8.1 Temperature

| Parameter | Value |
|---|---|
| Operating | -40°C to +85°C |
| Storage | -55°C to +125°C |
| Thermal Shock | -55°C to +125°C, 100 cycles |

### 8.2 Vibration

| Parameter | Value |
|---|---|
| Random Vibration | MIL-STD-810G, Method 514.6 |
| Frequency Range | 20-2000 Hz |
| PSD | 0.04 g²/Hz (20-80 Hz), -3 dB/octave (80-2000 Hz) |
| Duration | 4 axes, 4 hours per axis |

### 8.3 Shock

| Parameter | Value |
|---|---|
| Half-sine | MIL-STD-810G, Method 516.6 |
| Peak Acceleration | 20 g |
| Duration | 11 ms |

### 8.4 Humidity

| Parameter | Value |
|---|---|
| Test | MIL-STD-810G, Method 507.6 |
| Conditions | 85°C / 85% RH |
| Duration | 1000 hours |
| Bias | Applied during test |

## 9. Drawing List

| Drawing ID | Title | Size | Revision |
|---|---|---|---|
| XBDM-MEC-001 | Module Outline | A3 | A |
| XBDM-MEC-002 | Mounting Holes | A3 | A |
| XBDM-MEC-003 | Connector Layout | A3 | A |
| XBDM-MEC-004 | PCB Stackup | A4 | A |
| XBDM-MEC-005 | Thermal Design | A3 | A |
| XBDM-MEC-006 | 3D Model | - | A |

## 10. Revision History

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | 2026-09-09 | Mechanical Engineer | Initial release |

---
*End of Document*
