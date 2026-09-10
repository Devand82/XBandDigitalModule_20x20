-- XBandDigitalModule_20x20 - FIR Compensation Filter
-- File: fir_compensation.vhd
-- Description: 21-tap symmetric FIR compensation filter for CIC droop correction
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity fir_compensation is
    generic (
        DATA_WIDTH  : integer := 16;
        COEFF_WIDTH : integer := 16;
        TAPS        : integer := 21
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        -- Input
        data_in     : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        in_valid    : in  std_logic;
        -- Output
        data_out    : out std_logic_vector(DATA_WIDTH-1 downto 0);
        out_valid   : out std_logic
    );
end entity fir_compensation;

architecture rtl of fir_compensation is

    -- Coefficients: 21-tap CIC compensation filter (pre-calculated)
    -- Symmetric: h[0]=h[20], h[1]=h[19], ..., h[9]=h[11], h[10]=center
    type coeff_array_t is array (0 to 10) of signed(COEFF_WIDTH-1 downto 0);
    constant COEFFS : coeff_array_t := (
        to_signed(-245,  COEFF_WIDTH),  -- h[0] = h[20]
        to_signed( 523,  COEFF_WIDTH),  -- h[1] = h[19]
        to_signed(-1204, COEFF_WIDTH),  -- h[2] = h[18]
        to_signed( 2456, COEFF_WIDTH),  -- h[3] = h[17]
        to_signed(-4891, COEFF_WIDTH),  -- h[4] = h[16]
        to_signed( 12453,COEFF_WIDTH),  -- h[5] = h[15]
        to_signed( 24567,COEFF_WIDTH),  -- h[6] = h[14]  (center region)
        to_signed(-4891, COEFF_WIDTH),  -- h[7] = h[13]
        to_signed( 2456, COEFF_WIDTH),  -- h[8] = h[12]
        to_signed(-1204, COEFF_WIDTH),  -- h[9] = h[11]
        to_signed( 32767,COEFF_WIDTH)   -- h[10] center tap (largest)
    );

    -- Shift register for input samples
    type shift_reg_t is array (0 to TAPS-1) of signed(DATA_WIDTH-1 downto 0);
    signal shift_reg : shift_reg_t := (others => (others => '0'));

    -- Product and accumulator
    signal accumulator : signed(DATA_WIDTH+COEFF_WIDTH+5 downto 0) := (others => '0');
    signal prod        : signed(DATA_WIDTH+COEFF_WIDTH-1 downto 0);

    -- Valid pipeline
    signal valid_pipe  : unsigned(4 downto 0) := (others => '0');

    -- MAC control
    signal mac_idx     : integer range 0 to 10 := 0;
    signal mac_running : std_logic := '0';

begin

    -- Shift register (input delay line)
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            for i in 0 to TAPS-1 loop
                shift_reg(i) <= (others => '0');
            end loop;
        elsif rising_edge(clk) then
            if in_valid = '1' then
                shift_reg(0) <= signed(data_in);
                for i in 1 to TAPS-1 loop
                    shift_reg(i) <= shift_reg(i-1);
                end loop;
            end if;
        end if;
    end process;

    -- MAC engine: computes symmetric FIR using 11 multiply-accumulate operations
    process(clk, rst_n)
        variable sym_sum : signed(DATA_WIDTH downto 0);
    begin
        if rst_n = '0' then
            accumulator <= (others => '0');
            mac_idx <= 0;
            mac_running <= '0';
            out_valid <= '0';
            data_out <= (others => '0');
        elsif rising_edge(clk) then
            out_valid <= '0';
            if in_valid = '1' and mac_running = '0' then
                mac_running <= '1';
                mac_idx <= 0;
                accumulator <= (others => '0');
            elsif mac_running = '1' then
                -- Symmetric: h[i] * (x[i] + x[TAPS-1-i])
                sym_sum := resize(shift_reg(mac_idx), DATA_WIDTH+1) +
                           resize(shift_reg(TAPS-1-mac_idx), DATA_WIDTH+1);
                prod <= resize(sym_sum, DATA_WIDTH+1) * COEFFS(mac_idx);
                accumulator <= accumulator + resize(prod, DATA_WIDTH+COEFF_WIDTH+6);

                if mac_idx = 10 then
                    mac_running <= '0';
                    -- Round and output (take MSBs)
                    data_out <= std_logic_vector(
                        accumulator(DATA_WIDTH+COEFF_WIDTH+5 downto COEFF_WIDTH+5));
                    out_valid <= '1';
                else
                    mac_idx <= mac_idx + 1;
                end if;
            end if;
        end if;
    end process;

end architecture rtl;
