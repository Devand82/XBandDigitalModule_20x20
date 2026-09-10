-- XBandDigitalModule_20x20 - CIC Decimator
-- File: cic_decimator.vhd
-- Description: CIC (Cascaded Integrator-Comb) decimation filter, N=5 stages
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity cic_decimator is
    generic (
        INPUT_WIDTH : integer := 16;
        OUTPUT_WIDTH: integer := 16;
        STAGES      : integer := 5;       -- CIC order (N)
        MAX_DECIM   : integer := 1024      -- Maximum decimation factor
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        -- Control
        decim_rate  : in  std_logic_vector(15 downto 0);  -- decimation factor R
        -- Input
        data_in     : in  std_logic_vector(INPUT_WIDTH-1 downto 0);
        in_valid    : in  std_logic;
        -- Output
        data_out    : out std_logic_vector(OUTPUT_WIDTH-1 downto 0);
        out_valid   : out std_logic
    );
end entity cic_decimator;

architecture rtl of cic_decimator is

    -- Internal width: INPUT_WIDTH + N * log2(MAX_DECIM)
    constant INTERNAL_WIDTH : integer := INPUT_WIDTH + STAGES * 16;

    -- Integrator stage outputs
    type integrator_t is array (0 to STAGES-1) of signed(INTERNAL_WIDTH-1 downto 0);
    signal integrators : integrator_t := (others => (others => '0'));

    -- Comb stage outputs
    type comb_t is array (0 to STAGES-1) of signed(INTERNAL_WIDTH-1 downto 0);
    signal combs       : comb_t := (others => (others => '0'));
    signal comb_prev   : comb_t := (others => (others => '0'));

    -- Decimation counter
    signal decim_cnt   : unsigned(15 downto 0) := (others => '0');
    signal decim_done  : std_logic := '0';

    -- Valid pipeline
    signal in_valid_d  : std_logic := '0';
    signal out_valid_i : std_logic := '0';

begin

    data_out <= std_logic_vector(combs(STAGES-1)(INTERNAL_WIDTH-1 downto INTERNAL_WIDTH-OUTPUT_WIDTH));
    out_valid <= out_valid_i;

    -- Integrator section (runs at input rate)
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            for i in 0 to STAGES-1 loop
                integrators(i) <= (others => '0');
            end loop;
        elsif rising_edge(clk) then
            if in_valid = '1' then
                integrators(0) <= integrators(0) + signed(data_in);
                for i in 1 to STAGES-1 loop
                    integrators(i) <= integrators(i) + integrators(i-1);
                end loop;
            end if;
        end if;
    end process;

    -- Decimation counter
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            decim_cnt <= (others => '0');
            decim_done <= '0';
        elsif rising_edge(clk) then
            decim_done <= '0';
            if in_valid = '1' then
                if decim_cnt = unsigned(decim_rate) - 1 then
                    decim_cnt <= (others => '0');
                    decim_done <= '1';
                else
                    decim_cnt <= decim_cnt + 1;
                end if;
            end if;
        end if;
    end process;

    -- Comb section (runs at decimated rate)
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            for i in 0 to STAGES-1 loop
                combs(i) <= (others => '0');
                comb_prev(i) <= (others => '0');
            end loop;
            out_valid_i <= '0';
        elsif rising_edge(clk) then
            out_valid_i <= '0';
            if decim_done = '1' then
                combs(0) <= integrators(STAGES-1) - comb_prev(0);
                comb_prev(0) <= integrators(STAGES-1);
                for i in 1 to STAGES-1 loop
                    combs(i) <= combs(i-1) - comb_prev(i);
                    comb_prev(i) <= combs(i-1);
                end loop;
                out_valid_i <= '1';
            end if;
        end if;
    end process;

end architecture rtl;
