-- XBandDigitalModule_20x20 - Clock Domain Crossing
-- File: cdc_sync.vhd
-- Description: 2-FF clock domain crossing synchronizer
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity cdc_sync is
    generic (
        WIDTH : integer := 1
    );
    port (
        clk_dst : in  std_logic;
        rst_n   : in  std_logic;
        data_in : in  std_logic_vector(WIDTH-1 downto 0);
        data_out: out std_logic_vector(WIDTH-1 downto 0)
    );
end entity cdc_sync;

architecture rtl of cdc_sync is
    signal ff1 : std_logic_vector(WIDTH-1 downto 0) := (others => '0');
    signal ff2 : std_logic_vector(WIDTH-1 downto 0) := (others => '0');
begin
    process(clk_dst, rst_n)
    begin
        if rst_n = '0' then
            ff1 <= (others => '0');
            ff2 <= (others => '0');
        elsif rising_edge(clk_dst) then
            ff1 <= data_in;
            ff2 <= ff1;
        end if;
    end process;
    data_out <= ff2;
end architecture rtl;
