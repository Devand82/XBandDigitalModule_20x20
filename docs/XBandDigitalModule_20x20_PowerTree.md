# XBandDigitalModule_20x20 - Power Tree Document

## Document Information
| Field | Value |
|---|---|
| Document ID | XBDM-DOC-002 |
| Version | 1.0 |
| Date | 2026-09-09 |
| Classification | ITAR Restricted |
| Status | Preliminary Design Review |

## 1. Power Architecture Overview

### 1.1 Input Power Specification

| Parameter | Min | Typ | Max | Unit | Notes |
|---|---|---|---|---|---|
| Input Voltage | 4.0 | 4.5 | 5.5 | V | Nominal 4.5V |
| Input Current | - | 16.2 | 25 | A | At 96.5W max |
| Input Power | - | 72.7 | 96.5 | W | Including losses |
| Ripple | - | - | 100 | mVpp | Before regulation |
| Transient | 3.5 | - | 6.0 | V | MIL-STD-704 |
| Dropout | - | - | 0.5 | V | Min input for regulation |

### 1.2 Power Rail Requirements

| Rail | Voltage | Tolerance | Current | Noise | Sequencing |
|---|---|---|---|---|---|
| VCCINT | 1.0V | ±3% | 44A | <10 mVpp | First |
| VCCAUX | 1.8V | ±3% | 6A | <20 mVpp | Second |
| VCCO | 3.3V | ±3% | 3A | <30 mVpp | Third |
| AVDD | 1.0V | ±2% | 1.5A | <1 mVpp | Fourth |
| DVDD | 1.8V | ±3% | 1.5A | <5 mVpp | Fifth |
| VCLK | 2.5V | ±3% | 2A | <2 mVpp | Fourth |

## 2. Power Tree Diagram

```
                         ┌─────────────────────────────────────────────────────────────┐
                         │                    POWER INPUT SECTION                       │
                         │                                                             │
                         │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
  4.5V Input ───────────►│  │ Reverse     │──►│ Input       │──►│ EMI         │───────┐│
  (4.0-5.5V)             │  │ Polarity    │   │ Filter      │   │ Filter      │       ││
                         │  │ Protection  │   │ (Pi filter) │   │ (Common     │       ││
                         │  └─────────────┘   └─────────────┘   │  mode)      │       ││
                         │                                     └─────────────┘       ││
                         └─────────────────────────────────────────────────────────────┘
                                                                                      │
                                                                                      ▼
                         ┌─────────────────────────────────────────────────────────────┐
                         │                    POWER DISTRIBUTION                       │
                         │                                                             │
                         │  ┌─────────────────────────────────────────────────────┐   │
                         │  │              4.5V BUS (after protection)            │   │
                         │  └─────────────────────────────────────────────────────┘   │
                         │         │         │         │         │         │           │
                         │         ▼         ▼         ▼         ▼         ▼           │
                         │    ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐     │
                         │    │ BUCK 1 ││ BUCK 2 ││ BUCK 3 ││ LDO 1  ││ LDO 2  │     │
                         │    │ TPS7H  ││ ISL70  ││ ISL70  ││ TPS7H  ││ TPS7H  │     │
                         │    │ 5002   ││ 003A   ││ 003A   ││ 1111   ││ 1111   │     │
                         │    └───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘     │
                         │        │         │         │         │         │           │
                         │        ▼         ▼         ▼         ▼         ▼           │
                         │    ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐     │
                         │    │ 1.0V   ││ 1.8V   ││ 3.3V   ││ 1.0V   ││ 1.8V   │     │
                         │    │ Core   ││ Aux    ││ I/O    ││ Analog ││ Digital│     │
                         │    │ 44A    ││ 6A     ││ 3A     ││ 1.5A   ││ 1.5A   │     │
                         │    └────────┘└────────┘└────────┘└────────┘└────────┘     │
                         │                                                             │
                         │  ┌─────────────────────────────────────────────────────┐   │
                         │  │              2.5V LDO (from 3.3V)                   │   │
                         │  │              TPS7H1121-SP                            │   │
                         │  │              2A                                      │   │
                         │  └─────────────────────────────────────────────────────┘   │
                         │                                                             │
                         │  ┌─────────────────────────────────────────────────────┐   │
                         │  │              POWER SEQUENCER                        │   │
                         │  │              TPS7H3014-SP (4-channel)               │   │
                         │  │              Controls: VCCINT→VCCAUX→VCCO→AVDD→DVDD│   │
                         │  └─────────────────────────────────────────────────────┘   │
                         │                                                             │
                         │  ┌─────────────────────────────────────────────────────┐   │
                         │  │              POWER MONITORING                       │   │
                         │  │              INA214-SP (current sense)              │   │
                         │  │              TPS7H3014-SP (voltage monitor)         │   │
                         │  └─────────────────────────────────────────────────────┘   │
                         └─────────────────────────────────────────────────────────────┘
```

## 3. Detailed Rail Analysis

### 3.1 VCCINT (1.0V, 44A) - FPGA Core

**Component**: TPS7H5002-SP (Buck Controller) + External MOSFETs

| Parameter | Value | Notes |
|---|---|---|
| Input Voltage | 4.5V (4.0-5.5V) | Direct from bus |
| Output Voltage | 1.0V ±3% | 0.97V - 1.03V |
| Output Current | 44A max | 35A typical |
| Switching Frequency | 500 kHz | Configurable |
| Efficiency | 92% | At 35A, 4.5V input |
| Output Ripple | <10 mVpp | With ceramic caps |
| Load Transient | <50 mV | 0-100% load step |
| Thermal | 2.8W loss | At 92% efficiency |

**External Components**:
- High-side MOSFET: CSD19538Q3A (TI, 100V, 3.8 mΩ)
- Low-side MOSFET: CSD19538Q3A (TI, 100V, 3.8 mΩ)
- Inductor: Coilcraft XAL6060-402 (4.0 µH, 60A sat)
- Output Caps: 20x TDK C3225X5R1E106K (10 µF, 25V, X5R)
- Input Caps: 10x TDK C3225X5R1E106K (10 µF, 25V, X5R)

**Protection**:
- Overcurrent: Hiccup mode, threshold 48A (109%)
- Overvoltage: 1.15V clamp (115%)
- Undervoltage: 0.85V threshold (85%)
- Thermal: 150°C shutdown

### 3.2 VCCAUX (1.8V, 6A) - FPGA Auxiliary

**Component**: ISL70003ASEH (Integrated Buck)

| Parameter | Value | Notes |
|---|---|---|
| Input Voltage | 4.5V (4.0-5.5V) | Direct from bus |
| Output Voltage | 1.8V ±3% | 1.75V - 1.85V |
| Output Current | 6A max | 4A typical |
| Switching Frequency | 500 kHz | Fixed |
| Efficiency | 94% | At 4A, 4.5V input |
| Output Ripple | <15 mVpp | With ceramic caps |
| Load Transient | <30 mV | 0-100% load step |
| Thermal | 0.45W loss | At 94% efficiency |

**Internal MOSFETs**: 31 mΩ (high-side), 21 mΩ (low-side)

**External Components**:
- Inductor: Coilcraft XAL5030-222 (2.2 µH, 5.5A sat)
- Output Caps: 6x TDK C3225X5R1A106K (10 µF, 10V, X5R)
- Input Caps: 4x TDK C3225X5R1A106K (10 µF, 10V, X5R)

### 3.3 VCCO (3.3V, 3A) - I/O and Clock

**Component**: ISL70003ASEH (Integrated Buck)

| Parameter | Value | Notes |
|---|---|---|
| Input Voltage | 4.5V (4.0-5.5V) | Direct from bus |
| Output Voltage | 3.3V ±3% | 3.20V - 3.40V |
| Output Current | 3A max | 2A typical |
| Switching Frequency | 500 kHz | Fixed |
| Efficiency | 93% | At 2A, 4.5V input |
| Output Ripple | <20 mVpp | With ceramic caps |
| Load Transient | <40 mV | 0-100% load step |
| Thermal | 0.47W loss | At 93% efficiency |

### 3.4 AVDD (1.0V, 1.5A) - ADC Analog

**Component**: TPS7H1111-SP (Ultra-Low Noise LDO)

| Parameter | Value | Notes |
|---|---|---|
| Input Voltage | 3.3V | From VCCO via ferrite |
| Output Voltage | 1.0V ±2% | 0.98V - 1.02V |
| Output Current | 1.5A max | 1.2A typical |
| Dropout Voltage | 200 mV | At 1.5A |
| Output Noise | 1.71 µVRMS | 10 Hz - 100 kHz |
| PSRR | 71 dB | @ 100 kHz |
| Thermal | 0.45W loss | At 3.3V input, 1.5A |

**External Components**:
- Input Cap: 10 µF ceramic (X7R)
- Output Cap: 22 µF ceramic (X7R)
- Feedforward Cap: 100 pF (noise optimization)

**Critical**: This rail powers ADC analog circuitry. Ultra-low noise is essential for maintaining SNR.

### 3.5 DVDD (1.8V, 1.5A) - ADC Digital

**Component**: TPS7H1111-SP (Ultra-Low Noise LDO)

| Parameter | Value | Notes |
|---|---|---|
| Input Voltage | 3.3V | From VCCO via ferrite |
| Output Voltage | 1.8V ±3% | 1.75V - 1.85V |
| Output Current | 1.5A max | 1.0A typical |
| Dropout Voltage | 200 mV | At 1.5A |
| Output Noise | 1.71 µVRMS | 10 Hz - 100 kHz |
| PSRR | 71 dB | @ 100 kHz |
| Thermal | 0.75W loss | At 3.3V input, 1.5A |

### 3.6 VCLK (2.5V, 2A) - Clock and Balun

**Component**: TPS7H1121-SP (General Purpose LDO)

| Parameter | Value | Notes |
|---|---|---|
| Input Voltage | 3.3V | From VCCO |
| Output Voltage | 2.5V ±3% | 2.43V - 2.58V |
| Output Current | 2A max | 1.5A typical |
| Dropout Voltage | 300 mV | At 2A |
| Output Noise | 4 µVRMS | 10 Hz - 100 kHz |
| PSRR | 45 dB | @ 100 kHz |
| Thermal | 1.2W loss | At 3.3V input, 2A |

## 4. Power Sequencing

### 4.1 Sequencing Requirements

| Order | Rail | Delay | Reason |
|---|---|---|---|
| 1 | VCCINT (1.0V) | 0 ms | FPGA core must power first |
| 2 | VCCAUX (1.8V) | 10 ms | Auxiliary before I/O |
| 3 | VCCO (3.3V) | 20 ms | I/O banks |
| 4 | AVDD (1.0V) | 30 ms | ADC analog (after FPGA ready) |
| 5 | DVDD (1.8V) | 40 ms | ADC digital (after analog) |

### 4.2 Sequencer Implementation

**Component**: TPS7H3014-SP (4-Channel Sequencer)

```
Channel 1: VCCINT (1.0V) ──► Delay 10ms ──►
Channel 2: VCCAUX (1.8V) ──► Delay 10ms ──►
Channel 3: VCCO (3.3V) ──► Delay 10ms ──►
Channel 4: AVDD (1.0V) ──► (external RC for DVDD delay)
```

**PGOOD Chain**:
```
VCCINT PGOOD ──┐
                ├──► AND ──► VCCAUX Enable
VCCAUX PGOOD ──┘

VCCAUX PGOOD ──┐
                ├──► AND ──► VCCO Enable
VCCO PGOOD ────┘

VCCO PGOOD ────┐
                ├──► AND ──► AVDD Enable
AVDD PGOOD ────┘

AVDD PGOOD ────┐
                ├──► AND ──► DVDD Enable
RC Delay ──────┘
```

### 4.3 Shutdown Sequence

Reverse order: DVDD → AVDD → VCCO → VCCAUX → VCCINT

**Emergency Shutdown**: If any rail faults, all rails shutdown simultaneously via FAULT pin.

## 5. Protection Circuits

### 5.1 Input Protection

| Function | Component | Specification |
|---|---|---|
| Reverse Polarity | P-MOSFET (IRF9310) | -40V, 6.5A, RDS(on)=0.15Ω |
| OVP | TVS (SMDJ6.0A) | 6.0V breakdown, 600W |
| Inrush Current | NTC Thermistor (5D-9) | 5Ω cold, 0.3Ω hot |
| EMI Filter | Pi-filter | 2x 10µH + 2x 100µF |
| Fuse | Resettable (Bourns MF-MSMF050) | 5A hold, 10A trip |

### 5.2 Per-Rail Protection

| Rail | OVP | OCP | UVLO | Thermal |
|---|---|---|---|---|
| VCCINT | 1.15V (115%) | 48A (109%) | 0.85V (85%) | 150°C |
| VCCAUX | 1.95V (108%) | 7A (117%) | 1.5V (83%) | 150°C |
| VCCO | 3.5V (106%) | 3.5A (117%) | 2.8V (85%) | 150°C |
| AVDD | 1.05V (105%) | 2A (133%) | 0.8V (80%) | 125°C |
| DVDD | 1.9V (106%) | 2A (133%) | 1.5V (83%) | 125°C |
| VCLK | 2.65V (106%) | 2.5A (125%) | 2.0V (80%) | 125°C |

### 5.3 Fault Handling

**Fault Sources**:
1. Overvoltage (OVP)
2. Overcurrent (OCP)
3. Undervoltage (UVLO)
4. Overtemperature (OT)
5. Sequencing fault

**Fault Response**:
```
Fault Detected ──► Assert FAULT pin ──► Log error register ──►
    │
    ├──► If critical: Emergency shutdown (all rails off)
    │
    └──► If recoverable: Attempt retry (3 attempts)
```

## 6. Power Monitoring

### 6.1 Voltage Monitoring

| Rail | Monitor | Threshold | Method |
|---|---|---|---|
| VCCINT | TPS7H3014-SP | ±5% | Internal comparator |
| VCCAUX | TPS7H3014-SP | ±5% | Internal comparator |
| VCCO | TPS7H3014-SP | ±5% | Internal comparator |
| AVDD | INA214-SP | ±3% | External sense |
| DVDD | INA214-SP | ±5% | External sense |

### 6.2 Current Monitoring

| Rail | Monitor | Range | Accuracy |
|---|---|---|---|
| Input (4.5V) | INA214-SP | 0-25A | ±1% |
| VCCINT | INA214-SP | 0-50A | ±1% |
| VCCAUX | INA214-SP | 0-10A | ±2% |
| Total Power | Calculated | 0-100W | ±3% |

### 6.3 Temperature Monitoring

| Location | Sensor | Range | Accuracy |
|---|---|---|---|
| FPGA die | Internal DTS | -40 to +125°C | ±3°C |
| ADC die | Internal | -40 to +125°C | ±5°C |
| PCB hot spot | TMP102-SP | -40 to +125°C | ±1°C |
| Ambient | TMP102-SP | -40 to +85°C | ±1°C |

## 7. Efficiency Analysis

### 7.1 Rail Efficiency

| Rail | Topology | Efficiency @ Typ Load | Efficiency @ Max Load |
|---|---|---|---|
| VCCINT (1.0V) | Buck (TPS7H5002) | 92% | 90% |
| VCCAUX (1.8V) | Buck (ISL70003) | 94% | 92% |
| VCCO (3.3V) | Buck (ISL70003) | 93% | 91% |
| AVDD (1.0V) | LDO (TPS7H1111) | 30% | 30% |
| DVDD (1.8V) | LDO (TPS7H1111) | 55% | 55% |
| VCLK (2.5V) | LDO (TPS7H1121) | 76% | 76% |

### 7.2 Total System Efficiency

```
Buck Rails:
  VCCINT: 60W × 92% = 55.2W output, 6.8W loss
  VCCAUX: 10.8W × 94% = 10.1W output, 0.7W loss
  VCCO:   9.9W × 93% = 9.2W output, 0.7W loss

LDO Rails:
  AVDD: 1.5W × 30% = 1.5W output, 3.5W loss
  DVDD: 2.7W × 55% = 2.7W output, 2.2W loss
  VCLK: 5W × 76% = 5W output, 1.6W loss

Total Output Power: 83.7W
Total Input Power: 96.5W
Overall Efficiency: 86.7%
```

## 8. Thermal Considerations

### 8.1 Power Dissipation by Component

| Component | Power Loss | Package | θJC | θJA | TJ Max |
|---|---|---|---|---|---|
| TPS7H5002-SP | 0.3W | CFP-22 | 15°C/W | 50°C/W | 125°C |
| External MOSFETs | 2.8W | D2PAK | 1.5°C/W | 40°C/W | 150°C |
| ISL70003ASEH (x2) | 0.9W | CQFP-64 | 5°C/W | 25°C/W | 150°C |
| TPS7H1111-SP (x2) | 1.2W | HTSSOP-28 | 3°C/W | 30°C/W | 125°C |
| TPS7H1121-SP | 1.2W | CFP-22 | 4°C/W | 35°C/W | 125°C |
| TPS7H3014-SP | 0.1W | CFP-22 | 10°C/W | 45°C/W | 125°C |
| **Total** | **6.5W** | - | - | - | - |

### 8.2 Thermal Management

- **PCB Copper**: 2 oz copper on power layers
- **Thermal Vias**: Under all power components, 0.3mm diameter, 1mm pitch
- **Copper Pour**: Connected to thermal pads
- **Heat Sink**: Optional for >80W operation

## 9. EMC Considerations

### 9.1 Conducted Emissions

| Frequency | Limit | Mitigation |
|---|---|---|
| 150 kHz - 30 MHz | CISPR 11 Class A | Pi-filter at input |
| 30 MHz - 1 GHz | CISPR 11 Class A | Common-mode choke |

### 9.2 Radiated Emissions

| Frequency | Limit | Mitigation |
|---|---|---|
| 30 MHz - 1 GHz | CISPR 11 Class A | Shielded enclosure, filtering |
| 1 GHz - 6 GHz | CISPR 11 Class A | PCB layout, grounding |

### 9.3 PCB Layout Guidelines

- **Ground Plane**: Continuous ground plane on layer 2
- **Decoupling**: 100nF + 10µF per power pin
- **Routing**: Power traces on dedicated layers
- **Separation**: Analog and digital grounds separated at single point
- **Via Stitching**: Around high-speed areas

## 10. BOM Summary

### 10.1 Power Section BOM

| Reference | Part Number | Description | Qty | Unit Cost | Total |
|---|---|---|---|---|---|
| U1 | TPS7H5002-SP | Buck Controller | 1 | $45.00 | $45.00 |
| U2 | ISL70003ASEH | Integrated Buck | 2 | $35.00 | $70.00 |
| U3 | TPS7H1111-SP | Ultra-Low Noise LDO | 2 | $25.00 | $50.00 |
| U4 | TPS7H1121-SP | General LDO | 1 | $20.00 | $20.00 |
| U5 | TPS7H3014-SP | Sequencer | 1 | $30.00 | $30.00 |
| U6 | INA214-SP | Current Sense Amp | 3 | $15.00 | $45.00 |
| Q1-Q4 | CSD19538Q3A | MOSFET 100V 3.8mΩ | 4 | $8.00 | $32.00 |
| L1 | XAL6060-402 | Inductor 4µH 60A | 1 | $12.00 | $12.00 |
| L2-L3 | XAL5030-222 | Inductor 2.2µH 5.5A | 2 | $6.00 | $12.00 |
| C1-C36 | C3225X5R | Capacitors 10µF | 36 | $0.50 | $18.00 |
| **Total Power Section** | - | - | **53** | - | **$334.00** |

### 10.2 Cost Estimation

| Category | Cost | Notes |
|---|---|---|
| Power Section | $334 | As above |
| ADC Section | $850 | ADC12DJ5200-SP + support |
| FPGA Section | $180,000 | XQRVC1902 + DDR4 |
| Clock Section | $450 | LMX2615-SP + LMK04832-SP |
| Mechanical | $2,500 | PCB + chassis + connectors |
| Assembly | $5,000 | SMT + test |
| **Total Module** | **~$189,134** | - |

## 11. Risk Assessment

| Risk ID | Description | Probability | Impact | Mitigation |
|---|---|---|---|---|
| P001 | Buck regulator instability | Low | High | Proper compensation, ceramic caps |
| P002 | LDO thermal shutdown | Medium | Medium | Derating, thermal vias |
| P003 | Sequencing timing error | Low | High | Programmable delays, margin |
| P004 | Noise coupling to ADC | Medium | High | Separate rails, ferrite beads |
| P005 | Input voltage transient | Low | Medium | TVS protection, bulk caps |

## 12. Revision History

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | 2026-09-09 | Power Electronics Engineer | Initial release |

---
*End of Document*
