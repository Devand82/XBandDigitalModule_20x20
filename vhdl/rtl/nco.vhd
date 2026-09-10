-- XBandDigitalModule_20x20 - NCO (Numerically Controlled Oscillator)
-- File: nco.vhd
-- Description: 48-bit phase accumulator NCO with CORDIC sin/cos lookup
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity nco is
    generic (
        PHASE_WIDTH : integer := 48;
        OUT_WIDTH   : integer := 16
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        -- Control
        freq_word   : in  std_logic_vector(PHASE_WIDTH-1 downto 0);  -- phase increment
        phase_off   : in  std_logic_vector(PHASE_WIDTH-1 downto 0);  -- phase offset
        -- Output
        sin_out     : out std_logic_vector(OUT_WIDTH-1 downto 0);
        cos_out     : out std_logic_vector(OUT_WIDTH-1 downto 0);
        out_valid   : out std_logic
    );
end entity nco;

architecture rtl of nco is

    -- CORDIC iteration count
    constant CORDIC_STAGES : integer := 16;

    -- Precomputed CORDIC angles (atan(2^-i) in fixed point Q1.15)
    type angle_table_t is array (0 to CORDIC_STAGES-1) of signed(15 downto 0);
    constant ATAN_TABLE : angle_table_t := (
        to_signed(16#4000#, 16),  -- atan(2^0)  = 45.000 deg
        to_signed(16#25C8#, 16),  -- atan(2^-1) = 26.565 deg
        to_signed(16#13F6#, 16),  -- atan(2^-2) = 14.036 deg
        to_signed(16#0A22#, 16),  -- atan(2^-3) =  7.125 deg
        to_signed(16#0516#, 16),  -- atan(2^-4) =  3.576 deg
        to_signed(16#028B#, 16),  -- atan(2^-5) =  1.790 deg
        to_signed(16#0146#, 16),  -- atan(2^-6) =  0.895 deg
        to_signed(16#00A3#, 16),  -- atan(2^-7) =  0.448 deg
        to_signed(16#0051#, 16),  -- atan(2^-8) =  0.224 deg
        to_signed(16#0029#, 16),  -- atan(2^-9) =  0.112 deg
        to_signed(16#0014#, 16),  -- atan(2^-10) = 0.056 deg
        to_signed(16#000A#, 16),  -- atan(2^-11) = 0.028 deg
        to_signed(16#0005#, 16),  -- atan(2^-12) = 0.014 deg
        to_signed(16#0003#, 16),  -- atan(2^-13) = 0.007 deg
        to_signed(16#0001#, 16),  -- atan(2^-14) = 0.004 deg
        to_signed(16#0001#, 16)   -- atan(2^-15) = 0.002 deg
    );

    -- Gain correction for 16-stage CORDIC: product = 0.607252935
    -- In Q1.15: 0.607252935 * 32768 = 19898 = x"4DB2"
    constant CORDIC_GAIN : signed(15 downto 0) := to_signed(19898, 16);

    -- Phase accumulator
    signal phase_acc    : unsigned(PHASE_WIDTH-1 downto 0) := (others => '0');
    signal phase_sum    : unsigned(PHASE_WIDTH-1 downto 0) := (others => '0');

    -- CORDIC pipeline registers
    type cordic_x_t is array (0 to CORDIC_STAGES) of signed(15 downto 0);
    type cordic_y_t is array (0 to CORDIC_STAGES) of signed(15 downto 0);
    type cordic_z_t is array (0 to CORDIC_STAGES) of signed(15 downto 0);

    signal cx : cordic_x_t := (others => (others => '0'));
    signal cy : cordic_y_t := (others => (others => '0'));
    signal cz : cordic_z_t := (others => (others => '0'));

    -- CORDIC valid pipeline
    signal cordic_valid : std_logic_vector(0 to CORDIC_STAGES) := (others => '0');

    -- Quadrant info
    signal quadrant     : std_logic_vector(1 downto 0) := "00";

begin

    -- Phase accumulator
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            phase_acc <= (others => '0');
        elsif rising_edge(clk) then
            phase_acc <= phase_acc + unsigned(freq_word);
        end if;
    end process;

    -- Phase sum with offset
    phase_sum <= phase_acc + unsigned(phase_off);

    -- Quadrant selection and phase reduction to [0, pi/2]
    process(phase_sum)
        variable phase_ext : signed(15 downto 0);
    begin
        quadrant <= phase_sum(PHASE_WIDTH-1 downto PHASE_WIDTH-2);
        case phase_sum(PHASE_WIDTH-1 downto PHASE_WIDTH-2) is
            when "00" =>  -- Q1: 0 to pi/2
                phase_ext := signed(phase_sum(PHASE_WIDTH-3 downto PHASE_WIDTH-18));
            when "01" =>  -- Q2: pi/2 to pi
                phase_ext := to_signed(16#7FFF#, 16) -
                             signed(phase_sum(PHASE_WIDTH-3 downto PHASE_WIDTH-18));
            when "10" =>  -- Q3: pi to 3pi/2
                phase_ext := signed(phase_sum(PHASE_WIDTH-3 downto PHASE_WIDTH-18));
            when others => -- Q4: 3pi/2 to 2pi
                phase_ext := to_signed(16#7FFF#, 16) -
                             signed(phase_sum(PHASE_WIDTH-3 downto PHASE_WIDTH-18));
        end case;
        cz(0) <= phase_ext;
    end process;

    -- CORDIC initial values
    cx(0) <= CORDIC_GAIN;
    cy(0) <= (others => '0');

    -- CORDIC pipeline stages
    gen_cordic: for i in 0 to CORDIC_STAGES-1 generate
        process(clk, rst_n)
            variable x_new, y_new : signed(15 downto 0);
        begin
            if rst_n = '0' then
                cx(i+1) <= (others => '0');
                cy(i+1) <= (others => '0');
                cz(i+1) <= (others => '0');
            elsif rising_edge(clk) then
                if cz(i) >= 0 then
                    x_new := cx(i) - shift_right(cy(i), i);
                    y_new := cy(i) + shift_right(cx(i), i);
                    cz(i+1) <= cz(i) - ATAN_TABLE(i);
                else
                    x_new := cx(i) + shift_right(cy(i), i);
                    y_new := cy(i) - shift_right(cx(i), i);
                    cz(i+1) <= cz(i) + ATAN_TABLE(i);
                end if;
                cx(i+1) <= x_new;
                cy(i+1) <= y_new;
            end if;
        end process;
    end generate gen_cordic;

    -- Valid pipeline
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            cordic_valid <= (others => '0');
        elsif rising_edge(clk) then
            cordic_valid(0) <= '1';
            for i in 1 to CORDIC_STAGES loop
                cordic_valid(i) <= cordic_valid(i-1);
            end loop;
        end if;
    end process;

    -- Output quadrant correction
    process(clk, rst_n)
        variable cos_val, sin_val : signed(15 downto 0);
    begin
        if rst_n = '0' then
            sin_out <= (others => '0');
            cos_out <= (others => '0');
            out_valid <= '0';
        elsif rising_edge(clk) then
            out_valid <= cordic_valid(CORDIC_STAGES);
            if cordic_valid(CORDIC_STAGES) = '1' then
                case quadrant is
                    when "00" =>  -- Q1
                        cos_out <= std_logic_vector(cx(CORDIC_STAGES));
                        sin_out <= std_logic_vector(cy(CORDIC_STAGES));
                    when "01" =>  -- Q2
                        cos_out <= std_logic_vector(-cy(CORDIC_STAGES));
                        sin_out <= std_logic_vector(cx(CORDIC_STAGES));
                    when "10" =>  -- Q3
                        cos_out <= std_logic_vector(-cx(CORDIC_STAGES));
                        sin_out <= std_logic_vector(-cy(CORDIC_STAGES));
                    when others => -- Q4
                        cos_out <= std_logic_vector(cy(CORDIC_STAGES));
                        sin_out <= std_logic_vector(-cx(CORDIC_STAGES));
                end case;
            end if;
        end if;
    end process;

end architecture rtl;
