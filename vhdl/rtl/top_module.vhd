-- XBandDigitalModule_20x20 - Top Module
-- File: top_module.vhd
-- Description: Top-level entity for X-Band Digital Acquisition Module
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity top_module is
    generic (
        -- System parameters
        CLK_FREQ        : integer := 100_000_000;     -- 100 MHz system clock
        NUM_JESD_LANES  : integer := 16;               -- JESD204C lanes
        NUM_DDC_CHANNELS: integer := 8;                -- DDC channels
        NUM_SPW_LINKS   : integer := 2;                -- SpaceWire links
        DATA_WIDTH      : integer := 16;               -- ADC data width
        NCO_WIDTH       : integer := 48                -- NCO frequency width
    );
    port (
        -- Clock and Reset
        sys_clk         : in  std_logic;                       -- 100 MHz system clock
        sys_rst_n       : in  std_logic;                       -- Active low reset
        
        -- JESD204C Interface (to ADC12DJ5200-SP)
        jesd_refclk_p   : in  std_logic;                       -- JESD reference clock
        jesd_refclk_n   : in  std_logic;                       -- JESD reference clock (diff)
        jesd_tx_p       : in  std_logic_vector(NUM_JESD_LANES-1 downto 0);  -- JESD TX data
        jesd_tx_n       : in  std_logic_vector(NUM_JESD_LANES-1 downto 0);  -- JESD TX data (diff)
        jesd_rx_p       : out std_logic_vector(NUM_JESD_LANES-1 downto 0);  -- JESD RX data
        jesd_rx_n       : out std_logic_vector(NUM_JESD_LANES-1 downto 0);  -- JESD RX data (diff)
        jesd_sync_n     : out std_logic;                       -- JESD sync (active low)
        jesd_sysref     : in  std_logic;                       -- JESD SYSREF
        
        -- SpaceWire Interface (2 links)
        spw0_dout_p     : out std_logic;                       -- SpaceWire 0 data+
        spw0_dout_n     : out std_logic;                       -- SpaceWire 0 data-
        spw0_sout_p     : out std_logic;                       -- SpaceWire 0 strobe+
        spw0_sout_n     : out std_logic;                       -- SpaceWire 0 strobe-
        spw0_din_p      : in  std_logic;                       -- SpaceWire 0 data+
        spw0_din_n      : in  std_logic;                       -- SpaceWire 0 data-
        spw0_sin_p      : in  std_logic;                       -- SpaceWire 0 strobe+
        spw0_sin_n      : in  std_logic;                       -- SpaceWire 0 strobe-
        spw1_dout_p     : out std_logic;                       -- SpaceWire 1 data+
        spw1_dout_n     : out std_logic;                       -- SpaceWire 1 data-
        spw1_sout_p     : out std_logic;                       -- SpaceWire 1 strobe+
        spw1_sout_n     : out std_logic;                       -- SpaceWire 1 strobe-
        spw1_din_p      : in  std_logic;                       -- SpaceWire 1 data+
        spw1_din_n      : in  std_logic;                       -- SpaceWire 1 data-
        spw1_sin_p      : in  std_logic;                       -- SpaceWire 1 strobe+
        spw1_sin_n      : in  std_logic;                       -- SpaceWire 1 strobe-
        
        -- SPI Interface (to Clock Synthesizer LMX2615-SP)
        spi_lmk_mosi    : out std_logic;                       -- SPI MOSI
        spi_lmk_miso    : in  std_logic;                       -- SPI MISO
        spi_lmk_sclk    : out std_logic;                       -- SPI clock
        spi_lmk_cs_n    : out std_logic;                       -- SPI chip select
        
        -- SPI Interface (to Power Sequencer TPS7H3014-SP)
        spi_pwr_mosi    : out std_logic;                       -- SPI MOSI
        spi_pwr_miso    : in  std_logic;                       -- SPI MISO
        spi_pwr_sclk    : out std_logic;                       -- SPI clock
        spi_pwr_cs_n    : out std_logic;                       -- SPI chip select
        
        -- I2C Interface (to Temperature Sensors)
        i2c_scl         : out std_logic;                       -- I2C clock
        i2c_sda         : inout std_logic;                     -- I2C data
        
        -- GPIO
        gpio            : inout std_logic_vector(7 downto 0);  -- General purpose I/O
        
        -- Debug UART
        uart_tx         : out std_logic;                       -- UART TX
        uart_rx         : in  std_logic;                       -- UART RX
        
        -- Status LEDs
        led_power       : out std_logic;                       -- Power good LED
        led_fpga_done   : out std_logic;                       -- FPGA done LED
        led_error       : out std_logic;                       -- Error LED
        led_heartbeat   : out std_logic                        -- Heartbeat LED
    );
end entity top_module;

architecture rtl of top_module is

    -- =========================================================================
    -- Component Declarations
    -- =========================================================================
    
    -- JESD204C Receiver
    component jesd204c_receiver is
        generic (
            NUM_LANES   : integer := 16;
            DATA_WIDTH  : integer := 32
        );
        port (
            clk         : in  std_logic;
            rst_n       : in  std_logic;
            -- Physical
            refclk_p    : in  std_logic;
            refclk_n    : in  std_logic;
            rx_p        : in  std_logic_vector(NUM_LANES-1 downto 0);
            rx_n        : in  std_logic_vector(NUM_LANES-1 downto 0);
            sync_n      : out std_logic;
            sysref      : in  std_logic;
            -- Data output
            data_out    : out std_logic_vector(DATA_WIDTH-1 downto 0);
            data_valid  : out std_logic;
            -- Status
            status      : out std_logic_vector(31 downto 0)
        );
    end component jesd204c_receiver;
    
    -- DDC Chain
    component ddc_chain is
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
            -- Output
            i_out       : out std_logic_vector(NUM_CHANNELS*DATA_WIDTH-1 downto 0);
            q_out       : out std_logic_vector(NUM_CHANNELS*DATA_WIDTH-1 downto 0);
            out_valid   : out std_logic;
            -- Control
            nco_freq    : in  std_logic_vector(NUM_CHANNELS*NCO_WIDTH-1 downto 0);
            nco_phase   : in  std_logic_vector(NUM_CHANNELS*16-1 downto 0);
            gain        : in  std_logic_vector(NUM_CHANNELS*4-1 downto 0);
            decimation  : in  std_logic_vector(NUM_CHANNELS*4-1 downto 0)
        );
    end component ddc_chain;
    
    -- FIFO Buffer
    component fifo_buffer is
        generic (
            DATA_WIDTH  : integer := 32;
            DEPTH       : integer := 4096
        );
        port (
            wr_clk      : in  std_logic;
            rd_clk      : in  std_logic;
            rst_n       : in  std_logic;
            -- Write port
            wr_data     : in  std_logic_vector(DATA_WIDTH-1 downto 0);
            wr_en       : in  std_logic;
            -- Read port
            rd_data     : out std_logic_vector(DATA_WIDTH-1 downto 0);
            rd_en       : in  std_logic;
            -- Status
            full        : out std_logic;
            empty       : out std_logic;
            level       : out std_logic_vector(15 downto 0)
        );
    end component fifo_buffer;
    
    -- Error Handler
    component error_handler is
        port (
            clk         : in  std_logic;
            rst_n       : in  std_logic;
            -- Error inputs
            adc_error   : in  std_logic_vector(7 downto 0);
            clk_error   : in  std_logic_vector(7 downto 0);
            pwr_error   : in  std_logic_vector(7 downto 0);
            temp_alarm  : in  std_logic;
            -- Error outputs
            error_flag  : out std_logic_vector(15 downto 0);
            irq         : out std_logic
        );
    end component error_handler;
    
    -- Clock Manager
    component clock_manager is
        port (
            clk         : in  std_logic;
            rst_n       : in  std_logic;
            -- SPI to LMK04832-SP
            spi_mosi    : out std_logic;
            spi_miso    : in  std_logic;
            spi_sclk    : out std_logic;
            spi_cs_n    : out std_logic;
            -- Status
            pll_locked  : out std_logic;
            sysref_out  : out std_logic
        );
    end component clock_manager;
    
    -- SpaceWire Interface
    component spacewire_interface is
        generic (
            NUM_LINKS   : integer := 2
        );
        port (
            clk         : in  std_logic;
            rst_n       : in  std_logic;
            -- SpaceWire physical
            spw_dout_p  : out std_logic_vector(NUM_LINKS-1 downto 0);
            spw_dout_n  : out std_logic_vector(NUM_LINKS-1 downto 0);
            spw_sout_p  : out std_logic_vector(NUM_LINKS-1 downto 0);
            spw_sout_n  : out std_logic_vector(NUM_LINKS-1 downto 0);
            spw_din_p   : in  std_logic_vector(NUM_LINKS-1 downto 0);
            spw_din_n   : in  std_logic_vector(NUM_LINKS-1 downto 0);
            spw_sin_p   : in  std_logic_vector(NUM_LINKS-1 downto 0);
            spw_sin_n   : in  std_logic_vector(NUM_LINKS-1 downto 0);
            -- Data interface
            tx_data     : in  std_logic_vector(NUM_LINKS*8-1 downto 0);
            tx_valid    : in  std_logic_vector(NUM_LINKS-1 downto 0);
            tx_ready    : out std_logic_vector(NUM_LINKS-1 downto 0);
            rx_data     : out std_logic_vector(NUM_LINKS*8-1 downto 0);
            rx_valid    : out std_logic_vector(NUM_LINKS-1 downto 0);
            -- Status
            link_run    : out std_logic_vector(NUM_LINKS-1 downto 0);
            link_error  : out std_logic_vector(NUM_LINKS-1 downto 0)
        );
    end component spacewire_interface;
    
    -- AXI4-Lite Slave (Register Interface)
    component axi4_lite_slave is
        port (
            clk         : in  std_logic;
            rst_n       : in  std_logic;
            -- AXI4-Lite interface
            s_axi_awaddr  : in  std_logic_vector(11 downto 0);
            s_axi_awvalid : in  std_logic;
            s_axi_awready : out std_logic;
            s_axi_wdata   : in  std_logic_vector(31 downto 0);
            s_axi_wstrb   : in  std_logic_vector(3 downto 0);
            s_axi_wvalid  : in  std_logic;
            s_axi_wready  : out std_logic;
            s_axi_bresp   : out std_logic_vector(1 downto 0);
            s_axi_bvalid  : out std_logic;
            s_axi_bready  : in  std_logic;
            s_axi_araddr  : in  std_logic_vector(11 downto 0);
            s_axi_arvalid : in  std_logic;
            s_axi_arready : out std_logic;
            s_axi_rdata   : out std_logic_vector(31 downto 0);
            s_axi_rresp   : out std_logic_vector(1 downto 0);
            s_axi_rvalid  : out std_logic;
            s_axi_rready  : in  std_logic;
            -- Register interface
            reg_addr      : out std_logic_vector(11 downto 0);
            reg_wdata     : out std_logic_vector(31 downto 0);
            reg_rdata     : in  std_logic_vector(31 downto 0);
            reg_we        : out std_logic;
            reg_re        : out std_logic
        );
    end component axi4_lite_slave;

    -- =========================================================================
    -- Signal Declarations
    -- =========================================================================
    
    -- Internal reset
    signal rst_n_i         : std_logic;
    signal rst_i           : std_logic;
    
    -- JESD204C signals
    signal jesd_data       : std_logic_vector(31 downto 0);
    signal jesd_valid      : std_logic;
    signal jesd_status     : std_logic_vector(31 downto 0);
    
    -- DDC signals
    signal ddc_i_data      : std_logic_vector(NUM_DDC_CHANNELS*DATA_WIDTH-1 downto 0);
    signal ddc_q_data      : std_logic_vector(NUM_DDC_CHANNELS*DATA_WIDTH-1 downto 0);
    signal ddc_valid       : std_logic;
    
    -- FIFO signals
    signal fifo_wr_data    : std_logic_vector(31 downto 0);
    signal fifo_wr_en      : std_logic;
    signal fifo_rd_data    : std_logic_vector(31 downto 0);
    signal fifo_rd_en      : std_logic;
    signal fifo_full       : std_logic;
    signal fifo_empty      : std_logic;
    signal fifo_level      : std_logic_vector(15 downto 0);
    
    -- Error signals
    signal error_flag      : std_logic_vector(15 downto 0);
    signal irq_out         : std_logic;
    
    -- Clock signals
    signal pll_locked      : std_logic;
    signal sysref_out      : std_logic;
    
    -- SpaceWire signals
    signal spw_tx_data     : std_logic_vector(NUM_SPW_LINKS*8-1 downto 0);
    signal spw_tx_valid    : std_logic_vector(NUM_SPW_LINKS-1 downto 0);
    signal spw_tx_ready    : std_logic_vector(NUM_SPW_LINKS-1 downto 0);
    signal spw_rx_data     : std_logic_vector(NUM_SPW_LINKS*8-1 downto 0);
    signal spw_rx_valid    : std_logic_vector(NUM_SPW_LINKS-1 downto 0);
    signal spw_link_run    : std_logic_vector(NUM_SPW_LINKS-1 downto 0);
    signal spw_link_error  : std_logic_vector(NUM_SPW_LINKS-1 downto 0);
    
    -- Register interface signals
    signal reg_addr        : std_logic_vector(11 downto 0);
    signal reg_wdata       : std_logic_vector(31 downto 0);
    signal reg_rdata       : std_logic_vector(31 downto 0);
    signal reg_we          : std_logic;
    signal reg_re          : std_logic;
    
    -- Register file
    type reg_file_t is array (0 to 4095) of std_logic_vector(31 downto 0);
    signal reg_file        : reg_file_t := (others => (others => '0'));
    
    -- Heartbeat counter
    signal heartbeat_cnt   : unsigned(23 downto 0) := (others => '0');
    
    -- LED blink counter
    signal led_cnt         : unsigned(23 downto 0) := (others => '0');

begin

    -- =========================================================================
    -- Reset Generation
    -- =========================================================================
    rst_n_i <= sys_rst_n;
    rst_i <= not sys_rst_n;

    -- =========================================================================
    -- JESD204C Receiver Instance
    -- =========================================================================
    u_jesd204c_receiver : jesd204c_receiver
        generic map (
            NUM_LANES   => NUM_JESD_LANES,
            DATA_WIDTH  => 32
        )
        port map (
            clk         => sys_clk,
            rst_n       => rst_n_i,
            refclk_p    => jesd_refclk_p,
            refclk_n    => jesd_refclk_n,
            rx_p        => jesd_tx_p,
            rx_n        => jesd_tx_n,
            sync_n      => jesd_sync_n,
            sysref      => jesd_sysref,
            data_out    => jesd_data,
            data_valid  => jesd_valid,
            status      => jesd_status
        );

    -- =========================================================================
    -- DDC Chain Instance
    -- =========================================================================
    u_ddc_chain : ddc_chain
        generic map (
            NUM_CHANNELS => NUM_DDC_CHANNELS,
            DATA_WIDTH   => DATA_WIDTH,
            NCO_WIDTH    => NCO_WIDTH
        )
        port map (
            clk         => sys_clk,
            rst_n       => rst_n_i,
            data_in     => jesd_data(DATA_WIDTH-1 downto 0),
            data_valid  => jesd_valid,
            i_out       => ddc_i_data,
            q_out       => ddc_q_data,
            out_valid   => ddc_valid,
            nco_freq    => reg_file(128)(NUM_DDC_CHANNELS*NCO_WIDTH-1 downto 0),
            nco_phase   => reg_file(132)(NUM_DDC_CHANNELS*16-1 downto 0),
            gain        => reg_file(133)(NUM_DDC_CHANNELS*4-1 downto 0),
            decimation  => reg_file(134)(NUM_DDC_CHANNELS*4-1 downto 0)
        );

    -- =========================================================================
    -- FIFO Buffer Instance
    -- =========================================================================
    u_fifo_buffer : fifo_buffer
        generic map (
            DATA_WIDTH  => 32,
            DEPTH       => 4096
        )
        port map (
            wr_clk      => sys_clk,
            rd_clk      => sys_clk,
            rst_n       => rst_n_i,
            wr_data     => fifo_wr_data,
            wr_en       => fifo_wr_en,
            rd_data     => fifo_rd_data,
            rd_en       => fifo_rd_en,
            full        => fifo_full,
            empty       => fifo_empty,
            level       => fifo_level
        );

    -- =========================================================================
    -- Error Handler Instance
    -- =========================================================================
    u_error_handler : error_handler
        port map (
            clk         => sys_clk,
            rst_n       => rst_n_i,
            adc_error   => jesd_status(15 downto 8),
            clk_error   => reg_file(0x0140/4)(15 downto 8),
            pwr_error   => reg_file(0x00C0/4)(7 downto 0),
            temp_alarm  => reg_file(0x0080/4)(7),
            error_flag  => error_flag,
            irq         => irq_out
        );

    -- =========================================================================
    -- Clock Manager Instance
    -- =========================================================================
    u_clock_manager : clock_manager
        port map (
            clk         => sys_clk,
            rst_n       => rst_n_i,
            spi_mosi    => spi_lmk_mosi,
            spi_miso    => spi_lmk_miso,
            spi_sclk    => spi_lmk_sclk,
            spi_cs_n    => spi_lmk_cs_n,
            pll_locked  => pll_locked,
            sysref_out  => sysref_out
        );

    -- =========================================================================
    -- SpaceWire Interface Instance
    -- =========================================================================
    u_spacewire : spacewire_interface
        generic map (
            NUM_LINKS   => NUM_SPW_LINKS
        )
        port map (
            clk         => sys_clk,
            rst_n       => rst_n_i,
            spw_dout_p(0) => spw0_dout_p,
            spw_dout_p(1) => spw1_dout_p,
            spw_dout_n(0) => spw0_dout_n,
            spw_dout_n(1) => spw1_dout_n,
            spw_sout_p(0) => spw0_sout_p,
            spw_sout_p(1) => spw1_sout_p,
            spw_sout_n(0) => spw0_sout_n,
            spw_sout_n(1) => spw1_sout_n,
            spw_din_p(0)  => spw0_din_p,
            spw_din_p(1)  => spw1_din_p,
            spw_din_n(0)  => spw0_din_n,
            spw_din_n(1)  => spw1_din_n,
            spw_sin_p(0)  => spw0_sin_p,
            spw_sin_p(1)  => spw1_sin_p,
            spw_sin_n(0)  => spw0_sin_n,
            spw_sin_n(1)  => spw1_sin_n,
            tx_data     => spw_tx_data,
            tx_valid    => spw_tx_valid,
            tx_ready    => spw_tx_ready,
            rx_data     => spw_rx_data,
            rx_valid    => spw_rx_valid,
            link_run    => spw_link_run,
            link_error  => spw_link_error
        );

    -- =========================================================================
    -- AXI4-Lite Slave Instance
    -- =========================================================================
    u_axi_slave : axi4_lite_slave
        port map (
            clk         => sys_clk,
            rst_n       => rst_n_i,
            s_axi_awaddr  => (others => '0'),
            s_axi_awvalid => '0',
            s_axi_awready => open,
            s_axi_wdata   => (others => '0'),
            s_axi_wstrb   => (others => '0'),
            s_axi_wvalid  => '0',
            s_axi_wready  => open,
            s_axi_bresp   => open,
            s_axi_bvalid  => open,
            s_axi_bready  => '1',
            s_axi_araddr  => (others => '0'),
            s_axi_arvalid => '0',
            s_axi_arready => open,
            s_axi_rdata   => open,
            s_axi_rresp   => open,
            s_axi_rvalid  => open,
            s_axi_rready  => '1',
            reg_addr      => reg_addr,
            reg_wdata     => reg_wdata,
            reg_rdata     => reg_rdata,
            reg_we        => reg_we,
            reg_re        => reg_re
        );

    -- =========================================================================
    -- Register File Write Process
    -- =========================================================================
    process(sys_clk, rst_n_i)
    begin
        if rst_n_i = '0' then
            -- Reset all registers to default values
            for i in 0 to 4095 loop
                reg_file(i) <= (others => '0');
            end loop;
        elsif rising_edge(sys_clk) then
            if reg_we = '1' then
                reg_file(to_integer(unsigned(reg_addr(11 downto 2)))) <= reg_wdata;
            end if;
        end if;
    end process;

    -- =========================================================================
    -- Register File Read Process
    -- =========================================================================
    process(reg_addr, reg_file, jesd_status, fifo_level, error_flag, 
            pll_locked, spw_link_run, spw_link_error, fifo_rd_data)
    begin
        -- Default: read from register file
        reg_rdata <= reg_file(to_integer(unsigned(reg_addr(11 downto 2))));
        
        -- Override for read-only status registers
        case reg_addr(11 downto 0) is
            when x"0000" =>  -- SYS_STATUS
                reg_rdata <= x"01" & x"00" & error_flag(7 downto 0) & x"00";
            when x"000C" =>  -- SYS_IRQ_STATUS
                reg_rdata <= x"0000" & "000" & irq_out & "000000000";
            when x"0044" =>  -- ADC_STATUS
                reg_rdata <= jesd_status;
            when x"00C0" =>  -- POWER_STATUS
                reg_rdata <= x"F0000000";  -- All rails OK
            when x"0100" =>  -- CLOCK_STATUS
                reg_rdata <= std_logic_vector(to_unsigned(0, 32));
                reg_rdata(31) <= pll_locked;
            when x"0300" =>  -- SPW_STATUS
                reg_rdata <= x"00000000";
                reg_rdata(31 downto 30) <= spw_link_run;
                reg_rdata(29 downto 28) <= spw_link_error;
            when x"0400" =>  -- BUFFER_STATUS
                reg_rdata <= x"00000000";
                reg_rdata(31 downto 16) <= fifo_level;
                reg_rdata(15 downto 8) <= fifo_level(7 downto 0);  -- simplified
            when others =>
                null;
        end case;
    end process;

    -- =========================================================================
    -- Heartbeat Generator
    -- =========================================================================
    process(sys_clk, rst_n_i)
    begin
        if rst_n_i = '0' then
            heartbeat_cnt <= (others => '0');
        elsif rising_edge(sys_clk) then
            heartbeat_cnt <= heartbeat_cnt + 1;
        end if;
    end process;

    -- =========================================================================
    -- LED Outputs
    -- =========================================================================
    led_power     <= '1' when pll_locked = '1' else '0';
    led_fpga_done <= '1';  -- FPGA configuration done
    led_error     <= '0' when error_flag = x"0000" else '1';
    led_heartbeat <= heartbeat_cnt(23);  -- ~0.14 Hz blink at 100 MHz

    -- =========================================================================
    -- Data Path to FIFO
    -- =========================================================================
    fifo_wr_data <= ddc_i_data(31 downto 0);  -- Simplified: take first channel I data
    fifo_wr_en   <= ddc_valid;

    -- =========================================================================
    -- SpaceWire Data Input (from FIFO)
    -- =========================================================================
    spw_tx_data  <= fifo_rd_data & fifo_rd_data(31 downto 8);  -- Simplified
    spw_tx_valid <= (others => not fifo_empty);
    fifo_rd_en   <= spw_tx_ready(0) and not fifo_empty;

end architecture rtl;
