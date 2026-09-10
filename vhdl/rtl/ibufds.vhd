-- XBandDigitalModule_20x20 - Differential Input Buffer
-- File: ibufds.vhd
-- Description: Differential to single-ended input buffer (Vivilog primitive wrapper)
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity ibufds is
    port (
        I  : in  std_logic;
        IB : in  std_logic;
        O  : out std_logic
    );
end entity ibufds;

architecture rtl of ibufds is
begin
    O <= '1' when (I = '1' and IB = '0') else
         '0' when (I = '0' and IB = '1') else
         '0';
end architecture rtl;
