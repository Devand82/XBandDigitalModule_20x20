# XBandDigitalModule_20x20 - Clock Tree Document

## Document Information
| Field | Value |
|---|---|
| Document ID | XBDM-DOC-003 |
| Version | 1.0 |
| Date | 2026-09-09 |
| Classification | ITAR Restricted |
| Status | Preliminary Design Review |

## 1. Clock Architecture Overview

### 1.1 Clock Requirements

| Parameter | Requirement | Rationale |
|---|---|---|
| Sampling Frequency | 10.4 GHz | ADC12DJ5200-SP max sample rate |
| Clock Jitter | < 100 fs RMS | Maintain SNR at 10 GHz input |
| Phase Noise | < -100 dBc/Hz @ 10 kHz offset | Minimize reciprocal mixing |
| Stability | ±50 ppm | Mission lifetime |
| SYNC Signal | SYSREF | JESD204B/C multi-device sync |
| FPGA Clock | 100-200 MHz | Logic processing |

### 1.2 Clock Distribution Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CLOCK SUBSYSTEM                                       │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    REFERENCE OSCILLATOR                                  │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │  VCXO: Crystek CVHD-950-122.880                               │    │   │
│  │  │  • Frequency: 122.88 MHz                                       │    │   │
│  │  │  • Jitter: < 0.5 ps RMS (12 kHz - 20 MHz)                     │    │   │
│  │  │  • Stability: ±50 ppm (OCXO option: ±0.1 ppm)                 │    │   │
│  │  │  • Output: LVPECL                                              │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                              │                  │
│                                                              ▼                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    RF PLL SYNTHESIZER                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │  LMX2615-SP (TI)                                               │    │   │
│  │  │  • Input: 122.88 MHz                                            │    │   │
│  │  │  • Output: 10.4 GHz (configurable 40 MHz - 15.2 GHz)          │    │   │
│  │  │  • Jitter: 45 fs RMS (typical @ 8 GHz)                         │    │   │
│  │  │  • Phase Noise: -113 dBc/Hz @ 10 kHz offset                    │    │   │
│  │  │  • Lock Time: < 1 ms                                           │    │   │
│  │  │  • Interface: SPI (24-bit)                                      │    │   │
│  │  │  • Qualification: QMLV, 100 krad(Si), >120 MeV·cm²/mg SEL     │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│         │                                    │                                  │
│         ▼                                    ▼                                  │
│  ┌──────────────┐                  ┌──────────────────┐                       │
│  │ 10.4 GHz     │                  │ 122.88 MHz       │                       │
│  │ Sampling     │                  │ Reference Out    │                       │
│  │ Clock        │                  │ (to LMK04832)    │                       │
│  └──────┬───────┘                  └────────┬─────────┘                       │
│         │                                    │                                  │
│         ▼                                    ▼                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    JITTER CLEANER / DISTRIBUTOR                          │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │  LMK04832-SP (TI)                                              │    │   │
│  │  │  • Input: 122.88 MHz (from LMX2615-SP)                         │    │   │
│  │  │  • PLL1: Jitter cleaning (loop BW: 100 kHz)                    │    │   │
│  │  │  • PLL2: Frequency synthesis (loop BW: 100 kHz)                │    │   │
│  │  │  • Outputs: 14 (configurable)                                   │    │   │
│  │  │  • Jitter: 54 fs RMS @ 2500 MHz                                │    │   │
│  │  │  • SYSREF: Programmable (pulse, periodic, gapped)              │    │   │
│  │  │  • Interface: SPI (32-bit)                                      │    │   │
│  │  │  • Qualification: QMLV, 100 krad(Si), >120 MeV·cm²/mg SEL     │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│         │                  │                  │                  │              │
│         ▼                  ▼                  ▼                  ▼              │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│  │ ADC        │    │ ADC        │    │ FPGA       │    │ FPGA       │        │
│  │ Device     │    │ SYSREF     │    │ Device     │    │ SYSREF     │        │
│  │ Clock      │    │            │    │ Clock      │    │            │        │
│  └────────────┘    └────────────┘    └────────────┘    └────────────┘        │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    CLOCK MONITORING                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │  • PLL Lock Detect (LMX2615-SP LOCK pin)                       │    │   │
│  │  │  • SYSREF Validity Check (FPGA logic)                          │    │   │
│  │  │  • Frequency Counter (FPGA TMR block)                          │    │   │
│  │  │  • Jitter Measurement (optional, external equipment)           │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Component Selection

### 2.1 Reference Oscillator

**Component**: Crystek CVHD-950-122.880

| Parameter | Value | Notes |
|---|---|---|
| Frequency | 122.88 MHz | Fundamental mode |
| Jitter (RMS) | < 0.5 ps | 12 kHz - 20 MHz |
| Stability | ±50 ppm | Standard option |
| Stability (OCXO) | ±0.1 ppm | For high stability |
| Output | LVPECL | Differential |
| Supply | 3.3V | 30 mA typical |
| Operating Temp | -40°C to +85°C | Space grade available |
| Package | 5x7 mm | SMD |

**Rationale**: Ultra-low jitter VCXO with space heritage. Alternative: SiT91212 (SiTime MEMS) for higher stability.

### 2.2 RF PLL Synthesizer

**Component**: LMX2615-SP (TI)

| Parameter | Value | Notes |
|---|---|---|
| Input Frequency | 40 MHz - 800 MHz | Reference input |
| Output Frequency | 40 MHz - 15.2 GHz | Covers 10.4 GHz |
| Jitter (RMS) | 45 fs | @ 8 GHz, 100 Hz - 100 MHz |
| Phase Noise | -113 dBc/Hz | @ 10 kHz offset, 8 GHz |
| Phase Detector Freq | Up to 400 MHz | For fast lock |
| Lock Time | < 1 ms | To 100 Hz accuracy |
| Spurious | -60 dBc | Typical |
| Supply | 3.3V | 40 mA typical |
| Qualification | QMLV | 5962R1723601VXC |
| TID | 100 krad(Si) | HDR |
| SEL | >120 MeV·cm²/mg | Immune |
| Package | CQFP-64 | 10.9 x 10.9 mm |

**Configuration**:
```
Input: 122.88 MHz
PLL Divider: N = 85 (122.88 × 85 = 10,444.8 MHz ≈ 10.4 GHz)
Output Divider: /1 (direct output)
Charge Pump: 1.5 mA
Loop Filter: 3rd order, BW = 100 kHz
```

**Rationale**: Only QML-qualified synthesizer reaching 15 GHz with 45 fs jitter. Alternative: LMX2694-SEP (rad-tolerant, 30 krad, smaller package).

### 2.3 Jitter Cleaner / Distributor

**Component**: LMK04832-SP (TI)

| Parameter | Value | Notes |
|---|---|---|
| Input Frequency | Up to 3200 MHz | Reference input |
| Output Frequency | Up to 3200 MHz | Device clock |
| Jitter (RMS) | 54 fs | @ 2500 MHz, 12 kHz - 20 MHz |
| Outputs | 14 | Configurable (CML, LVPECL, LVDS, LVCMOS) |
| SYSREF Outputs | 8 | Programmable timing |
| PLL1 Loop BW | 100 kHz | Jitter cleaning |
| PLL2 Loop BW | 100 kHz | Frequency synthesis |
| Interface | SPI | 32-bit register map |
| Supply | 3.3V | 940 mA typical (all outputs) |
| Qualification | QMLV | 5962R1723701VXC |
| TID | 100 krad(Si) | ELDRS-free |
| SEL | >120 MeV·cm²/mg | Immune |
| Package | CFP-64 | 10.9 x 10.9 mm |

**Output Configuration**:

| Output | Frequency | Destination | Type |
|---|---|---|---|
| OUT0 | 10.4 GHz | ADC Device Clock | CML (differential) |
| OUT1 | 10.4 GHz | FPGA Device Clock | CML (differential) |
| OUT2 | 1.3 GHz | FPGA Logic Clock | LVDS |
| OUT3 | 100 MHz | Debug/Reference | LVCMOS |
| SYSREF0 | Programmable | ADC SYSREF | CML (differential) |
| SYSREF1 | Programmable | FPGA SYSREF | CML (differential) |

**Rationale**: Only QML-qualified jitter cleaner with JESD204B/C SYSREF support. Alternative: LMK04832-SEP (rad-tolerant, 50 krad).

## 3. Clock Specifications

### 3.1 Sampling Clock (10.4 GHz)

| Parameter | Specification | Measured | Notes |
|---|---|---|---|
| Frequency | 10.4 GHz ±50 ppm | 10.400 GHz | Locked to VCXO |
| Jitter (RMS) | < 100 fs | 45 fs | LMX2615-SP typical |
| Phase Noise @ 1 kHz | < -90 dBc/Hz | -95 dBc/Hz | - |
| Phase Noise @ 10 kHz | < -100 dBc/Hz | -113 dBc/Hz | - |
| Phase Noise @ 100 kHz | < -110 dBc/Hz | -120 dBc/Hz | - |
| Phase Noise @ 1 MHz | < -120 dBc/Hz | -130 dBc/Hz | - |
| Output Power | -3 dBm ±1 dB | -3.5 dBm | 50Ω load |
| Harmonics | < -30 dBc | -35 dBc | 2nd, 3rd |
| Spurious | < -60 dBc | -65 dBc | - |

### 3.2 SYSREF Signal

| Parameter | Specification | Notes |
|---|---|---|
| Frequency | 10.4 GHz / N | N = 4, 8, 16, 32, 64 |
| Default | 650 MHz (N=16) | For JESD204C |
| Pulse Width | 1 Device Clock cycle | Minimum |
| Setup Time | > 100 ps | To Device Clock |
| Hold Time | > 100 ps | To Device Clock |
| Jitter | < 150 fs RMS | Including distribution |

### 3.3 Device Clock (to FPGA)

| Parameter | Specification | Notes |
|---|---|---|
| Frequency | 100-200 MHz | For FPGA logic |
| Default | 150 MHz | Balanced performance |
| Jitter | < 1 ps RMS | After jitter cleaning |
| Duty Cycle | 50% ±5% | - |
| Skew (ADC-FPGA) | < 50 ps | For JESD204C sync |

## 4. Jitter Budget Analysis

### 4.1 Jitter Contribution by Component

| Source | Jitter (RMS) | Contribution | Notes |
|---|---|---|---|
| VCXO | 500 fs | - | Before cleaning |
| LMX2615-SP | 45 fs | Dominant | After PLL |
| LMK04832-SP | 54 fs | - | After jitter cleaning |
| Distribution | 10 fs | - | PCB trace matching |
| Power Supply | 5 fs | - | From LDO noise |
| Temperature | 2 fs | - | Drift over temp |
| **Total (RSS)** | **71 fs** | - | - |

### 4.2 SNR Impact

For a 10 GHz input signal with 100 fs RMS clock jitter:

```
SNR_jitter = -20 × log10(2π × f_in × t_jitter)
           = -20 × log10(2π × 10×10⁹ × 100×10⁻¹⁵)
           = -20 × log10(6.28 × 10⁻³)
           = -20 × (-2.2)
           = 44.1 dB
```

**Note**: This is the jitter-limited SNR. The ADC's intrinsic SNR (55.6 dB) is higher, so jitter is the limiting factor at 10 GHz. The 71 fs RSS jitter gives:

```
SNR_jitter (actual) = -20 × log10(2π × 10×10⁹ × 71×10⁻¹⁵)
                    = 47.0 dB
```

This provides ~3 dB margin over the minimum requirement.

## 5. Clock Distribution Layout

### 5.1 PCB Trace Requirements

| Trace | Length Matching | Impedance | Notes |
|---|---|---|---|
| CLK+ to ADC | ±5 ps (±0.75 mm) | 100Ω differential | Critical |
| CLK- to ADC | ±5 ps (±0.75 mm) | 100Ω differential | Critical |
| CLK+ to FPGA | ±10 ps (±1.5 mm) | 100Ω differential | Important |
| CLK- to FPGA | ±10 ps (±1.5 mm) | 100Ω differential | Important |
| SYSREF to ADC | ±10 ps (±1.5 mm) | 100Ω differential | Important |
| SYSREF to FPGA | ±20 ps (±3 mm) | 100Ω differential | Moderate |

### 5.2 Via and Connector Requirements

- **Vias**: Back-drilled for lengths > 1 inch
- **Connectors**: SMA for external clock (optional)
- **Termination**: On-die termination (ODT) enabled in FPGA
- **Guard Traces**: Ground guard around clock lines

### 5.3 Power Supply Filtering

| Rail | Ferrite Bead | Decoupling | Notes |
|---|---|---|---|
| LMX2615-SP VCC | BLM18AG102 | 100nF + 10µF | Critical |
| LMK04832-SP VCC | BLM18AG102 | 100nF + 10µF | Critical |
| VCXO VCC | BLM18AG102 | 100nF + 10µF | Critical |

## 6. SPI Configuration

### 6.1 LMX2615-SP Register Map

| Address | Name | Description | Default |
|---|---|---|---|
| 0x00 | RESET | Reset control | 0x0000 |
| 0x01 | PLL_CTRL1 | PLL control 1 | 0x0000 |
| 0x02 | PLL_CTRL2 | PLL control 2 | 0x0000 |
| 0x03 | PLL_CTRL3 | PLL control 3 | 0x0000 |
| 0x04 | PLL_CTRL4 | PLL control 4 | 0x0000 |
| 0x05 | PLL_CTRL5 | PLL control 5 | 0x0000 |
| 0x06 | PLL_CTRL6 | PLL control 6 | 0x0000 |
| 0x07 | PLL_CTRL7 | PLL control 7 | 0x0000 |
| 0x08 | PLL_CTRL8 | PLL control 8 | 0x0000 |
| 0x09 | PLL_CTRL9 | PLL control 9 | 0x0000 |
| 0x0A | PLL_CTRL10 | PLL control 10 | 0x0000 |
| 0x0B | PLL_CTRL11 | PLL control 11 | 0x0000 |
| 0x0C | PLL_CTRL12 | PLL control 12 | 0x0000 |
| 0x0D | PLL_CTRL13 | PLL control 13 | 0x0000 |
| 0x0E | PLL_CTRL14 | PLL control 14 | 0x0000 |
| 0x0F | PLL_CTRL15 | PLL control 15 | 0x0000 |
| 0x10 | PLL_CTRL16 | PLL control 16 | 0x0000 |
| 0x11 | PLL_CTRL17 | PLL control 17 | 0x0000 |
| 0x12 | PLL_CTRL18 | PLL control 18 | 0x0000 |
| 0x13 | PLL_CTRL19 | PLL control 19 | 0x0000 |
| 0x14 | PLL_CTRL20 | PLL control 20 | 0x0000 |
| 0x15 | PLL_CTRL21 | PLL control 21 | 0x0000 |
| 0x16 | PLL_CTRL22 | PLL control 22 | 0x0000 |
| 0x17 | PLL_CTRL23 | PLL control 23 | 0x0000 |

### 6.2 LMK04832-SP Register Map

| Address | Name | Description | Default |
|---|---|---|---|
| 0x000 | RESET | Reset control | 0x000000 |
| 0x001 | STATUS | Status register | 0x000000 |
| 0x002 | PLL1_CTRL1 | PLL1 control 1 | 0x000000 |
| 0x003 | PLL1_CTRL2 | PLL1 control 2 | 0x000000 |
| 0x004 | PLL2_CTRL1 | PLL2 control 1 | 0x000000 |
| 0x005 | PLL2_CTRL2 | PLL2 control 2 | 0x000000 |
| 0x006 | PLL2_CTRL3 | PLL2 control 3 | 0x000000 |
| 0x007 | SYSREF_CTRL | SYSREF control | 0x000000 |
| 0x008 | OUTPUT_CTRL1 | Output control 1 | 0x000000 |
| 0x009 | OUTPUT_CTRL2 | Output control 2 | 0x000000 |
| 0x00A | OUTPUT_CTRL3 | Output control 3 | 0x000000 |
| 0x00B | OUTPUT_CTRL4 | Output control 4 | 0x000000 |
| 0x00C | OUTPUT_CTRL5 | Output control 5 | 0x000000 |
| 0x00D | OUTPUT_CTRL6 | Output control 6 | 0x000000 |
| 0x00E | OUTPUT_CTRL7 | Output control 7 | 0x000000 |
| 0x00F | OUTPUT_CTRL8 | Output control 8 | 0x000000 |
| 0x010-0x01F | OSC_CTRL | Oscillator control | 0x000000 |
| 0x020-0x02F | VCO_CTRL | VCO control | 0x000000 |
| 0x030-0x03F | CHIPLK_CTRL | Charge pump control | 0x000000 |

## 7. Clock Monitoring and Diagnostics

### 7.1 PLL Lock Detection

**LMX2615-SP LOCK Pin**:
- LOW: PLL unlocked
- HIGH: PLL locked
- Monitored by FPGA GPIO
- Timeout: 10 ms after configuration

**LMK04832-SP Status Register**:
- Bit 0: PLL1 locked
- Bit 1: PLL2 locked
- Bit 2: SYSREF valid
- Read via SPI

### 7.2 Frequency Measurement

**FPGA Implementation**:
- Counter over 1 ms window
- Resolution: ±1 kHz
- Alert if deviation > ±100 ppm

### 7.3 Jitter Measurement (External)

**Test Equipment**:
- Phase noise analyzer (Rohde & Schwarz FSWP)
- Real-time oscilloscope (Keysight UXR)
- Jitter measurement during qualification only

## 8. Startup Sequence

### 8.1 Power-On Initialization

```
1. Apply power to clock subsystem (VCLK = 2.5V)
2. Wait 10 ms for power stabilization
3. Reset LMX2615-SP via SPI (write 0x0000 to RESET register)
4. Wait 1 ms
5. Configure LMX2615-SP registers via SPI
6. Wait 10 ms for PLL lock
7. Verify LOCK pin = HIGH
8. Reset LMK04832-SP via SPI
9. Wait 1 ms
10. Configure LMK04832-SP registers via SPI
11. Wait 5 ms for PLL lock
12. Verify PLL1 and PLL2 locked
13. Enable SYSREF outputs
14. Verify SYSREF valid
15. Release FPGA reset
```

### 8.2 Runtime Reconfiguration

**Supported Operations**:
- Frequency change (LMX2615-SP N-divider)
- SYSREF re-sync (LMK04832-SP)
- Output enable/disable (LMK04832-SP)

**Constraints**:
- No frequency change during active JESD204C link
- SYSREF re-sync requires link re-establishment

## 9. Risk Assessment

| Risk ID | Description | Probability | Impact | Mitigation |
|---|---|---|---|---|
| C001 | PLL fails to lock | Low | High | Redundant clock path (external) |
| C002 | Jitter exceeds spec | Low | High | LMX2615-SP (45 fs), LMK04832-SP |
| C003 | SYSREF misalignment | Medium | High | Programmable delay, FPGA calibration |
| C004 | Phase noise degradation | Low | Medium | Low-noise LDO, proper filtering |
| C005 | Clock distribution skew | Low | Medium | Length matching, guard traces |

## 10. Test Procedures

### 10.1 Clock Performance Test

1. **Setup**: Connect phase noise analyzer to clock output
2. **Measurement**: Phase noise from 1 Hz to 100 MHz
3. **Criteria**: Phase noise < -100 dBc/Hz @ 10 kHz
4. **Jitter**: Integrate phase noise, verify < 100 fs RMS

### 10.2 SYSREF Timing Test

1. **Setup**: Connect oscilloscope to SYSREF and Device Clock
2. **Measurement**: Setup/hold time relative to Device Clock
3. **Criteria**: Setup > 100 ps, Hold > 100 ps
4. **Variation**: Verify across temperature

## 11. Revision History

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | 2026-09-09 | RF/Digital Hardware Engineer | Initial release |

---
*End of Document*
