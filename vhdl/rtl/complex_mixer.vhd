-- XBandDigitalModule_20x20 - Complex Mixer
-- File: complex_mixer.vhd
-- Description: I/Q complex mixer: (I_in + j*Q_in) * (cos + j*sin)
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity complex_mixer is
    generic (
        DATA_WIDTH  : integer := 16;
        NCO_WIDTH   : integer := 16
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        -- Input (complex)
        i_in        : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        q_in        : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        in_valid    : in  std_logic;
        -- NCO input (complex)
        cos_in      : in  std_logic_vector(NCO_WIDTH-1 downto 0);
        sin_in      : in  std_logic_vector(NCO_WIDTH-1 downto 0);
        -- Output (complex)
        i_out       : out std_logic_vector(DATA_WIDTH-1 downto 0);
        q_out       : out std_logic_vector(DATA_WIDTH-1 downto 0);
        out_valid   : out std_logic
    );
end entity complex_mixer;

architecture rtl of complex_mixer is

    -- Multiplication result width
    constant PROD_WIDTH : integer := DATA_WIDTH + NCO_WIDTH;

    -- Pipeline registers
    signal i_in_r       : signed(DATA_WIDTH-1 downto 0) := (others => '0');
    signal q_in_r       : signed(DATA_WIDTH-1 downto 0) := (others => '0');
    signal cos_r        : signed(NCO_WIDTH-1 downto 0) := (others => '0');
    signal sin_r        : signed(NCO_WIDTH-1 downto 0) := (others => '0');

    -- Multiply results (full width)
    signal i_cos        : signed(PROD_WIDTH-1 downto 0) := (others => '0');
    signal q_sin        : signed(PROD_WIDTH-1 downto 0) := (others => '0');
    signal i_sin        : signed(PROD_WIDTH-1 downto 0) := (others => '0');
    signal q_cos        : signed(PROD_WIDTH-1 downto 0) := (others => '0');

    -- Output accumulator
    signal i_sum        : signed(PROD_WIDTH-1 downto 0) := (others => '0');
    signal q_diff       : signed(PROD_WIDTH-1 downto 0) := (others => '0');

begin

    -- Input register stage
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            i_in_r <= (others => '0');
            q_in_r <= (others => '0');
            cos_r <= (others => '0');
            sin_r <= (others => '0');
        elsif rising_edge(clk) then
            i_in_r <= signed(i_in);
            q_in_r <= signed(q_in);
            cos_r <= signed(cos_in);
            sin_r <= signed(sin_in);
        end if;
    end process;

    -- Multiply stage
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            i_cos <= (others => '0');
            q_sin <= (others => '0');
            i_sin <= (others => '0');
            q_cos <= (others => '0');
        elsif rising_edge(clk) then
            i_cos <= i_in_r * cos_r;
            q_sin <= q_in_r * sin_r;
            i_sin <= i_in_r * sin_r;
            q_cos <= q_in_r * cos_r;
        end if;
    end process;

    -- Accumulate stage: I_out = I*cos - Q*sin, Q_out = I*sin + Q*cos
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            i_sum <= (others => '0');
            q_diff <= (others => '0');
        elsif rising_edge(clk) then
            i_sum <= i_cos - q_sin;
            q_diff <= i_sin + q_cos;
        end if;
    end process;

    -- Output (take MSBs for rounding)
    i_out <= std_logic_vector(i_sum(PROD_WIDTH-2 downto PROD_WIDTH-DATA_WIDTH-1));
    q_out <= std_logic_vector(q_diff(PROD_WIDTH-2 downto PROD_WIDTH-DATA_WIDTH-1));

    -- Valid pipeline (3 stages)
    process(clk, rst_n)
        variable v : unsigned(2 downto 0) := (others => '0');
    begin
        if rst_n = '0' then
            v := (others => '0');
            out_valid <= '0';
        elsif rising_edge(clk) then
            v := v(1 downto 0) & in_valid;
            out_valid <= v(2);
        end if;
    end process;

end architecture rtl;
