-- XBandDigitalModule_20x20 - SpaceWire Interface
-- File: spacewire_interface.vhd
-- Description: Dual-link SpaceWire interface with routing
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity spacewire_interface is
    generic (
        NUM_LINKS   : integer := 2;
        TX_FIFO_DEPTH: integer := 64;
        RX_FIFO_DEPTH: integer := 64
    );
    port (
        clk             : in  std_logic;
        rst_n           : in  std_logic;
        -- SpaceWire physical
        spw_dout_p      : out std_logic_vector(NUM_LINKS-1 downto 0);
        spw_dout_n      : out std_logic_vector(NUM_LINKS-1 downto 0);
        spw_sout_p      : out std_logic_vector(NUM_LINKS-1 downto 0);
        spw_sout_n      : out std_logic_vector(NUM_LINKS-1 downto 0);
        spw_din_p       : in  std_logic_vector(NUM_LINKS-1 downto 0);
        spw_din_n       : in  std_logic_vector(NUM_LINKS-1 downto 0);
        spw_sin_p       : in  std_logic_vector(NUM_LINKS-1 downto 0);
        spw_sin_n       : in  std_logic_vector(NUM_LINKS-1 downto 0);
        -- Data interface
        tx_data         : in  std_logic_vector(NUM_LINKS*8-1 downto 0);
        tx_valid        : in  std_logic_vector(NUM_LINKS-1 downto 0);
        tx_ready        : out std_logic_vector(NUM_LINKS-1 downto 0);
        rx_data         : out std_logic_vector(NUM_LINKS*8-1 downto 0);
        rx_valid        : out std_logic_vector(NUM_LINKS-1 downto 0);
        -- Status
        link_run        : out std_logic_vector(NUM_LINKS-1 downto 0);
        link_error      : out std_logic_vector(NUM_LINKS-1 downto 0)
    );
end entity spacewire_interface;

architecture rtl of spacewire_interface is

    type spw_state_t is (S_RESET, S_RUN, S_ERROR);

    signal state_0       : spw_state_t := S_RESET;
    signal state_1       : spw_state_t := S_RESET;
    signal bit_cnt_0     : unsigned(2 downto 0) := (others => '0');
    signal bit_cnt_1     : unsigned(2 downto 0) := (others => '0');
    signal tx_shift_0    : std_logic_vector(7 downto 0) := (others => '0');
    signal tx_shift_1    : std_logic_vector(7 downto 0) := (others => '0');
    signal tx_running_i  : std_logic_vector(NUM_LINKS-1 downto 0) := (others => '0');
    signal dout_i        : std_logic_vector(NUM_LINKS-1 downto 0);
    signal sout_i        : std_logic_vector(NUM_LINKS-1 downto 0);

begin

    -- Link 0
    spw_dout_p(0) <= dout_i(0);
    spw_dout_n(0) <= not dout_i(0);
    spw_sout_p(0) <= sout_i(0);
    spw_sout_n(0) <= not sout_i(0);
    tx_ready(0) <= tx_running_i(0);
    link_run(0) <= tx_running_i(0);
    link_error(0) <= '0';
    rx_valid(0) <= '0';
    rx_data(7 downto 0) <= (others => '0');

    -- Link 1 (if present)
    gen_link1: if NUM_LINKS > 1 generate
        spw_dout_p(1) <= dout_i(1);
        spw_dout_n(1) <= not dout_i(1);
        spw_sout_p(1) <= sout_i(1);
        spw_sout_n(1) <= not sout_i(1);
        tx_ready(1) <= tx_running_i(1);
        link_run(1) <= tx_running_i(1);
        link_error(1) <= '0';
        rx_valid(1) <= '0';
        rx_data(15 downto 8) <= (others => '0');
    end generate gen_link1;

    -- Link 0 process
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            state_0 <= S_RESET;
            tx_running_i(0) <= '0';
            dout_i(0) <= '0';
            sout_i(0) <= '0';
            bit_cnt_0 <= (others => '0');
            tx_shift_0 <= (others => '0');
        elsif rising_edge(clk) then
            case state_0 is
                when S_RESET =>
                    tx_running_i(0) <= '0';
                    if tx_valid(0) = '1' then
                        state_0 <= S_RUN;
                        tx_running_i(0) <= '1';
                        tx_shift_0 <= tx_data(7 downto 0);
                        bit_cnt_0 <= (others => '0');
                    end if;
                when S_RUN =>
                    if tx_valid(0) = '1' and bit_cnt_0 = "000" then
                        tx_shift_0 <= tx_data(7 downto 0);
                    end if;
                    dout_i(0) <= tx_shift_0(to_integer(bit_cnt_0));
                    sout_i(0) <= bit_cnt_0(0);
                    if bit_cnt_0 = "111" then
                        bit_cnt_0 <= (others => '0');
                    else
                        bit_cnt_0 <= bit_cnt_0 + 1;
                    end if;
                when S_ERROR =>
                    tx_running_i(0) <= '0';
                    state_0 <= S_RESET;
            end case;
        end if;
    end process;

    -- Link 1 process
    gen_proc1: if NUM_LINKS > 1 generate
        process(clk, rst_n)
        begin
            if rst_n = '0' then
                state_1 <= S_RESET;
                tx_running_i(1) <= '0';
                dout_i(1) <= '0';
                sout_i(1) <= '0';
                bit_cnt_1 <= (others => '0');
                tx_shift_1 <= (others => '0');
            elsif rising_edge(clk) then
                case state_1 is
                    when S_RESET =>
                        tx_running_i(1) <= '0';
                        if tx_valid(1) = '1' then
                            state_1 <= S_RUN;
                            tx_running_i(1) <= '1';
                            tx_shift_1 <= tx_data(15 downto 8);
                            bit_cnt_1 <= (others => '0');
                        end if;
                    when S_RUN =>
                        if tx_valid(1) = '1' and bit_cnt_1 = "000" then
                            tx_shift_1 <= tx_data(15 downto 8);
                        end if;
                        dout_i(1) <= tx_shift_1(to_integer(bit_cnt_1));
                        sout_i(1) <= bit_cnt_1(0);
                        if bit_cnt_1 = "111" then
                            bit_cnt_1 <= (others => '0');
                        else
                            bit_cnt_1 <= bit_cnt_1 + 1;
                        end if;
                    when S_ERROR =>
                        tx_running_i(1) <= '0';
                        state_1 <= S_RESET;
                end case;
            end if;
        end process;
    end generate gen_proc1;

end architecture rtl;
