# XBandDigitalModule_20x20 - BOM Alternatives

## Document Information
| Field | Value |
|---|---|
| Document ID | XBDM-DOC-014 |
| Version | 1.0 |
| Date | 2026-09-09 |
| Classification | ITAR Restricted |

## 1. Primary vs Alternative Components

### 1.1 Critical Components

| Component | Primary | Alternative | Trade-off |
|---|---|---|---|
| ADC | ADC12DJ5200-SP | ADC12DJ5200-SEP | Lower TID (30krad vs 300krad), lower cost |
| FPGA | XQRVC1902 | XQRKU060 | Lower speed (12.5Gbps), lower cost |
| Clock Synth | LMX2615-SP | LMX2694-SEP | Lower TID, smaller package |
| Clock Dist | LMK04832-SP | LMK04832-SEP | Lower TID, plastic package |
| Buck Controller | TPS7H5002-SP | RIC70847 | Newer, different vendor |
| LDO | TPS7H1111-SP | ISL75052SEH | Higher noise, different vendor |

### 1.2 Passive Components

| Component | Primary | Alternative | Notes |
|---|---|---|---|
| MLCC 10uF 25V | TDK C3225X5R1E106K | Murata GRM31CR61E106K | Equivalent |
| MLCC 10uF 10V | TDK C3225X5R1A106K | Samsung CL32A106KAYNNNE | Equivalent |
| MLCC 100nF 16V | Murata GRM188R71C104K | TDK C1005X7R1C104K | Equivalent |
| Inductor 4uH | Coilcraft XAL6060-402 | Würth 7443551400 | Verify saturation current |
| Ferrite Bead | Murata BLM18AG102 | TDK MPZ2012S102A | Equivalent |

## 2. Multi-Source Strategy

### 2.1 Critical Components (Single Source)

| Component | Vendor | Reason | Risk |
|---|---|---|---|
| ADC12DJ5200-SP | Texas Instruments | Only space-grade ADC with 8 GHz BW | High |
| XQRVC1902 | AMD/Xilinx | Only space-grade FPGA with 26.5 Gbps | High |
| LMX2615-SP | Texas Instruments | Only QML synthesizer to 15 GHz | Medium |

### 2.2 Dual-Source Components

| Component | Source 1 | Source 2 | Notes |
|---|---|---|---|
| Buck Regulator | ISL70003ASEH (Renesas) | ISL71001SLHM (Renesas) | Same vendor, different package |
| LDO | TPS7H1111-SP (TI) | ISL75052SEH (Renesas) | Different vendors |
| Sequencer | TPS7H3014-SP (TI) | ISL70321SEH (Renesas) | Different vendors |
| MOSFET | CSD19538Q3A (TI) | IRFB4110PBF (IR) | Different vendors |

## 3. Cost Analysis

### 3.1 Unit Cost Breakdown

| Category | Primary Cost | Alternative Cost | Savings |
|---|---|---|---|
| ADC | $850 | $650 (SEP) | $200 |
| FPGA | $180,000 | $100,000 (KU060) | $80,000 |
| Clock | $450 | $350 (SEP) | $100 |
| Power | $334 | $300 | $34 |
| Passive | $100 | $90 | $10 |
| Mechanical | $2,600 | $2,500 | $100 |
| Assembly | $5,000 | $5,000 | $0 |
| **Total** | **$189,334** | **$108,890** | **$80,444** |

### 3.2 Quantity Price Breaks

| Quantity | Unit Price | Total | Notes |
|---|---|---|---|
| 1 | $189,334 | $189,334 | Single unit |
| 5 | $165,000 | $825,000 | Small batch |
| 10 | $145,000 | $1,450,000 | Production run |
| 25 | $125,000 | $3,125,000 | High volume |

### 3.3 Non-Recurring Engineering (NRE)

| Item | Cost | Notes |
|---|---|---|
| PCB Fabrication | $5,000 | 12-layer, high-speed |
| Stencil | $500 | For SMT assembly |
| Test Fixtures | $10,000 | Custom test jig |
| Qualification | $50,000 | Radiation, environmental |
| Documentation | $5,000 | Technical manuals |
| **Total NRE** | **$70,500** | - |

## 4. Availability Assessment

### 4.1 Current Stock (Estimated)

| Component | Distributor Stock | Lead Time |
|---|---|---|
| ADC12DJ5200-SP | 50 units | 16-20 weeks |
| XQRVC1902 | 10 units | 20-26 weeks |
| LMX2615-SP | 100 units | 12-16 weeks |
| LMK04832-SP | 80 units | 12-16 weeks |
| ISL70003ASEH | 200 units | 8-12 weeks |
| TPS7H1111-SP | 150 units | 8-12 weeks |

### 4.2 Risk Items

| Component | Risk Level | Mitigation |
|---|---|---|
| XQRVC1902 | High | Order immediately, consider KU060 |
| ADC12DJ5200-SP | Medium | Order in advance |
| LMX2615-SP | Low | Adequate stock |

## 5. Derating Summary

### 5.1 Voltage Derating

| Component | Operating | Rated | Derating |
|---|---|---|---|
| ADC12DJ5200-SP (AVDD) | 1.0V | 1.1V | 91% |
| XQRVC1902 (VCCINT) | 1.0V | 1.05V | 95% |
| MLCC 25V | 5.5V | 25V | 22% |
| MOSFET 100V | 5.5V | 100V | 5.5% |

### 5.2 Current Derating

| Component | Operating | Rated | Derating |
|---|---|---|---|
| ISL70003ASEH | 4A | 9A | 44% |
| TPS7H1111-SP | 1.2A | 1.5A | 80% |
| MOSFET CSD19538Q3A | 44A | 100A | 44% |

### 5.3 Temperature Derating

| Component | Operating | Rated | Derating |
|---|---|---|---|
| FPGA | 120°C | 125°C | 96% |
| ADC | 110°C | 125°C | 88% |
| LDO | 100°C | 125°C | 80% |

## 6. Revision History

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | 2026-09-09 | Procurement Engineer | Initial release |

---
*End of Document*
