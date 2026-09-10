-- XBandDigitalModule_20x20 - SpaceWire Codec
-- File: spw_codec.vhd
-- Description: SpaceWire transceiver codec (physical + link layer)
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity spw_codec is
    generic (
        CLK_FREQ    : integer := 100_000_000;
        TX_SPEED    : integer := 100       -- Mbps
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        -- Link control
        link_start  : in  std_logic;
        link_dis    : in  std_logic;
        -- TX data
        tx_data     : in  std_logic_vector(7 downto 0);
        tx_valid    : in  std_logic;
        tx_ready    : out std_logic;
        -- RX data
        rx_data     : out std_logic_vector(7 downto 0);
        rx_valid    : out std_logic;
        -- SpaceWire physical pins (active)
        spw_dout    : out std_logic;      -- data out
        spw_sout    : out std_logic;      -- strobe out
        spw_din     : in  std_logic;      -- data in
        spw_sin     : in  std_logic;      -- strobe in
        -- Status
        link_run    : out std_logic;
        link_error  : out std_logic
    );
end entity spw_codec;

architecture rtl of spw_codec is

    -- Internal signals
    signal txbit_i     : std_logic := '0';
    signal txstb_i     : std_logic := '0';
    signal rxbit_i     : std_logic := '0';
    signal rxstb_i     : std_logic := '0';
    signal link_status : std_logic_vector(3 downto 0) := (others => '0');
    signal link_err_i  : std_logic := '0';

begin

    -- Link layer instance
    u_link: entity work.spw_link
        generic map (
            CLK_FREQ => CLK_FREQ,
            TX_SPEED => TX_SPEED
        )
        port map (
            clk         => clk,
            rst_n       => rst_n,
            link_start  => link_start,
            link_dis    => link_dis,
            tx_data     => tx_data,
            tx_valid    => tx_valid,
            tx_ready    => tx_ready,
            tx_timecode => (others => '0'),
            tx_tc_valid => '0',
            rx_data     => rx_data,
            rx_valid    => rx_valid,
            rx_timecode => open,
            rx_tc_valid => open,
            txbit       => txbit_i,
            txstb       => txstb_i,
            rxbit       => rxbit_i,
            rxstb       => rxstb_i,
            link_status => link_status,
            link_error  => link_err_i
        );

    -- Physical layer: encode Data/Strobe on differential pairs
    -- SpaceWire encoding: dout = data, sout = data XOR strobe
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            spw_dout <= '0';
            spw_sout <= '0';
        elsif rising_edge(clk) then
            if txstb_i = '1' then
                spw_dout <= txbit_i;
                spw_sout <= txbit_i xor txstb_i;
            end if;
        end if;
    end process;

    -- Physical layer: decode incoming Data/Strobe
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            rxbit_i <= '0';
            rxstb_i <= '0';
        elsif rising_edge(clk) then
            rxbit_i <= spw_din;
            rxstb_i <= spw_sin xor spw_din;
        end if;
    end process;

    link_run <= link_status(0);
    link_error <= link_err_i;

end architecture rtl;
