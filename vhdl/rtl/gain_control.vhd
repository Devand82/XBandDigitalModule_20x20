-- XBandDigitalModule_20x20 - Gain Control
-- File: gain_control.vhd
-- Description: Programmable gain amplifier with 4-bit gain selection
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity gain_control is
    generic (
        DATA_WIDTH  : integer := 16;
        GAIN_WIDTH  : integer := 4
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        -- Input
        data_in     : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        in_valid    : in  std_logic;
        -- Gain setting
        gain        : in  std_logic_vector(GAIN_WIDTH-1 downto 0);
        -- Output
        data_out    : out std_logic_vector(DATA_WIDTH-1 downto 0);
        out_valid   : out std_logic
    );
end entity gain_control;

architecture rtl of gain_control is

    -- Gain LUT: 16 gain settings from 0dB to +45dB in ~3dB steps
    -- Gain values as Q1.15 multiplier (1.0 = 32768)
    type gain_lut_t is array (0 to 15) of signed(15 downto 0);
    constant GAIN_LUT : gain_lut_t := (
        to_signed( 3277,  16),  --  0: 0.1x   (-20dB)
        to_signed( 4634,  16),  --  1: 0.14x  (-17dB)
        to_signed( 6554,  16),  --  2: 0.2x   (-14dB)
        to_signed( 9261,  16),  --  3: 0.28x  (-11dB)
        to_signed( 13107, 16),  --  4: 0.4x   (-8dB)
        to_signed( 18530, 16),  --  5: 0.57x  (-5dB)
        to_signed( 26214, 16),  --  6: 0.8x   (-2dB)
        to_signed( 32768, 16),  --  7: 1.0x   ( 0dB)
        to_signed( 46341, 16),  --  8: 1.4x   (+3dB)
        to_signed( 65535, 16),  --  9: 2.0x   (+6dB)
        to_signed( 92682, 16),  -- 10: 2.8x   (+9dB)
        to_signed(131072, 16),  -- 11: 4.0x   (+12dB)
        to_signed(185302, 16),  -- 12: 5.7x   (+15dB)
        to_signed(262144, 16),  -- 13: 8.0x   (+18dB)
        to_signed(327680, 16),  -- 14: 10x    (+20dB)
        to_signed(463410, 16)   -- 15: 14x    (+23dB)
    );

    signal gain_val     : signed(15 downto 0) := to_signed(32768, 16);
    signal data_in_r    : signed(DATA_WIDTH-1 downto 0) := (others => '0');
    signal product      : signed(DATA_WIDTH+15 downto 0) := (others => '0');
    signal valid_pipe   : unsigned(1 downto 0) := (others => '0');

begin

    -- Gain LUT lookup
    gain_val <= GAIN_LUT(to_integer(unsigned(gain)));

    -- Input register
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            data_in_r <= (others => '0');
        elsif rising_edge(clk) then
            data_in_r <= signed(data_in);
        end if;
    end process;

    -- Multiply
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            product <= (others => '0');
        elsif rising_edge(clk) then
            product <= data_in_r * gain_val;
        end if;
    end process;

    -- Output (take upper bits, round to DATA_WIDTH)
    data_out <= std_logic_vector(product(DATA_WIDTH+13 downto 14));

    -- Valid pipeline
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            valid_pipe <= (others => '0');
            out_valid <= '0';
        elsif rising_edge(clk) then
            valid_pipe <= valid_pipe(0) & in_valid;
            out_valid <= valid_pipe(1);
        end if;
    end process;

end architecture rtl;
