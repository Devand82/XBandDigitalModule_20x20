# XBandDigitalModule_20x20 - Architecture Comparison

## Document Information
| Field | Value |
|---|---|
| Document ID | XBDM-DOC-005 |
| Version | 1.0 |
| Date | 2026-09-09 |
| Classification | ITAR Restricted |

## 1. Executive Summary

This document compares four RF sampling architectures for the XBandDigitalModule_20x20, evaluating trade-offs in performance, complexity, power, and risk. The **Direct RF Sampling** architecture is selected as the optimal solution.

## 2. Architecture Options

### 2.1 Option 1: Direct RF Sampling (SELECTED)

**Description**: ADC samples X-band signal directly at 10.4 GSPS.

```
RF In (8-12 GHz) → BPF → LNA → Balun → ADC (10.4 GSPS) → FPGA
```

| Aspect | Evaluation |
|---|---|
| **Components** | Minimal (BPF, LNA, Balun, ADC) |
| **ADC Requirement** | 10.4 GSPS, 8 GHz BW, 12-bit |
| **Clock Requirement** | 10.4 GHz, <100 fs jitter |
| **FPGA Requirement** | 16-lane JESD204C @ 16 Gbps |
| **SNR** | ~55 dB (limited by jitter at 10 GHz) |
| **Flexibility** | Highest (software tunable) |
| **Size** | Smallest |
| **Power** | 72-96 W |
| **Complexity** | Low (analog), High (digital) |
| **Risk** | Medium (new technique) |
| **Heritage** | Growing (TI TIDA-010274) |

**Pros**:
- Minimal analog components
- Maximum flexibility
- Smallest size
- Software-defined frequency selection

**Cons**:
- Requires highest-performance ADC
- Clock jitter critical
- High FPGA processing load

### 2.2 Option 2: Bandpass Sampling

**Description**: ADC samples at sub-Nyquist rate, using aliasing intentionally.

```
RF In (8-12 GHz) → BPF → LNA → ADC (2-4 GSPS) → FPGA
```

| Aspect | Evaluation |
|---|---|
| **Components** | Minimal (BPF, LNA, ADC) |
| **ADC Requirement** | 2-4 GSPS, 8 GHz BW |
| **Clock Requirement** | 2-4 GHz, <200 fs jitter |
| **FPGA Requirement** | 8-lane JESD204C @ 10 Gbps |
| **SNR** | ~45-50 dB (degraded by aliasing) |
| **Flexibility** | Low (fixed bands) |
| **Size** | Small |
| **Power** | 40-60 W |
| **Complexity** | Medium (aliasing management) |
| **Risk** | Medium-High |
| **Heritage** | Limited for X-band |

**Pros**:
- Lower ADC speed requirement
- Reduced FPGA load
- Lower power

**Cons**:
- Complex aliasing management
- Limited bandwidth per Nyquist zone
- SNR degradation
- Less flexible

### 2.3 Option 3: Analog Downconversion

**Description**: Mixer translates X-band to IF, then ADC samples IF.

```
RF In (8-12 GHz) → BPF → LNA → Mixer → IF BPF → ADC (1-2 GSPS) → FPGA
                       ↑
                       LO (8-12 GHz synthesizer)
```

| Aspect | Evaluation |
|---|---|
| **Components** | Many (Mixer, LO, IF filters, LO synth) |
| **ADC Requirement** | 1-2 GSPS, 500 MHz BW |
| **Clock Requirement** | 1-2 GHz, <500 fs jitter |
| **FPGA Requirement** | 4-lane JESD204C @ 5 Gbps |
| **SNR** | ~65-70 dB (best) |
| **Flexibility** | Low (fixed LO frequency) |
| **Size** | Medium |
| **Power** | 20-40 W |
| **Complexity** | High (analog), Low (digital) |
| **Risk** | Low (traditional) |
| **Heritage** | Excellent (decades) |

**Pros**:
- Best SNR performance
- Lowest ADC speed requirement
- Lowest FPGA load
- Proven technology

**Cons**:
- Most components (mixer, LO, filters)
- LO phase noise adds to signal
- Larger size
- Fixed frequency (less flexible)

### 2.4 Option 4: Hybrid IF Digital

**Description**: Two-stage conversion with digital IF processing.

```
RF In (8-12 GHz) → BPF → LNA → Mixer → IF (500 MHz) → ADC (1 GSPS) → FPGA
                       ↑                                    ↑
                       LO (first)                          Clock
```

| Aspect | Evaluation |
|---|---|
| **Components** | Moderate (Mixer, LO, IF filter) |
| **ADC Requirement** | 1 GSPS, 500 MHz BW |
| **Clock Requirement** | 1 GHz, <500 fs jitter |
| **FPGA Requirement** | 4-lane JESD204C @ 5 Gbps |
| **SNR** | ~60-65 dB |
| **Flexibility** | Medium |
| **Size** | Medium |
| **Power** | 25-45 W |
| **Complexity** | Medium (analog + digital) |
| **Risk** | Low-Medium |
| **Heritage** | Good |

**Pros**:
- Balanced performance
- Moderate component count
- Good SNR

**Cons**:
- Still requires analog mixer
- More complex than direct sampling
- LO noise contribution

## 3. Comparison Matrix

| Criterion | Weight | Direct RF | Bandpass | Downconv | Hybrid | Winner |
|---|---|---|---|---|---|---|
| SNR Performance | 20% | 7 | 5 | 9 | 7 | Downconv |
| Flexibility | 15% | 10 | 4 | 3 | 5 | Direct RF |
| Component Count | 15% | 9 | 8 | 4 | 6 | Direct RF |
| Size | 10% | 9 | 8 | 5 | 6 | Direct RF |
| Power | 10% | 5 | 7 | 9 | 7 | Downconv |
| Risk | 15% | 6 | 4 | 9 | 7 | Downconv |
| Heritage | 15% | 6 | 3 | 9 | 7 | Downconv |
| **Weighted Score** | **100%** | **7.35** | **5.55** | **6.85** | **6.35** | **Direct RF** |

## 4. Component Availability

### 4.1 ADC Options

| Architecture | Required ADC | Available | Status |
|---|---|---|---|
| Direct RF | 10+ GSPS, 8 GHz BW | ADC12DJ5200-SP (10.4 GSPS, 8 GHz) | ✅ Available |
| Bandpass | 2-4 GSPS, 8 GHz BW | ADC12DJ3200QML-SP (6.4 GSPS, 7 GHz) | ✅ Available |
| Downconv | 1-2 GSPS, 500 MHz BW | EV12AQ600 (6.4 GSPS) | ✅ Available |
| Hybrid | 1 GSPS, 500 MHz BW | ADC12DJ3200QML-SP | ✅ Available |

### 4.2 FPGA Options

| Architecture | Required FPGA | Available | Status |
|---|---|---|---|
| Direct RF | 16+ Gbps transceivers | XQRVC1902 (26.5 Gbps) | ✅ Available |
| Bandpass | 10+ Gbps transceivers | XQRKU060 (12.5 Gbps) | ✅ Available |
| Downconv | 5+ Gbps transceivers | XQRKU060 | ✅ Available |
| Hybrid | 5+ Gbps transceivers | XQRKU060 | ✅ Available |

## 5. Trade-off Analysis

### 5.1 SNR vs. Flexibility

```
SNR (dB)
  70 ┤                    ● Downconv
     │
  65 ┤                              ● Hybrid
     │
  60 ┤
     │
  55 ┤        ● Direct RF
     │
  50 ┤              ● Bandpass
     │
  45 ┼──────────────────────────────────►
     Low    Medium    High    Very High
                Flexibility
```

### 5.2 Size vs. Power

```
Power (W)
  100 ┤        ● Direct RF
      │
   80 ┤
      │
   60 ┤              ● Bandpass
      │
   40 ┤                              ● Hybrid
      │                    ● Downconv
   20 ┤
      │
    0 ┼──────────────────────────────────►
      Small   Medium   Large   Very Large
                Size (cm²)
```

### 5.3 Risk vs. Heritage

```
Heritage (years)
  30 ┤                    ● Downconv
     │
  20 ┤
     │
  10 ┤                              ● Hybrid
     │
   5 ┤
     │        ● Direct RF
   0 ┤              ● Bandpass
     ┼──────────────────────────────────►
     Low    Medium    High    Very High
                Risk
```

## 6. Sensitivity Analysis

### 6.1 If SNR is Most Critical

**Winner**: Analog Downconversion (Option 3)
- Best SNR: 65-70 dB
- Trade-off: Larger size, more components

### 6.2 If Size is Most Critical

**Winner**: Direct RF Sampling (Option 1)
- Smallest: Minimal components
- Trade-off: Lower SNR, higher risk

### 6.3 If Risk is Most Critical

**Winner**: Analog Downconversion (Option 3)
- Lowest risk: Proven technology
- Trade-off: Larger size, less flexible

## 7. Recommendation

### 7.1 Selected Architecture: Direct RF Sampling

**Rationale**:
1. **Highest weighted score** (7.35 vs. 6.85 for downconversion)
2. **Maximum flexibility** for future missions
3. **Smallest size** fits 20x20 cm module with margin
4. **Growing heritage** in modern space payloads
5. **Component availability** confirmed (ADC12DJ5200-SP, XQRVC1902)

### 7.2 Risk Mitigation

To address the higher risk of direct RF sampling:
1. Use proven reference design (TI TIDA-010274)
2. Implement robust clock subsystem (LMX2615-SP + LMK04832-SP)
3. Include debug/test capabilities for validation
4. Plan prototype testing before flight hardware

### 7.3 Alternative Recommendation

If direct RF sampling risk is unacceptable:
- **Second choice**: Analog Downconversion (Option 3)
- **Rationale**: Lowest risk, best SNR, proven heritage
- **Trade-off**: Larger size, more components, less flexible

## 8. Revision History

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | 2026-09-09 | System Engineering | Initial release |

---
*End of Document*
