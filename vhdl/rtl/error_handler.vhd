-- XBandDigitalModule_20x20 - Error Handler
-- File: error_handler.vhd
-- Description: Error detection, logging, and interrupt generation
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity error_handler is
    port (
        clk             : in  std_logic;
        rst_n           : in  std_logic;
        -- Error inputs
        adc_error       : in  std_logic_vector(7 downto 0);
        clk_error       : in  std_logic_vector(7 downto 0);
        pwr_error       : in  std_logic_vector(7 downto 0);
        temp_alarm      : in  std_logic;
        -- Error outputs
        error_flag      : out std_logic_vector(15 downto 0);
        irq             : out std_logic
    );
end entity error_handler;

architecture rtl of error_handler is
    signal error_flag_i : std_logic_vector(15 downto 0) := (others => '0');
    signal irq_i        : std_logic := '0';
    signal edge_detect  : std_logic_vector(15 downto 0) := (others => '0');
begin
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            error_flag_i <= (others => '0');
            irq_i <= '0';
            edge_detect <= (others => '0');
        elsif rising_edge(clk) then
            edge_detect <= error_flag_i;
            error_flag_i(7 downto 0) <= adc_error;
            error_flag_i(11 downto 8) <= clk_error(3 downto 0);
            error_flag_i(14 downto 12) <= pwr_error(2 downto 0);
            error_flag_i(15) <= temp_alarm;
            irq_i <= '0';
            for i in 0 to 15 loop
                if error_flag_i(i) = '1' and edge_detect(i) = '0' then
                    irq_i <= '1';
                end if;
            end loop;
        end if;
    end process;
    error_flag <= error_flag_i;
    irq <= irq_i;
end architecture rtl;
