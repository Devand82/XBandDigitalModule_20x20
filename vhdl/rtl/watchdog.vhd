-- XBandDigitalModule_20x20 - Watchdog Timer
-- File: watchdog.vhd
-- Description: Configurable watchdog timer with interrupt and reset generation
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity watchdog is
    generic (
        CLK_FREQ    : integer := 100_000_000;
        TIMEOUT_MS  : integer := 1000
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        -- Control
        enable      : in  std_logic;
        kick        : in  std_logic;    -- pulse to reload counter
        -- Status
        timeout     : out std_logic;    -- goes high on timeout
        irq         : out std_logic     -- interrupt pulse
    );
end entity watchdog;

architecture rtl of watchdog is
    constant MAX_COUNT : integer := (TIMEOUT_MS * CLK_FREQ / 1000) - 1;
    signal counter     : unsigned(31 downto 0) := (others => '0');
    signal timeout_i   : std_logic := '0';
    signal irq_i       : std_logic := '0';
begin
    timeout <= timeout_i;
    irq <= irq_i;

    process(clk, rst_n)
    begin
        if rst_n = '0' then
            counter <= (others => '0');
            timeout_i <= '0';
            irq_i <= '0';
        elsif rising_edge(clk) then
            irq_i <= '0';
            if enable = '0' then
                counter <= (others => '0');
                timeout_i <= '0';
            elsif kick = '1' then
                counter <= to_unsigned(MAX_COUNT, 32);
                timeout_i <= '0';
            elsif counter = 0 then
                timeout_i <= '1';
                irq_i <= '1';
            else
                counter <= counter - 1;
            end if;
        end if;
    end process;
end architecture rtl;
