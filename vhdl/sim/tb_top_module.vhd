-- XBandDigitalModule_20x20 - Top Module Testbench
-- File: tb_top_module.vhd
-- Description: Testbench for top_module verification
-- Author: Verification Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_top_module is
end entity tb_top_module;

architecture sim of tb_top_module is

    -- Constants
    constant CLK_PERIOD : time := 10 ns;  -- 100 MHz
    
    -- Component declaration
    component top_module is
        generic (
            CLK_FREQ        : integer := 100_000_000;
            NUM_JESD_LANES  : integer := 16;
            NUM_DDC_CHANNELS: integer := 8;
            NUM_SPW_LINKS   : integer := 2;
            DATA_WIDTH      : integer := 16;
            NCO_WIDTH       : integer := 48
        );
        port (
            sys_clk         : in  std_logic;
            sys_rst_n       : in  std_logic;
            jesd_refclk_p   : in  std_logic;
            jesd_refclk_n   : in  std_logic;
            jesd_tx_p       : in  std_logic_vector(NUM_JESD_LANES-1 downto 0);
            jesd_tx_n       : in  std_logic_vector(NUM_JESD_LANES-1 downto 0);
            jesd_rx_p       : out std_logic_vector(NUM_JESD_LANES-1 downto 0);
            jesd_rx_n       : out std_logic_vector(NUM_JESD_LANES-1 downto 0);
            jesd_sync_n     : out std_logic;
            jesd_sysref     : in  std_logic;
            spw0_dout_p     : out std_logic;
            spw0_dout_n     : out std_logic;
            spw0_sout_p     : out std_logic;
            spw0_sout_n     : out std_logic;
            spw0_din_p      : in  std_logic;
            spw0_din_n      : in  std_logic;
            spw0_sin_p      : in  std_logic;
            spw0_sin_n      : in  std_logic;
            spw1_dout_p     : out std_logic;
            spw1_dout_n     : out std_logic;
            spw1_sout_p     : out std_logic;
            spw1_sout_n     : out std_logic;
            spw1_din_p      : in  std_logic;
            spw1_din_n      : in  std_logic;
            spw1_sin_p      : in  std_logic;
            spw1_sin_n      : in  std_logic;
            spi_lmk_mosi    : out std_logic;
            spi_lmk_miso    : in  std_logic;
            spi_lmk_sclk    : out std_logic;
            spi_lmk_cs_n    : out std_logic;
            spi_pwr_mosi    : out std_logic;
            spi_pwr_miso    : in  std_logic;
            spi_pwr_sclk    : out std_logic;
            spi_pwr_cs_n    : out std_logic;
            i2c_scl         : out std_logic;
            i2c_sda         : inout std_logic;
            gpio            : inout std_logic_vector(7 downto 0);
            uart_tx         : out std_logic;
            uart_rx         : in  std_logic;
            led_power       : out std_logic;
            led_fpga_done   : out std_logic;
            led_error       : out std_logic;
            led_heartbeat   : out std_logic
        );
    end component top_module;

    -- Signals
    signal sys_clk         : std_logic := '0';
    signal sys_rst_n       : std_logic := '0';
    signal jesd_refclk_p   : std_logic := '0';
    signal jesd_refclk_n   : std_logic := '1';
    signal jesd_tx_p       : std_logic_vector(15 downto 0) := (others => '0');
    signal jesd_tx_n       : std_logic_vector(15 downto 0) := (others => '1');
    signal jesd_rx_p       : std_logic_vector(15 downto 0);
    signal jesd_rx_n       : std_logic_vector(15 downto 0);
    signal jesd_sync_n     : std_logic;
    signal jesd_sysref     : std_logic := '0';
    signal spw0_dout_p     : std_logic;
    signal spw0_dout_n     : std_logic;
    signal spw0_sout_p     : std_logic;
    signal spw0_sout_n     : std_logic;
    signal spw0_din_p      : std_logic := '0';
    signal spw0_din_n      : std_logic := '1';
    signal spw0_sin_p      : std_logic := '0';
    signal spw0_sin_n      : std_logic := '1';
    signal spw1_dout_p     : std_logic;
    signal spw1_dout_n     : std_logic;
    signal spw1_sout_p     : std_logic;
    signal spw1_sout_n     : std_logic;
    signal spw1_din_p      : std_logic := '0';
    signal spw1_din_n      : std_logic := '1';
    signal spw1_sin_p      : std_logic := '0';
    signal spw1_sin_n      : std_logic := '1';
    signal spi_lmk_mosi    : std_logic;
    signal spi_lmk_miso    : std_logic := '0';
    signal spi_lmk_sclk    : std_logic;
    signal spi_lmk_cs_n    : std_logic;
    signal spi_pwr_mosi    : std_logic;
    signal spi_pwr_miso    : std_logic := '0';
    signal spi_pwr_sclk    : std_logic;
    signal spi_pwr_cs_n    : std_logic;
    signal i2c_scl         : std_logic;
    signal i2c_sda         : std_logic := 'Z';
    signal gpio            : std_logic_vector(7 downto 0) := (others => 'Z');
    signal uart_tx         : std_logic;
    signal uart_rx         : std_logic := '0';
    signal led_power       : std_logic;
    signal led_fpga_done   : std_logic;
    signal led_error       : std_logic;
    signal led_heartbeat   : std_logic;

begin

    -- Clock generation
    sys_clk <= not sys_clk after CLK_PERIOD / 2;
    jesd_refclk_p <= not jesd_refclk_p after 0.048 ns;  -- ~10.4 GHz
    jesd_refclk_n <= not jesd_refclk_n after 0.048 ns;

    -- DUT instantiation
    u_dut : top_module
        port map (
            sys_clk         => sys_clk,
            sys_rst_n       => sys_rst_n,
            jesd_refclk_p   => jesd_refclk_p,
            jesd_refclk_n   => jesd_refclk_n,
            jesd_tx_p       => jesd_tx_p,
            jesd_tx_n       => jesd_tx_n,
            jesd_rx_p       => jesd_rx_p,
            jesd_rx_n       => jesd_rx_n,
            jesd_sync_n     => jesd_sync_n,
            jesd_sysref     => jesd_sysref,
            spw0_dout_p     => spw0_dout_p,
            spw0_dout_n     => spw0_dout_n,
            spw0_sout_p     => spw0_sout_p,
            spw0_sout_n     => spw0_sout_n,
            spw0_din_p      => spw0_din_p,
            spw0_din_n      => spw0_din_n,
            spw0_sin_p      => spw0_sin_p,
            spw0_sin_n      => spw0_sin_n,
            spw1_dout_p     => spw1_dout_p,
            spw1_dout_n     => spw1_dout_n,
            spw1_sout_p     => spw1_sout_p,
            spw1_sout_n     => spw1_sout_n,
            spw1_din_p      => spw1_din_p,
            spw1_din_n      => spw1_din_n,
            spw1_sin_p      => spw1_sin_p,
            spw1_sin_n      => spw1_sin_n,
            spi_lmk_mosi    => spi_lmk_mosi,
            spi_lmk_miso    => spi_lmk_miso,
            spi_lmk_sclk    => spi_lmk_sclk,
            spi_lmk_cs_n    => spi_lmk_cs_n,
            spi_pwr_mosi    => spi_pwr_mosi,
            spi_pwr_miso    => spi_pwr_miso,
            spi_pwr_sclk    => spi_pwr_sclk,
            spi_pwr_cs_n    => spi_pwr_cs_n,
            i2c_scl         => i2c_scl,
            i2c_sda         => i2c_sda,
            gpio            => gpio,
            uart_tx         => uart_tx,
            uart_rx         => uart_rx,
            led_power       => led_power,
            led_fpga_done   => led_fpga_done,
            led_error       => led_error,
            led_heartbeat   => led_heartbeat
        );

    -- Stimulus process
    stim_proc : process
    begin
        -- Reset
        sys_rst_n <= '0';
        wait for 100 ns;
        sys_rst_n <= '1';
        wait for 1 us;
        
        -- Wait for initialization
        wait for 10 ms;
        
        -- Check LEDs
        assert led_power = '1' report "Power LED should be ON" severity error;
        
        -- End simulation
        wait for 1 ms;
        report "Simulation completed successfully" severity note;
        wait;
    end process stim_proc;

end architecture sim;
