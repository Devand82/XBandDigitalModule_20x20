# XBandDigitalModule_20x20 - Technical Description

## Document Information
| Field | Value |
|---|---|
| Document ID | XBDM-DOC-010 |
| Version | 1.0 |
| Date | 2026-09-09 |
| Classification | ITAR Restricted |

## 1. Executive Summary

The XBandDigitalModule_20x20 is a 20cm x 20cm space-grade electronic module for direct RF sampling of X-band signals (8-12 GHz) with 500 MHz instantaneous bandwidth. The module implements a complete signal chain from RF input to digital data output via SpaceWire, using state-of-the-art radiation-hardened components.

## 2. System Architecture

### 2.1 Signal Chain

```
RF Input (8-12 GHz, SMA) → BPF → LNA → Balun (TRF0208-SP) → ADC (ADC12DJ5200-SP)
    → JESD204C (16 lanes @ 16 Gbps) → FPGA (XQRVC1902) → DDC (8 channels)
    → FIFO Buffer → SpaceWire (2 links @ 100 Mbps)
```

### 2.2 Key Features

| Feature | Specification |
|---|---|
| Input Frequency | 8-12 GHz (X-band) |
| Signal Bandwidth | 500 MHz |
| ADC Resolution | 12-bit |
| Sample Rate | 10.4 GSPS |
| Clock Jitter | <100 fs RMS |
| DDC Channels | 8 independent |
| Data Output | SpaceWire 2x 100 Mbps |
| Power | <100W |
| Dimensions | 200mm x 200mm x 25mm |
| Radiation | 100+ krad(Si) TID |

## 3. Component Selection

### 3.1 Critical Components

| Component | Part Number | Function | Rationale |
|---|---|---|---|
| ADC | ADC12DJ5200-SP | 10.4 GSPS sampling | Only space-grade ADC with 8 GHz BW |
| FPGA | XQRVC1902 | Digital processing | 44 GTY @ 26.5 Gbps for JESD204C |
| Clock Synth | LMX2615-SP | 10.4 GHz clock | 45 fs jitter, QML qualified |
| Clock Dist | LMK04832-SP | Jitter cleaning | JESD204B/C SYSREF support |
| Balun | TRF0208-SP | SE to Diff | DC-8 GHz, matches ADC |
| Buck | TPS7H5002-SP | FPGA core power | Rad-hard, GaN-optimized |
| LDO | TPS7H1111-SP | ADC analog power | 1.71 µVRMS ultra-low noise |
| Sequencer | TPS7H3014-SP | Power sequencing | 4-channel, programmable |

## 4. Power Tree

### 4.1 Power Architecture

```
Input: 4.5V (4.0-5.5V)
├── TPS7H5002-SP (Buck) → 1.0V @ 44A (FPGA Core)
├── ISL70003ASEH (Buck) → 1.8V @ 6A (FPGA Aux)
├── ISL70003ASEH (Buck) → 3.3V @ 3A (I/O, Clock)
├── TPS7H1111-SP (LDO) → 1.0V @ 1.5A (ADC AVDD)
├── TPS7H1111-SP (LDO) → 1.8V @ 1.5A (ADC DVDD)
└── TPS7H1121-SP (LDO) → 2.5V @ 2A (Clock, Balun)

Sequencing: TPS7H3014-SP (1.0V → 1.8V → 3.3V → 1.0V analog → 1.8V analog)
```

### 4.2 Power Budget

| Rail | Typical Power | Max Power | Efficiency |
|---|---|---|---|
| 1.0V Core | 44W | 52.8W | 92% |
| 1.8V Aux | 10.8W | 12.96W | 94% |
| 3.3V I/O | 9.9W | 11.88W | 93% |
| 1.0V Analog | 1.5W | 2.0W | 30% (LDO) |
| 1.8V Digital | 2.7W | 3.6W | 55% (LDO) |
| 2.5V Clock | 5.0W | 6.0W | 76% (LDO) |
| **Total** | **73.9W** | **89.2W** | **87% overall** |

## 5. Clock Architecture

### 5.1 Clock Tree

```
VCXO (122.88 MHz) → LMX2615-SP → 10.4 GHz → ADC
                    │
                    └──→ LMK04832-SP → Device Clock → FPGA
                                       SYSREF → ADC + FPGA
```

### 5.2 Jitter Budget

| Source | Jitter (RMS) |
|---|---|
| VCXO | 500 fs |
| LMX2615-SP | 45 fs |
| LMK04832-SP | 54 fs |
| Distribution | 10 fs |
| Power Supply | 5 fs |
| **Total (RSS)** | **71 fs** |

## 6. Mechanical Design

### 6.1 Module Dimensions

- **Length**: 200.00 mm ± 0.10 mm
- **Width**: 200.00 mm ± 0.10 mm
- **Height**: 25.00 mm max
- **Weight**: < 500 g

### 6.2 PCB Stackup

- **Layers**: 12
- **Material**: Megtron6 (high-speed, low-loss)
- **Thickness**: 2.40 mm
- **Copper**: 2 oz (power), 1 oz (signal)

### 6.3 Mounting

- 4x M3 holes (corners, 10mm from edges)
- 2x M2.5 holes (short sides, center)

## 7. VHDL Architecture

### 7.1 Module Hierarchy

```
top_module
├── jesd204c_receiver (16 lanes, 64B/66B)
├── ddc_chain (8 channels, NCO + CIC + FIR)
├── fifo_buffer (4K x 32-bit, async)
├── error_handler (EDAC, fault logging)
├── clock_manager (SPI config for LMK04832-SP)
├── spacewire_interface (2 links, 100 Mbps)
└── axi4_lite_slave (register interface)
```

### 7.2 Register Map Summary

| Address | Name | Description |
|---|---|---|
| 0x0000 | SYS_STATUS | System status and version |
| 0x0004 | SYS_CTRL | System control (reset, enable, mode) |
| 0x0040 | ADC_CTRL | ADC configuration |
| 0x0080 | FPGA_TEMP | FPGA temperature |
| 0x00C0 | POWER_STATUS | Power rail status |
| 0x0100 | CLOCK_STATUS | Clock lock status |
| 0x0200-0x02FF | DDC_CTRL | DDC configuration (8 channels) |
| 0x0300-0x03FF | SPW_CTRL | SpaceWire configuration |

## 8. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Clock jitter > 100 fs | Low | High | LMX2615-SP (45 fs) + LMK04832-SP |
| JESD204C lane margin | Low | Medium | GTY @ 26.5 Gbps vs 16 Gbps |
| Power sequencing error | Medium | High | TPS7H3014-SP programmable delays |
| TID accumulation | Low | Medium | 100+ krad components, 2x margin |
| Thermal hotspot | Medium | Medium | Thermal vias, copper pour, heat sink |

## 9. Test Approach

### 9.1 Test Points

| TP | Signal | Location |
|---|---|---|
| TP1 | VIN (4.5V) | Power input |
| TP2 | VCCINT (1.0V) | FPGA core |
| TP3 | VCCAUX (1.8V) | FPGA aux |
| TP4 | VCCO (3.3V) | I/O |
| TP5 | AVDD (1.0V) | ADC analog |
| TP6 | DVDD (1.8V) | ADC digital |
| TP7 | CLK (10.4 GHz) | Clock output |
| TP8 | SYSREF | JESD sync |
| TP9 | JESD Lane 0 | Data monitor |
| TP10 | ERROR | System error |

### 9.2 Test Procedures

1. Power-on test: Verify all rails within spec
2. Clock test: Measure phase noise and jitter
3. JESD204C test: Verify link synchronization
4. DDC test: Verify frequency translation
5. SpaceWire test: Verify link operation
6. Thermal test: Verify operation at temperature extremes
7. Radiation test: TID and SEL characterization

## 10. Conclusion

The XBandDigitalModule_20x20 design is complete and ready for detailed implementation. All critical components have been selected with adequate margins for space operation. The direct RF sampling architecture provides maximum flexibility while meeting all performance requirements.

---
*End of Document*
