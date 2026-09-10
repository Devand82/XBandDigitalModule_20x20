# XBandDigitalModule_20x20 - System Architecture Document

## Document Information
| Field | Value |
|---|---|
| Document ID | XBDM-DOC-001 |
| Version | 1.0 |
| Date | 2026-09-09 |
| Classification | ITAR Restricted |
| Status | Preliminary Design Review |

## 1. Executive Summary

The XBandDigitalModule_20x20 is a 20cm x 20cm space-grade electronic module designed for RF signal acquisition and sampling up to 500 MHz bandwidth in X-band (8-12 GHz). The module implements a direct RF sampling architecture using state-of-the-art radiation-hardened components.

## 2. System Overview

### 2.1 Mission Requirements
- **Frequency Range**: 8-12 GHz (X-band)
- **Signal Bandwidth**: 500 MHz
- **ADC Resolution**: 12-bit
- **Sample Rate**: 10.4 GSPS (single channel)
- **Data Interface**: SpaceWire / JESD204C
- **Operating Temperature**: -40°C to +85°C
- **Radiation Tolerance**: 100+ krad(Si) TID, >43 MeV·cm²/mg SEL

### 2.2 Design Philosophy
The module采用 direct RF sampling architecture to:
- Minimize analog components (no mixer, LO, IF filters)
- Maximize flexibility (software-defined frequency selection)
- Reduce SWaP-C (Space, Weight, Power, Cost)
- Leverage proven reference designs (TI TIDA-010274)

## 3. Architecture Selection

### 3.1 Options Considered

| Option | Description | Pros | Cons | Selected |
|---|---|---|---|---|
| 1. Direct RF Sampling | ADC samples X-band directly | Minimal components, high flexibility | Requires 10+ GSPS ADC, high clock jitter sensitivity | **YES** |
| 2. Undersampling | Bandpass sampling at lower rate | Lower ADC speed | Complex aliasing, limited bandwidth | No |
| 3. Downconversion | Analog mixer to IF | Better SNR, lower ADC speed | More components, LO noise, larger size | No |
| 4. Hybrid IF | Digital IF processing | Balanced approach | Complex architecture | No |

### 3.2 Rationale for Direct RF Sampling
1. **Component Availability**: ADC12DJ5200-SP (TI) provides 10.4 GSPS with 8 GHz analog bandwidth
2. **Reference Design**: TI TIDA-010274 demonstrates X-band direct sampling
3. **FPGA Capability**: XQRVC1902 (AMD Versal) supports 16-lane JESD204C at 16+ Gbps
4. **Heritage**: Increasing adoption in modern space payloads

## 4. Functional Block Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           XBAND DIGITAL MODULE 20x20                            │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                         RF FRONT END                                     │   │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────────────────┐  │   │
│  │  │ SMA     │───►│ BPF     │───►│ LNA     │───►│ Balun TRF0208-SP    │  │   │
│  │  │ Input   │    │ 8-12GHz │    │ (opt.)  │    │ SE to Diff          │  │   │
│  │  └─────────┘    └─────────┘    └─────────┘    └──────────┬──────────┘  │   │
│  └───────────────────────────────────────────────────────────┼──────────────┘   │
│                                                              │                  │
│                                                              ▼                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                      ANALOG-TO-DIGITAL CONVERSION                        │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │                    ADC12DJ5200-SP                                │    │   │
│  │  │  • 12-bit resolution                                            │    │   │
│  │  │  • 10.4 GSPS (single channel) / 5.2 GSPS (dual channel)       │    │   │
│  │  │  • 8 GHz analog bandwidth (-3dB)                                │    │   │
│  │  │  • JESD204C interface (up to 16 lanes)                          │    │   │
│  │  │  • Integrated DDC with 4 NCOs                                   │    │   │
│  │  │  • Radiation Hardened: 300 krad(Si) TID, 120 MeV·cm²/mg SEL   │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                              │                  │
│                                            JESD204C (16 lanes @ 16 Gbps)        │
│                                                              │                  │
│                                                              ▼                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                      DIGITAL PROCESSING ENGINE                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │                    AMD XQRVC1902 (Versal AI Core)               │    │   │
│  │  │  • 44x GTY transceivers @ 26.5625 Gbps                        │    │   │
│  │  │  • 400 AI Engine tiles for DSP                                  │    │   │
│  │  │  • Dual Cortex-A72 + Dual Cortex-R5F                           │    │   │
│  │  │  • 191 Mb PL memory                                            │    │   │
│  │  │  • 4x DDR4/LPDDR4 controllers                                  │    │   │
│  │  │  • Radiation Tolerant (Class B qualified)                       │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │   │
│  │  │ JESD204C     │  │ DDC Chain    │  │ Buffer/FIFO  │                 │   │
│  │  │ Receiver     │  │ (8 channels) │  │ (4K x 32b)   │                 │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                 │   │
│  │                                                                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │   │
│  │  │ Error        │  │ Clock        │  │ SpaceWire    │                 │   │
│  │  │ Handler      │  │ Manager      │  │ Interface    │                 │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                 │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                         POWER MANAGEMENT                                 │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │   │
│  │  │ Input        │  │ Buck         │  │ LDO          │  │ Sequencer  │  │   │
│  │  │ Protection   │  │ TPS7H5002    │  │ TPS7H1111    │  │ TPS7H3014  │  │   │
│  │  │ + Filtering  │  │ + ISL70003   │  │ (Analog)     │  │            │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                         CLOCK SUBSYSTEM                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │   │
│  │  │ VCXO         │  │ LMX2615-SP   │  │ LMK04832-SP  │                   │   │
│  │  │ 122.88 MHz   │─►│ 10.4 GHz     │─►│ Jitter       │                   │   │
│  │  │              │  │ Synthesizer  │  │ Cleaner      │                   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                   │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                         INTERFACES                                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │   │
│  │  │ RF Input     │  │ Power        │  │ JTAG/Debug   │  │ Test       │  │   │
│  │  │ SMA          │  │ Connector    │  │ Headers      │  │ Points     │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 5. Data Flow Architecture

### 5.1 Signal Path
```
RF Input (8-12 GHz, 500 MHz BW)
    │
    ▼
Bandpass Filter (8-12 GHz, insertion loss < 1 dB)
    │
    ▼
LNA (optional, gain 15-20 dB, NF < 2 dB)
    │
    ▼
Active Balun (TRF0208-SP, SE to Differential, DC-8 GHz)
    │
    ▼
ADC12DJ5200-SP (10.4 GSPS, 12-bit, JESD204C)
    │
    ├──► DDC (Digital Down-Conversion) - 8 independent channels
    │       ├── NCO (tunable frequency)
    │       ├── CIC/FIR decimation filter
    │       └── I/Q output (16-bit per component)
    │
    ▼
Buffer FIFO (4K x 32-bit, async clock domains)
    │
    ▼
SpaceWire Interface (2 links, 100 Mbps each)
    │
    ▼
External Data Storage / Processing
```

### 5.2 Clock Distribution
```
VCXO (122.88 MHz, <0.5 ps RMS jitter)
    │
    ▼
LMX2615-SP (PLL Synthesizer)
    ├──► 10.4 GHz Sampling Clock ──► ADC CLK±
    │
    └──► Reference ──► LMK04832-SP (Jitter Cleaner)
                           ├──► Device Clock (DCLK) ──► ADC, FPGA
                           ├──► SYSREF ──► ADC, FPGA (JESD204B/C sync)
                           └──► FPGA Clock ──► FPGA Logic
```

### 5.3 Power Distribution
```
Input: 4.5V nominal (range 4.0-5.5V)
    │
    ├──► TPS7H5002-SP (Buck) ──► 1.0V @ 44A (FPGA Core)
    │
    ├──► ISL70003ASEH (Buck) ──► 1.8V @ 6A (FPGA Aux)
    │
    ├──► ISL70003ASEH (Buck) ──► 3.3V @ 3A (I/O, Clock)
    │
    ├──► TPS7H1111-SP (LDO) ──► 1.0V @ 1.5A (ADC AVDD)
    │
    ├──► TPS7H1111-SP (LDO) ──► 1.8V @ 1.5A (ADC DVDD)
    │
    └──► TPS7H1121-SP (LDO) ──► 2.5V @ 2A (Clock, Balun)

Sequencing Order: 1.0V core → 1.8V aux → 3.3V I/O → 1.0V analog → 1.8V analog
```

## 6. Component Selection Summary

### 6.1 Critical Components

| Component | Part Number | Function | Qualification | Rationale |
|---|---|---|---|---|
| ADC | ADC12DJ5200-SP | 10.4 GSPS, 12-bit | QML-V, 300 krad | Only space-grade ADC with 8 GHz BW |
| FPGA | XQRVC1902 | Versal AI Core | Class B | 44 GTY @ 26.5 Gbps for JESD204C |
| Clock Synth | LMX2615-SP | 10.4 GHz PLL | QMLV, 100 krad | 45 fs RMS jitter, space qualified |
| Clock Clean | LMK04832-SP | Jitter cleaner | QMLV, 100 krad | JESD204B/C SYSREF support |
| Balun | TRF0208-SP | SE to Diff | Space-grade | DC-8 GHz, matches ADC input |
| Buck Ctrl | TPS7H5002-SP | Power regulator | QMLV-RHA, 100 krad | Rad-hard, GaN-optimized |
| Buck Integ | ISL70003ASEH | 9A Buck | QML Class V, 100 krad | High efficiency, rad-hard |
| LDO | TPS7H1111-SP | Ultra-low noise | QMLV-RHA, 100 krad | 1.71 µVRMS, critical for ADC |
| Sequencer | TPS7H3014-SP | 4-ch sequencer | QMLV-RHA, 100 krad | Programmable, fault detection |

### 6.2 Alternative Components

| Primary | Alternative | Qualification | Trade-off |
|---|---|---|---|
| ADC12DJ5200-SP | ADC12DJ5200-SEP | Rad-tolerant, 30 krad | Lower TID, lower cost |
| ADC12DJ5200-SP | EV12AQ600 | Space-grade, 6.4 GSPS | Lower sample rate |
| XQRVC1902 | XQRKU060 | Class B, 12.5 Gbps | GTH limited to 12.5 Gbps |
| LMX2615-SP | LMX2694-SEP | Rad-tolerant, 30 krad | Lower TID, smaller package |
| TPS7H5002-SP | RIC70847 | Class V, Infineon | Newer, limited heritage |

## 7. Design Constraints

### 7.1 Mechanical
- **Dimensions**: 200 mm x 200 mm x 25 mm (max)
- **Mounting**: 4x M3 (corners) + 2x M2.5 (short side)
- **Weight**: < 500 g
- **Material**: FR4/Megtron6 PCB, Aluminum 6061-T6 chassis

### 7.2 Electrical
- **Input Voltage**: 4.5V nominal (4.0-5.5V range)
- **Max Power**: 100 W (with thermal management)
- **ESD**: MIL-STD-883 Class 1C (2 kV HBM)
- **EMI**: FCC Part 15 Class A (space-qualified)

### 7.3 Environmental
- **Operating Temp**: -40°C to +85°C
- **Storage Temp**: -55°C to +125°C
- **Vibration**: MIL-STD-810G, Method 514.6
- **Shock**: MIL-STD-810G, Method 516.6
- **Humidity**: 85°C/85% RH, 1000 hours

### 7.4 Radiation
- **TID**: 100 krad(Si) minimum (2x margin for 50 krad mission)
- **SEL**: >43 MeV·cm²/mg (LET threshold)
- **SEU**: Mitigated by FPGA TMR and EDAC
- **DDSE**: Considered for critical registers

## 8. Performance Budget

### 8.1 Signal Chain Performance

| Parameter | Value | Notes |
|---|---|---|
| Input Frequency | 8-12 GHz | X-band |
| Signal Bandwidth | 500 MHz | Instantaneous |
| ADC Resolution | 12-bit | Nominal |
| ENOB (at 10 GHz) | ~8.8 bit | From datasheet |
| SNR (at 10 GHz) | ~55.6 dB | From datasheet |
| SFDR (at 10 GHz) | ~65 dBc | From datasheet |
| Clock Jitter | < 100 fs RMS | With LMK04832-SP |
| DDC Decimation | 2x to 32x | Software configurable |
| Output Data Rate | Up to 1.6 Gbps per channel | After decimation |

### 8.2 Power Budget

| Block | Typical | Max | Notes |
|---|---|---|---|
| ADC12DJ5200-SP | 4.0 W | 4.5 W | From datasheet |
| FPGA XQRVC1902 | 60 W | 80 W | Design dependent |
| Clock Subsystem | 3.2 W | 4.0 W | LMX2615 + LMK04832 |
| Power Management | 5.0 W | 7.0 W | Buck + LDO losses |
| Balun + Support | 0.5 W | 1.0 W | TRF0208-SP + misc |
| **Total** | **72.7 W** | **96.5 W** | With 30% margin |

### 8.3 Thermal Budget

| Parameter | Value | Notes |
|---|---|---|
| Max Junction Temp | 125°C | Per component specs |
| Ambient Temp | 85°C | Worst case |
| Thermal Resistance (J-C) | 1.5 °C/W | FPGA typical |
| Thermal Resistance (C-B) | 0.5 °C/W | With thermal interface |
| Thermal Resistance (B-A) | 2.0 °C/W | With heat sink |
| Max Power Dissipation | 100 W | With active cooling |

## 9. Reliability

### 9.1 MTBF Estimation
- **Target MTBF**: > 100,000 hours (11.4 years)
- **Approach**: Parts count + stress analysis
- **Key Contributors**: Active components (ADC, FPGA), power management
- **Mitigation**: Redundancy, derating, screening

### 9.2 Failure Modes

| Failure Mode | Probability | Impact | Mitigation |
|---|---|---|---|
| ADC failure | Low | Loss of acquisition | Watchdog, reset |
| FPGA SEU | Medium | Bit flip, logic error | TMR, EDAC, scrubbing |
| Clock unlock | Low | Loss of sampling | Redundant clock path |
| Power supply failure | Low | Module shutdown | Current limiting, OVP |
| SEL event | Very Low | Latch-up, damage | Current limiting, power cycle |

## 10. Interface Control Document (ICD) Summary

### 10.1 External Interfaces

| Interface | Type | Pins | Description |
|---|---|---|---|
| RF Input | SMA | 2 (signal + gnd) | 8-12 GHz input |
| Power Input | MIL-DTL-38999 | 4 (VIN, GND, GND, EP) | 4.5V, 25A max |
| SpaceWire | MIL-DTL-38999 | 8 (2 links) | Data + Strobe, 100 Mbps |
| JTAG | Box header | 14 | FPGA configuration/debug |
| Debug | Box header | 10 | UART, SPI, I2C |
| Test Points | Via | 10 | Power rails, clock, signals |

### 10.2 Internal Interfaces

| Interface | Standard | Width | Clock | Description |
|---|---|---|---|---|
| ADC to FPGA | JESD204C | 16 lanes | 10.4 GHz | 64B/66B encoding |
| FPGA to DDR4 | DDR4 | 256-bit | 1200 MHz | Memory interface |
| FPGA to SpaceWire | SWS | 2 links | 100 Mbps | Data output |
| FPGA to Clock | SPI | 24-bit | 10 MHz | Configuration |
| FPGA to Power | I2C | 8-bit | 400 kHz | Monitoring |

## 11. Verification Approach

### 11.1 Verification Methods
- **Analysis**: Worst-case analysis (WCA), Parts stress analysis (PSA)
- **Inspection**: Visual, X-ray, dimensional
- **Test**: Functional, parametric, environmental, radiation
- **Demonstration**: System integration, end-to-end data flow

### 11.2 Test Points

| Test Point | Location | Signal | Purpose |
|---|---|---|---|
| TP1 | Power input | VIN | Input voltage monitor |
| TP2 | 1.0V core | VCCINT | FPGA core voltage |
| TP3 | 1.8V aux | VCCAUX | FPGA aux voltage |
| TP4 | 3.3V I/O | VCCO | I/O voltage |
| TP5 | 1.0V analog | AVDD | ADC analog supply |
| TP6 | 1.8V digital | DVDD | ADC digital supply |
| TP7 | Clock output | CLK | Sampling clock |
| TP8 | SYSREF | SYSREF | JESD204 sync |
| TP9 | JESD lane 0 | TX0 | Data lane monitor |
| TP10 | Error flag | ERR | System error |

## 12. Risk Assessment Summary

| Risk ID | Description | Probability | Impact | Mitigation | Status |
|---|---|---|---|---|---|
| R001 | Clock jitter exceeds spec | Low | High | Use LMX2615-SP (45 fs), LMK04832-SP | Open |
| R002 | JESD204C lane margin | Low | Medium | GTY @ 26.5 Gbps vs 16 Gbps required | Open |
| R003 | Power sequencing error | Medium | High | TPS7H3014-SP with programmable delays | Open |
| R004 | TID accumulation | Low | Medium | 100+ krad components, 2x margin | Open |
| R005 | SEL event | Very Low | High | All components SEL-immune >43 MeV·cm²/mg | Open |
| R006 | Thermal hotspot | Medium | Medium | Thermal vias, copper pour, heat sink | Open |
| R007 | Component obsolescence | Low | Medium | Multi-source, alternative components | Open |

## 13. Documents Cross-Reference

| Document | ID | Description |
|---|---|---|
| System Architecture | XBDM-DOC-001 | This document |
| Power Tree | XBDM-DOC-002 | Detailed power architecture |
| Clock Tree | XBDM-DOC-003 | Clock distribution and jitter budget |
| Risk Assessment | XBDM-DOC-004 | Detailed risk matrix |
| Component Selection | XBDM-DOC-005 | Component rationale and alternatives |
| WCA | XBDM-DOC-006 | Worst-case analysis |
| PSA | XBDM-DOC-007 | Parts stress analysis |
| ICD Mechanical | XBDM-DOC-008 | Mechanical interface control |
| ICD VHDL | XBDM-DOC-009 | Digital interface control |
| Test Plan | XBDM-DOC-010 | Verification and test procedures |

## 14. Revision History

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | 2026-09-09 | System Engineering | Initial release |

---
*End of Document*
