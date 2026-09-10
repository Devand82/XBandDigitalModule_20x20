# XBandDigitalModule_20x20 - ICD VHDL

## Document Information
| Field | Value |
|---|---|
| Document ID | XBDM-DOC-009 |
| Version | 1.0 |
| Date | 2026-09-09 |
| Classification | ITAR Restricted |
| Status | Preliminary Design Review |

## 1. Digital Architecture Overview

### 1.1 Module Hierarchy

```
top_module
├── jesd204c_receiver
│   ├── lane_sync (x16)
│   ├── frame_align
│   └── descrambler
├── ddc_chain
│   ├── nco (x8)
│   ├── cic_decimator (x8)
│   └── fir_filter (x8)
├── fifo_buffer
│   ├── async_fifo (x8)
│   └── sync_fifo
├── error_handler
│   ├── edac
│   ├── crc
│   └── fault_log
├── clock_manager
│   ├── pll_ctrl
│   └── sysref_gen
├── spacewire_interface
│   ├── spw_link (x2)
│   ├── spw_codec (x2)
│   └── spw_router
└── axi4_lite_slave
    ├── register_file
    └── irq_controller
```

### 1.2 Clock Domains

| Domain | Frequency | Source | Description |
|---|---|---|---|
| sys_clk | 100 MHz | LMK04832-SP | System clock |
| jesd_clk | 10.4 GHz / 66 | JESD204C | JESD204C framing clock |
| ddc_clk | 500 MHz | PLL | DDC processing clock |
| spw_clk | 100 MHz | SpaceWire | SpaceWire link clock |
| axi_clk | 100 MHz | LMK04832-SP | AXI bus clock |

### 1.3 Reset Strategy

| Reset Source | Type | Duration | Affected Modules |
|---|---|---|---|
| power_on | Synchronous | 16 cycles | All |
| software | Synchronous | 8 cycles | All except clock_manager |
| watchdog | Asynchronous | 16 cycles | All |
| error | Synchronous | 8 cycles | error_handler, ddc_chain |

## 2. Register Map

### 2.1 Register Map Summary

| Address Range | Name | Access | Description |
|---|---|---|---|
| 0x0000-0x003F | SYS_CTRL | R/W | System control and status |
| 0x0040-0x007F | ADC_CTRL | R/W | ADC configuration |
| 0x0080-0x00BF | FPGA_CTRL | R/W | FPGA configuration |
| 0x00C0-0x00FF | POWER_CTRL | R/W | Power management |
| 0x0100-0x013F | CLOCK_CTRL | R/W | Clock configuration |
| 0x0140-0x017F | ERROR_CTRL | R/W | Error handling |
| 0x0180-0x01BF | DIAG_CTRL | R/W | Diagnostics |
| 0x0200-0x02FF | DDC_CTRL | R/W | DDC configuration (8 channels) |
| 0x0300-0x03FF | SPACEWIRE_CTRL | R/W | SpaceWire configuration |
| 0x0400-0x04FF | BUFFER_CTRL | R/W | Buffer management |
| 0x0500-0x05FF | TRACE_CTRL | R/W | Debug trace |
| 0x1000-0x1FFF | USER_REGS | R/W | User-defined registers |

### 2.2 System Control Registers (0x0000-0x003F)

#### 0x0000: SYS_STATUS

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:24] | REVISION | R | 0x01 | Firmware revision |
| [23:16] | STATUS | R | 0x00 | System status |
| [15:8] | ERROR | R | 0x00 | Error flags |
| [7:0] | VERSION | R | 0x00 | Version ID |

**STATUS bits**:
- [23]: DONE - FPGA configuration complete
- [22]: LOCKED - PLL locked
- [21]: SYSREF - SYSREF valid
- [20]: JESD_SYNC - JESD204C synchronized
- [19]: DDR_READY - DDR memory ready
- [18]: SPW_LINK - SpaceWire link up
- [17:16]: reserved

**ERROR bits**:
- [15]: ADC_ERR - ADC error
- [14]: FPGA_ERR - FPGA error
- [13]: CLOCK_ERR - Clock error
- [12]: POWER_ERR - Power error
- [11]: TEMP_ERR - Temperature error
- [10]: OVERFLOW - Data overflow
- [9:8]: reserved

#### 0x0004: SYS_CTRL

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:28] | RESET | W | 0x00 | Reset control |
| [27:24] | ENABLE | R/W | 0x00 | Module enable |
| [23:16] | MODE | R/W | 0x00 | Operating mode |
| [15:0] | reserved | R/W | 0x0000 | - |

**RESET bits** (write 1 to assert):
- [31]: SYS_RST - System reset
- [30]: ADC_RST - ADC reset
- [29]: FPGA_RST - FPGA logic reset
- [28]: SPW_RST - SpaceWire reset

**ENABLE bits** (write 1 to enable):
- [27]: ADC_EN - ADC enable
- [26]: DDC_EN - DDC enable
- [25]: BUFFER_EN - Buffer enable
- [24]: SPW_EN - SpaceWire enable

**MODE bits**:
- [23:20]: OPER_MODE - 0x0: Normal, 0x1: Test, 0x2: Debug, 0x3: Sleep
- [19:16]: SAMPLE_MODE - 0x0: Single, 0x1: Continuous, 0x2: Triggered

#### 0x0008: SYS_CONFIG

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:24] | reserved | R/W | 0x00 | - |
| [23:16] | WATCHDOG | R/W | 0xFF | Watchdog timeout (ms) |
| [15:8] | TEMPOUT | R/W | 0x80 | Temperature alarm (°C) |
| [7:0] | DEBUG | R/W | 0x00 | Debug mode |

#### 0x000C: SYS_IRQ_STATUS

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:16] | reserved | R | 0x0000 | - |
| [15] | IRQ_TEMP | R | 0 | Temperature alarm |
| [14] | IRQ_OVERFLOW | R | 0 | Data overflow |
| [13] | IRQ_ERROR | R | 0 | System error |
| [12] | IRQ_JESD | R | 0 | JESD204C status change |
| [11] | IRQ_SPW | R | 0 | SpaceWire event |
| [10] | IRQ_WDOG | R | 0 | Watchdog timeout |
| [9:0] | reserved | R | 0x000 | - |

#### 0x0010: SYS_IRQ_ENABLE

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:16] | reserved | R/W | 0x0000 | - |
| [15] | EN_IRQ_TEMP | R/W | 0 | Enable temperature IRQ |
| [14] | EN_IRQ_OVERFLOW | R/W | 0 | Enable overflow IRQ |
| [13] | EN_IRQ_ERROR | R/W | 0 | Enable error IRQ |
| [12] | EN_IRQ_JESD | R/W | 0 | Enable JESD IRQ |
| [11] | EN_IRQ_SPW | R/W | 0 | Enable SpaceWire IRQ |
| [10] | EN_IRQ_WDOG | R/W | 0 | Enable watchdog IRQ |
| [9:0] | reserved | R/W | 0x000 | - |

### 2.3 ADC Control Registers (0x0040-0x007F)

#### 0x0040: ADC_CTRL

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:28] | DECIMATION | R/W | 0x0 | Decimation factor (0:1, 1:2, 2:4, 3:8, 4:16) |
| [27:24] | GAIN | R/W | 0x0 | Digital gain (0:0dB, 1:6dB, 2:12dB, 3:18dB) |
| [23:20] | TEST_MODE | R/W | 0x0 | Test pattern (0:off, 1:sync, 2:step, 3:PRBS) |
| [19:16] | FORMAT | R/W | 0x0 | Data format (0:offset binary, 1:twos complement) |
| [15:12] | reserved | R/W | 0x0 | - |
| [11:8] | JESD_MODE | R/W | 0x0 | JESD mode (0:204B, 1:204C) |
| [7:4] | LANE_EN | R/W | 0xF | Lane enable (bit per lane) |
| [3:0] | reserved | R/W | 0x0 | - |

#### 0x0044: ADC_STATUS

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:24] | JESD_STATUS | R | 0x00 | JESD204C status |
| [23:16] | FIFO_LEVEL | R | 0x00 | FIFO fill level (0-255) |
| [15:8] | ERROR | R | 0x00 | ADC error flags |
| [7:0] | reserved | R | 0x00 | - |

**JESD_STATUS bits**:
- [31]: SYNC - All lanes synchronized
- [30]: SYSREF_VALID - SYSREF received
- [29:24]: CODE_ERR - Code error count (saturated)
- [23:16]: reserved

**ERROR bits**:
- [15]: OVERFLOW - ADC overflow
- [14]: UNDERFLOW - ADC underflow
- [13]: JESD_ERR - JESD204C error
- [12:8]: reserved

#### 0x0048: ADC_NCO_FREQ

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:0] | FREQ_WORD | R/W | 0x00000000 | NCO frequency word |

**Calculation**: FREQ_WORD = (f_IF / f_sample) × 2³²

#### 0x004C: ADC_NCO_PHASE

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:16] | PHASE_OFF | R/W | 0x0000 | NCO phase offset |
| [15:0] | reserved | R/W | 0x0000 | - |

### 2.4 FPGA Control Registers (0x0080-0x00BF)

#### 0x0080: FPGA_TEMP

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:16] | reserved | R | 0x0000 | - |
| [15:8] | TEMP_RAW | R | 0x00 | Raw temperature (8-bit) |
| [7:0] | TEMP Converted | R | 0x00 | Temperature (°C) |

#### 0x0084: FPGA_VOLTAGE

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:16] | reserved | R | 0x0000 | - |
| [15:8] | VCCINT | R | 0x00 | Core voltage (8-bit) |
| [7:0] | VCCAUX | R | 0x00 | Aux voltage (8-bit) |

#### 0x0088: FPGA_CONFIG

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:24] | VERSION | R | 0x00 | FPGA version |
| [23:16] | BUILD_DATE | R | 0x00 | Build date |
| [15:8] | BUILD_TIME | R | 0x00 | Build time |
| [7:0] | CONFIG_DONE | R | 0x00 | Configuration status |

### 2.5 Power Control Registers (0x00C0-0x00FF)

#### 0x00C0: POWER_STATUS

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:28] | RAIL_STATUS | R | 0xF | Rail power-good (bit per rail) |
| [27:24] | CURRENT | R | 0x0 | Current (4-bit, 0-25A) |
| [23:16] | reserved | R | 0x00 | - |
| [15:8] | SEQUENCER_STATUS | R | 0x00 | Sequencer status |
| [7:0] | FAULT_STATUS | R | 0x00 | Fault status |

**RAIL_STATUS bits**:
- [31]: VCCINT_OK
- [30]: VCCAUX_OK
- [29]: VCCO_OK
- [28]: AVDD_OK

#### 0x00C4: POWER_CTRL

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:28] | RAIL_ENABLE | R/W | 0x0 | Rail enable (bit per rail) |
| [27:24] | SEQUENCER_CTRL | R/W | 0x0 | Sequencer control |
| [23:16] | CURRENT_LIMIT | R/W | 0x0 | Current limit setting |
| [15:0] | reserved | R/W | 0x0000 | - |

### 2.6 Clock Control Registers (0x0100-0x013F)

#### 0x0100: CLOCK_STATUS

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:28] | PLL_LOCKED | R | 0x0 | PLL lock status |
| [27:24] | reserved | R | 0x0 | - |
| [23:16] | JITTER | R | 0x00 | Jitter (8-bit, 0-255 fs) |
| [15:0] | FREQ_ACTUAL | R | 0x0000 | Actual frequency (MHz) |

#### 0x0104: CLOCK_CTRL

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:28] | PLL_RESET | W | 0x0 | PLL reset (write 1 to reset) |
| [27:24] | PLL_ENABLE | R/W | 0x0 | PLL enable |
| [23:16] | DIVIDER | R/W | 0x00 | Output divider |
| [15:0] | reserved | R/W | 0x0000 | - |

#### 0x0108: CLOCK_NCO_FREQ

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:0] | FREQ_WORD | R/W | 0x00000000 | Clock frequency word |

### 2.7 Error Control Registers (0x0140-0x017F)

#### 0x0140: ERROR_STATUS

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:24] | ADC_ERROR | R | 0x00 | ADC error count |
| [23:16] | FPGA_ERROR | R | 0x00 | FPGA error count |
| [15:8] | CLOCK_ERROR | R | 0x00 | Clock error count |
| [7:0] | POWER_ERROR | R | 0x00 | Power error count |

#### 0x0144: ERROR_CTRL

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:28] | ERROR_MASK | R/W | 0xF | Error mask (bit per source) |
| [27:24] | ERROR_ACTION | R/W | 0x0 | Error action (0:log, 1:interrupt, 2:reset) |
| [23:16] | reserved | R/W | 0x00 | - |
| [15:0] | ERROR_THRESHOLD | R/W | 0x0100 | Error threshold |

#### 0x0148: ERROR_LOG

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:16] | TIMESTAMP | R | 0x0000 | Error timestamp (16-bit) |
| [15:8] | ERROR_TYPE | R | 0x00 | Error type |
| [7:0] | ERROR_SOURCE | R | 0x00 | Error source |

### 2.8 Diagnostics Control Registers (0x0180-0x01BF)

#### 0x0180: DIAG_CTRL

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:28] | TEST_PATTERN | R/W | 0x0 | Test pattern select |
| [27:24] | LOOPBACK | R/W | 0x0 | Loopback mode |
| [23:16] | PRBS_EN | R/W | 0x0 | PRBS generator enable |
| [15:0] | reserved | R/W | 0x0000 | - |

#### 0x0184: DIAG_STATUS

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:24] | PATTERN_ERR | R | 0x00 | Pattern error count |
| [23:16] | BIT_ERR | R | 0x00 | Bit error count |
| [15:8] | FRAME_ERR | R | 0x00 | Frame error count |
| [7:0] | reserved | R | 0x00 | - |

### 2.9 DDC Control Registers (0x0200-0x02FF)

**8 DDC channels, each with 16 registers (0x20 bytes per channel)**

| Channel | Base Address | Registers |
|---|---|---|
| DDC0 | 0x0200 | 0x0200-0x021F |
| DDC1 | 0x0220 | 0x0220-0x023F |
| DDC2 | 0x0240 | 0x0240-0x025F |
| DDC3 | 0x0260 | 0x0260-0x027F |
| DDC4 | 0x0280 | 0x0280-0x029F |
| DDC5 | 0x02A0 | 0x02A0-0x02BF |
| DDC6 | 0x02C0 | 0x02C0-0x02DF |
| DDC7 | 0x02E0 | 0x02E0-0x02FF |

#### DDC Channel Register Map (per channel)

| Offset | Name | Access | Description |
|---|---|---|---|
| 0x00 | DDC_CTRL | R/W | Channel control |
| 0x04 | DDC_STATUS | R | Channel status |
| 0x08 | DDC_FREQ_LOW | R/W | Frequency word [31:0] |
| 0x0C | DDC_FREQ_HIGH | R/W | Frequency word [47:32] |
| 0x10 | DDC_PHASE | R/W | Phase offset |
| 0x14 | DDC_GAIN | R/W | Gain control |
| 0x18 | DDC_OFFSET_I | R/W | I offset |
| 0x1C | DDC_OFFSET_Q | R/W | Q offset |

**DDC_CTRL bits**:
- [31]: ENABLE - Channel enable
- [30:28]: DECIMATION - Decimation factor
- [27:24]: MODE - Mode select
- [23:0]: reserved

**DDC_STATUS bits**:
- [31]: ACTIVE - Channel active
- [30]: OVERFLOW - Output overflow
- [29:24]: FILL_LEVEL - FIFO fill level
- [23:0]: reserved

### 2.10 SpaceWire Control Registers (0x0300-0x03FF)

#### 0x0300: SPW_STATUS

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:28] | LINK_STATUS | R | 0x0 | Link status (bit per link) |
| [27:24] | reserved | R | 0x0 | - |
| [23:16] | TX_COUNT | R | 0x00 | TX packet count |
| [15:8] | RX_COUNT | R | 0x00 | RX packet count |
| [7:0] | ERROR_COUNT | R | 0x00 | Error count |

**LINK_STATUS bits**:
- [31]: LINK0_RUN - Link 0 running
- [30]: LINK0_DISCONNECT - Link 0 disconnected
- [29]: LINK0_ERROR - Link 0 error
- [28]: LINK1_RUN - Link 1 running

#### 0x0304: SPW_CTRL

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:28] | LINK_ENABLE | R/W | 0x0 | Link enable |
| [27:24] | LINK_RESET | W | 0x0 | Link reset |
| [23:16] | TX_ENABLE | R/W | 0x0 | TX enable |
| [15:8] | RX_ENABLE | R/W | 0x0 | RX enable |
| [7:0] | reserved | R/W | 0x00 | - |

#### 0x0308: SPW_CONFIG

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:24] | TX_THRESHOLD | R/W | 0x08 | TX threshold |
| [23:16] | RX_THRESHOLD | R/W | 0x08 | RX threshold |
| [15:8] | TIMEOUT | R/W | 0x64 | Timeout (ms) |
| [7:0] | reserved | R/W | 0x00 | - |

#### 0x030C-0x03FF: SPW_ROUTER

| Offset | Name | Access | Description |
|---|---|---|---|
| 0x030C | ROUTER_CONFIG | R/W | Router configuration |
| 0x0310 | ROUTER_TABLE | R/W | Routing table (32 entries) |
| 0x03F0 | ROUTER_STATUS | R | Router status |

### 2.11 Buffer Control Registers (0x0400-0x04FF)

#### 0x0400: BUFFER_STATUS

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:24] | FIFO_LEVEL | R | 0x00 | FIFO fill level |
| [23:16] | FIFO_FREE | R | 0xFF | FIFO free space |
| [15:8] | OVERFLOW_COUNT | R | 0x00 | Overflow count |
| [7:0] | UNDERFLOW_COUNT | R | 0x00 | Underflow count |

#### 0x0404: BUFFER_CTRL

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:28] | FIFO_RESET | W | 0x0 | FIFO reset |
| [27:24] | FIFO_ENABLE | R/W | 0x0 | FIFO enable |
| [23:16] | THRESHOLD_HIGH | R/W | 0xC0 | High threshold |
| [15:8] | THRESHOLD_LOW | R/W | 0x40 | Low threshold |
| [7:0] | reserved | R/W | 0x00 | - |

### 2.12 Trace Control Registers (0x0500-0x05FF)

#### 0x0500: TRACE_CTRL

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:28] | TRACE_ENABLE | R/W | 0x0 | Trace enable |
| [27:24] | TRACE_SOURCE | R/W | 0x0 | Trace source select |
| [23:16] | TRACE_TRIGGER | R/W | 0x00 | Trace trigger |
| [15:0] | TRACE_SIZE | R/W | 0x0100 | Trace buffer size |

#### 0x0504: TRACE_STATUS

| Bit | Name | Access | Reset | Description |
|---|---|---|---|---|
| [31:16] | TRACE_COUNT | R | 0x0000 | Current trace count |
| [15:8] | TRACE_STATE | R | 0x00 | Trace state |
| [7:0] | reserved | R | 0x00 | - |

## 3. Interrupt Architecture

### 3.1 Interrupt Sources

| Source | Priority | Vector | Description |
|---|---|---|---|
| Temperature alarm | High | 0x01 | Overtemperature |
| Power fault | High | 0x02 | Power supply error |
| Clock unlock | High | 0x03 | PLL lost lock |
| JESD error | Medium | 0x10 | JESD204C error |
| SpaceWire event | Medium | 0x20 | SpaceWire link event |
| Data overflow | Medium | 0x30 | FIFO overflow |
| Watchdog | Low | 0x40 | Watchdog timeout |
| Debug | Low | 0x50 | Debug event |

### 3.2 Interrupt Flow

```
Interrupt Source ──► Priority Encoder ──► IRQ Controller ──► ARM Cortex-R5F
                                          │
                                          ├──► IRQ_STATUS register
                                          ├──► IRQ_ENABLE mask
                                          └──► IRQ_CLEAR (write 1 to clear)
```

## 4. VHDL Module Interface Summary

### 4.1 top_module

```vhdl
entity top_module is
    port (
        -- Clock and Reset
        sys_clk         : in  std_logic;                      -- 100 MHz system clock
        sys_rst_n       : in  std_logic;                      -- Active low reset
        
        -- JESD204C Interface (to ADC)
        jesd_refclk_p   : in  std_logic;                      -- JESD reference clock
        jesd_refclk_n   : in  std_logic;
        jesd_tx_p       : in  std_logic_vector(15 downto 0);  -- JESD TX data
        jesd_tx_n       : in  std_logic_vector(15 downto 0);
        jesd_rx_p       : out std_logic_vector(15 downto 0);  -- JESD RX data
        jesd_rx_n       : out std_logic_vector(15 downto 0);
        jesd_sync_n     : out std_logic;                      -- JESD sync
        jesd_sysref     : in  std_logic;                      -- JESD SYSREF
        
        -- SpaceWire Interface
        spw0_dout_p     : out std_logic;                      -- SpaceWire 0 data+
        spw0_dout_n     : out std_logic;                      -- SpaceWire 0 data-
        spw0_sout_p     : out std_logic;                      -- SpaceWire 0 strobe+
        spw0_sout_n     : out std_logic;                      -- SpaceWire 0 strobe-
        spw0_din_p      : in  std_logic;                      -- SpaceWire 0 data+
        spw0_din_n      : in  std_logic;                      -- SpaceWire 0 data-
        spw0_sin_p      : in  std_logic;                      -- SpaceWire 0 strobe+
        spw0_sin_n      : in  std_logic;                      -- SpaceWire 0 strobe-
        spw1_dout_p     : out std_logic;                      -- SpaceWire 1 data+
        spw1_dout_n     : out std_logic;                      -- SpaceWire 1 data-
        spw1_sout_p     : out std_logic;                      -- SpaceWire 1 strobe+
        spw1_sout_n     : out std_logic;                      -- SpaceWire 1 strobe-
        spw1_din_p      : in  std_logic;                      -- SpaceWire 1 data+
        spw1_din_n      : in  std_logic;                      -- SpaceWire 1 data-
        spw1_sin_p      : in  std_logic;                      -- SpaceWire 1 strobe+
        spw1_sin_n      : in  std_logic;                      -- SpaceWire 1 strobe-
        
        -- SPI Interface (to Clock/Power)
        spi_mosi        : out std_logic;                      -- SPI master out
        spi_miso        : in  std_logic;                      -- SPI master in
        spi_sclk        : out std_logic;                      -- SPI clock
        spi_cs_n        : out std_logic_vector(3 downto 0);   -- SPI chip select
        
        -- I2C Interface (to Sensors)
        i2c_scl         : out std_logic;                      -- I2C clock
        i2c_sda         : inout std_logic;                    -- I2C data
        
        -- GPIO
        gpio            : inout std_logic_vector(7 downto 0); -- General purpose I/O
        
        -- Debug
        uart_tx         : out std_logic;                      -- UART TX
        uart_rx         : in  std_logic;                      -- UART RX
        led             : out std_logic_vector(3 downto 0)    -- Status LEDs
    );
end entity top_module;
```

### 4.2 jesd204c_receiver

```vhdl
entity jesd204c_receiver is
    generic (
        NUM_LANES   : integer := 16;
        DATA_WIDTH  : integer := 32
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        -- JESD204C physical
        rx_p        : in  std_logic_vector(NUM_LANES-1 downto 0);
        rx_n        : in  std_logic_vector(NUM_LANES-1 downto 0);
        refclk_p    : in  std_logic;
        refclk_n    : in  std_logic;
        sync_n      : out std_logic;
        sysref      : in  std_logic;
        -- Parallel data output
        data_out    : out std_logic_vector(DATA_WIDTH-1 downto 0);
        data_valid  : out std_logic;
        -- Status
        status      : out std_logic_vector(31 downto 0)
    );
end entity jesd204c_receiver;
```

### 4.3 ddc_chain

```vhdl
entity ddc_chain is
    generic (
        NUM_CHANNELS : integer := 8;
        DATA_WIDTH   : integer := 16;
        NCO_WIDTH    : integer := 48
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        -- Input
        data_in     : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        data_valid  : in  std_logic;
        -- Output (I/Q per channel)
        i_out       : out std_logic_vector(NUM_CHANNELS*DATA_WIDTH-1 downto 0);
        q_out       : out std_logic_vector(NUM_CHANNELS*DATA_WIDTH-1 downto 0);
        out_valid   : out std_logic;
        -- Control
        nco_freq    : in  std_logic_vector(NUM_CHANNELS*NCO_WIDTH-1 downto 0);
        nco_phase   : in  std_logic_vector(NUM_CHANNELS*16-1 downto 0);
        gain        : in  std_logic_vector(NUM_CHANNELS*4-1 downto 0);
        decimation  : in  std_logic_vector(NUM_CHANNELS*4-1 downto 0)
    );
end entity ddc_chain;
```

## 5. Revision History

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | 2026-09-09 | FPGA/VHDL Engineer | Initial release |

---
*End of Document*
