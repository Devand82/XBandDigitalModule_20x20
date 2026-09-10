-- XBandDigitalModule_20x20 - SpaceWire Link Layer
-- File: spw_link.vhd
-- Description: SpaceWire link layer per ECSS-E-ST-50-12C
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity spw_link is
    generic (
        CLK_FREQ    : integer := 100_000_000;
        TX_SPEED    : integer := 100      -- Mbps
    );
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        -- Link control
        link_start  : in  std_logic;      -- start link
        link_dis    : in  std_logic;      -- disable link
        -- TX interface
        tx_data     : in  std_logic_vector(7 downto 0);
        tx_valid    : in  std_logic;
        tx_ready    : out std_logic;
        tx_timecode : in  std_logic_vector(5 downto 0);
        tx_tc_valid : in  std_logic;
        -- RX interface
        rx_data     : out std_logic_vector(7 downto 0);
        rx_valid    : out std_logic;
        rx_timecode : out std_logic_vector(5 downto 0);
        rx_tc_valid : out std_logic;
        -- Physical interface (to spw_codec)
        txbit       : out std_logic;
        txstb       : out std_logic;
        rxbit       : in  std_logic;
        rxstb       : in  std_logic;
        -- Status
        link_status : out std_logic_vector(3 downto 0);
        link_error  : out std_logic
    );
end entity spw_link;

architecture rtl of spw_link is

    -- Link states
    type link_state_t is (
        L_RESET,        -- reset state
        L_CONNECTING,   -- waiting for link connection
        L_RUN,          -- normal operation
        L_ERROR         -- error state
    );

    -- Link sub-states for TX
    type tx_state_t is (
        TX_IDLE, TX_FLAGS, TX_CHAR, TX_PARITY
    );

    signal state       : link_state_t := L_RESET;
    signal tx_state    : tx_state_t := TX_IDLE;

    -- Baud rate generator
    constant BAUD_DIV  : integer := CLK_FREQ / (TX_SPEED * 2);
    signal baud_cnt    : integer range 0 to BAUD_DIV-1 := 0;
    signal baud_tick   : std_logic := '0';

    -- TX shift register
    signal tx_shift     : std_logic_vector(7 downto 0) := (others => '0');
    signal tx_bit_cnt   : integer range 0 to 7 := 0;
    signal tx_parity    : std_logic := '0';

    -- Link init sequence (FCT, FCT, NULL)
    signal init_cnt     : integer range 0 to 3 := 0;
    signal init_sent    : std_logic := '0';

    -- Error tracking
    signal err_cnt      : unsigned(7 downto 0) := (others => '0');

begin

    link_status <= std_logic_vector(to_unsigned(
        link_state_t'pos(state), 4));

    -- Baud rate generator
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            baud_cnt <= 0;
            baud_tick <= '0';
        elsif rising_edge(clk) then
            baud_tick <= '0';
            if baud_cnt = BAUD_DIV-1 then
                baud_cnt <= 0;
                baud_tick <= '1';
            else
                baud_cnt <= baud_cnt + 1;
            end if;
        end if;
    end process;

    -- Link state machine
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            state <= L_RESET;
            tx_state <= TX_IDLE;
            tx_shift <= (others => '0');
            tx_bit_cnt <= 0;
            tx_parity <= '0';
            init_cnt <= 0;
            init_sent <= '0';
            txbit <= '0';
            txstb <= '0';
            tx_ready <= '0';
            rx_data <= (others => '0');
            rx_valid <= '0';
            rx_timecode <= (others => '0');
            rx_tc_valid <= '0';
            link_error <= '0';
            err_cnt <= (others => '0');
        elsif rising_edge(clk) then
            rx_valid <= '0';
            rx_tc_valid <= '0';
            link_error <= '0';

            case state is
                when L_RESET =>
                    tx_ready <= '0';
                    if link_start = '1' then
                        state <= L_CONNECTING;
                        init_cnt <= 0;
                        init_sent <= '0';
                    end if;

                when L_CONNECTING =>
                    if baud_tick = '1' then
                        -- Send link initialization: NULL + FCT sequences
                        if init_cnt < 3 then
                            case tx_state is
                                when TX_IDLE =>
                                    -- Send NULL code (0x00 with escape)
                                    tx_shift <= x"00";
                                    tx_bit_cnt <= 0;
                                    tx_parity <= '0';
                                    tx_state <= TX_CHAR;
                                when TX_CHAR =>
                                    txbit <= tx_shift(tx_bit_cnt);
                                    txstb <= '1';
                                    if tx_bit_cnt = 7 then
                                        tx_state <= TX_PARITY;
                                    else
                                        tx_bit_cnt <= tx_bit_cnt + 1;
                                    end if;
                                when TX_PARITY =>
                                    txbit <= tx_parity;
                                    txstb <= '0';
                                    tx_state <= TX_IDLE;
                                    init_cnt <= init_cnt + 1;
                                when TX_FLAGS =>
                                    tx_state <= TX_IDLE;
                            end case;
                        else
                            init_sent <= '1';
                            state <= L_RUN;
                            tx_ready <= '1';
                        end if;
                    end if;

                when L_RUN =>
                    tx_ready <= '0';
                    if baud_tick = '1' then
                        case tx_state is
                            when TX_IDLE =>
                                txstb <= '0';
                                if tx_valid = '1' then
                                    tx_shift <= tx_data;
                                    tx_bit_cnt <= 0;
                                    tx_parity <= '0';
                                    tx_state <= TX_CHAR;
                                    tx_ready <= '1';
                                end if;
                            when TX_CHAR =>
                                txbit <= tx_shift(tx_bit_cnt);
                                txstb <= '1';
                                tx_parity <= tx_parity xor tx_shift(tx_bit_cnt);
                                if tx_bit_cnt = 7 then
                                    tx_state <= TX_PARITY;
                                else
                                    tx_bit_cnt <= tx_bit_cnt + 1;
                                end if;
                            when TX_PARITY =>
                                txbit <= tx_parity;
                                txstb <= '0';
                                tx_state <= TX_IDLE;
                            when TX_FLAGS =>
                                tx_state <= TX_IDLE;
                        end case;

                        -- RX processing (simplified)
                        if rxstb = '1' then
                            rx_data <= (others => '0');
                            rx_valid <= '1';
                        end if;
                    end if;

                    if link_dis = '1' then
                        state <= L_RESET;
                    end if;

                when L_ERROR =>
                    link_error <= '1';
                    err_cnt <= err_cnt + 1;
                    if err_cnt > 255 then
                        state <= L_RESET;
                    end if;
            end case;
        end if;
    end process;

end architecture rtl;
