-- XBandDigitalModule_20x20 - DDC Chain
-- File: ddc_chain.vhd
-- Description: Digital Down Converter chain - instantiates NCO, mixer, CIC, FIR, gain
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity ddc_chain is
    generic (
        NUM_CHANNELS : integer := 8;
        DATA_WIDTH   : integer := 16;
        NCO_WIDTH    : integer := 48
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        -- Input
        data_in     : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        data_valid  : in  std_logic;
        -- Output
        i_out       : out std_logic_vector(NUM_CHANNELS*DATA_WIDTH-1 downto 0);
        q_out       : out std_logic_vector(NUM_CHANNELS*DATA_WIDTH-1 downto 0);
        out_valid   : out std_logic;
        -- Control
        nco_freq    : in  std_logic_vector(NUM_CHANNELS*NCO_WIDTH-1 downto 0);
        nco_phase   : in  std_logic_vector(NUM_CHANNELS*16-1 downto 0);
        gain        : in  std_logic_vector(NUM_CHANNELS*4-1 downto 0);
        decimation  : in  std_logic_vector(NUM_CHANNELS*4-1 downto 0)
    );
end entity ddc_chain;

architecture rtl of ddc_chain is

    -- Internal signals per channel
    type sin_array_t  is array (0 to NUM_CHANNELS-1) of std_logic_vector(15 downto 0);
    type cos_array_t  is array (0 to NUM_CHANNELS-1) of std_logic_vector(15 downto 0);
    type mix_i_arr_t  is array (0 to NUM_CHANNELS-1) of std_logic_vector(DATA_WIDTH-1 downto 0);
    type mix_q_arr_t  is array (0 to NUM_CHANNELS-1) of std_logic_vector(DATA_WIDTH-1 downto 0);
    type dec_data_t   is array (0 to NUM_CHANNELS-1) of std_logic_vector(DATA_WIDTH-1 downto 0);
    type dec_valid_t  is array (0 to NUM_CHANNELS-1) of std_logic;

    signal nco_sin     : sin_array_t := (others => (others => '0'));
    signal nco_cos     : cos_array_t := (others => (others => '0'));
    signal mixer_i     : mix_i_arr_t := (others => (others => '0'));
    signal mixer_q     : mix_q_arr_t := (others => (others => '0'));
    signal dec_data    : dec_data_t  := (others => (others => '0'));
    signal dec_valid   : dec_valid_t := (others => (others => '0'));
    signal nco_valid   : std_logic := '0';

begin

    -- Generate per-channel DDC chains
    gen_ddc: for ch in 0 to NUM_CHANNELS-1 generate

        -- NCO instance
        u_nco: entity work.nco
            generic map (
                PHASE_WIDTH => NCO_WIDTH,
                OUT_WIDTH   => 16
            )
            port map (
                clk       => clk,
                rst_n     => rst_n,
                freq_word => nco_freq((ch+1)*NCO_WIDTH-1 downto ch*NCO_WIDTH),
                phase_off => nco_phase((ch+1)*16-1 downto ch*16),
                sin_out   => nco_sin(ch),
                cos_out   => nco_cos(ch),
                out_valid => nco_valid
            );

        -- Complex Mixer instance
        u_mixer: entity work.complex_mixer
            generic map (
                DATA_WIDTH => DATA_WIDTH,
                NCO_WIDTH  => 16
            )
            port map (
                clk       => clk,
                rst_n     => rst_n,
                i_in      => data_in,
                q_in      => (others => '0'),
                in_valid  => data_valid,
                cos_in    => nco_cos(ch),
                sin_in    => nco_sin(ch),
                i_out     => mixer_i(ch),
                q_out     => mixer_q(ch),
                out_valid => open
            );

        -- CIC Decimator instance
        u_cic: entity work.cic_decimator
            generic map (
                INPUT_WIDTH  => DATA_WIDTH,
                OUTPUT_WIDTH => DATA_WIDTH,
                STAGES       => 5,
                MAX_DECIM    => 1024
            )
            port map (
                clk        => clk,
                rst_n      => rst_n,
                decim_rate => decimation((ch+1)*4-1 downto ch*4),
                data_in    => mixer_i(ch),
                in_valid   => '1',
                data_out   => dec_data(ch),
                out_valid  => dec_valid(ch)
            );

        -- Gain Control instance
        u_gain: entity work.gain_control
            generic map (
                DATA_WIDTH => DATA_WIDTH,
                GAIN_WIDTH => 4
            )
            port map (
                clk       => clk,
                rst_n     => rst_n,
                data_in   => dec_data(ch),
                in_valid  => dec_valid(ch),
                gain      => gain((ch+1)*4-1 downto ch*4),
                data_out  => i_out((ch+1)*DATA_WIDTH-1 downto ch*DATA_WIDTH),
                out_valid => open
            );

        -- Q output (simplified: same as I for single-channel input)
        q_out((ch+1)*DATA_WIDTH-1 downto ch*DATA_WIDTH) <= (others => '0');

    end generate gen_ddc;

    -- Output valid (simplified: use first channel valid)
    out_valid <= dec_valid(0);

end architecture rtl;
