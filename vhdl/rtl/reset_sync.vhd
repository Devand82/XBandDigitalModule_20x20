-- XBandDigitalModule_20x20 - Reset Synchronizer
-- File: reset_sync.vhd
-- Description: 2-stage reset synchronizer for metastability removal
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity reset_sync is
    port (
        clk      : in  std_logic;
        rst_n    : in  std_logic;
        rst_n_out: out std_logic
    );
end entity reset_sync;

architecture rtl of reset_sync is
    signal rst_ff1 : std_logic := '0';
    signal rst_ff2 : std_logic := '0';
begin
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            rst_ff1 <= '0';
            rst_ff2 <= '0';
        elsif rising_edge(clk) then
            rst_ff1 <= '1';
            rst_ff2 <= rst_ff1;
        end if;
    end process;
    rst_n_out <= rst_ff2;
end architecture rtl;
