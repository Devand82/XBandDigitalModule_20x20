-- XBandDigitalModule_20x20 - Clock Manager
-- File: clock_manager.vhd
-- Description: Clock configuration via SPI for LMK04832-SP and LMX2615-SP
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity clock_manager is
    port (
        clk             : in  std_logic;
        rst_n           : in  std_logic;
        -- SPI to LMK04832-SP
        spi_mosi        : out std_logic;
        spi_miso        : in  std_logic;
        spi_sclk        : out std_logic;
        spi_cs_n        : out std_logic;
        -- Status
        pll_locked      : out std_logic;
        sysref_out      : out std_logic
    );
end entity clock_manager;

architecture rtl of clock_manager is
    type spi_state_t is (IDLE, CS_LOW, SHIFT, CS_HIGH, WAIT_LOCK);
    signal state       : spi_state_t := IDLE;
    signal shift_reg   : std_logic_vector(31 downto 0) := (others => '0');
    signal bit_cnt     : unsigned(4 downto 0) := (others => '0');
    signal clk_div     : unsigned(3 downto 0) := (others => '0');
    signal spi_clk_i   : std_logic := '0';
    signal cs_n_i      : std_logic := '1';
    signal locked_i    : std_logic := '0';
    signal init_done   : std_logic := '0';
    signal init_cnt    : unsigned(7 downto 0) := (others => '0');
    type init_rom_t is array (0 to 15) of std_logic_vector(31 downto 0);
    constant INIT_ROM  : init_rom_t := (
        x"00000001",  -- RESET
        x"00000002",  -- POWERDOWN
        x"00080000",  -- PLL1 config
        x"00080001",  -- PLL1 config
        x"00100001",  -- PLL2 config
        x"00100002",  -- PLL2 config
        x"00140000",  -- SYSREF config
        x"00180001",  -- OUTPUT0 enable
        x"001C0001",  -- OUTPUT1 enable
        x"00200001",  -- OUTPUT2 enable
        x"00240000",  -- reserved
        x"00280000",  -- reserved
        x"002C0000",  -- reserved
        x"00300000",  -- reserved
        x"00340000",  -- reserved
        x"00000000"   -- end
    );
begin
    spi_sclk <= spi_clk_i;
    spi_cs_n <= cs_n_i;
    pll_locked <= locked_i;
    sysref_out <= '0';
    spi_mosi <= shift_reg(31);

    process(clk, rst_n)
    begin
        if rst_n = '0' then
            state <= IDLE;
            shift_reg <= (others => '0');
            bit_cnt <= (others => '0');
            clk_div <= (others => '0');
            spi_clk_i <= '0';
            cs_n_i <= '1';
            locked_i <= '0';
            init_done <= '0';
            init_cnt <= (others => '0');
        elsif rising_edge(clk) then
            case state is
                when IDLE =>
                    cs_n_i <= '1';
                    if init_done = '0' then
                        shift_reg <= INIT_ROM(to_integer(init_cnt(3 downto 0)));
                        state <= CS_LOW;
                        bit_cnt <= (others => '0');
                    end if;
                when CS_LOW =>
                    cs_n_i <= '0';
                    state <= SHIFT;
                when SHIFT =>
                    clk_div <= clk_div + 1;
                    if clk_div = "0111" then
                        spi_clk_i <= not spi_clk_i;
                        if spi_clk_i = '1' then
                            shift_reg <= shift_reg(30 downto 0) & '0';
                            bit_cnt <= bit_cnt + 1;
                            if bit_cnt = "11111" then
                                state <= CS_HIGH;
                            end if;
                        end if;
                    end if;
                when CS_HIGH =>
                    cs_n_i <= '1';
                    if init_cnt = 15 then
                        init_done <= '1';
                        locked_i <= '1';
                        state <= IDLE;
                    else
                        init_cnt <= init_cnt + 1;
                        state <= IDLE;
                    end if;
                when WAIT_LOCK =>
                    null;
            end case;
        end if;
    end process;
end architecture rtl;
