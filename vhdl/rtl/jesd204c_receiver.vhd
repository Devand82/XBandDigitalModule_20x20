-- XBandDigitalModule_20x20 - JESD204C Receiver
-- File: jesd204c_receiver.vhd
-- Description: JESD204C receiver with 16-lane support
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity jesd204c_receiver is
    generic (
        NUM_LANES   : integer := 16;
        DATA_WIDTH  : integer := 32;
        FRAME_SIZE  : integer := 32   -- 64B/66B frame size in bytes
    );
    port (
        -- Clock and Reset
        clk             : in  std_logic;                       -- System clock
        rst_n           : in  std_logic;                       -- Active low reset
        
        -- JESD204C Physical Interface
        refclk_p        : in  std_logic;                       -- Reference clock (diff+)
        refclk_n        : in  std_logic;                       -- Reference clock (diff-)
        rx_p            : in  std_logic_vector(NUM_LANES-1 downto 0);  -- RX data (diff+)
        rx_n            : in  std_logic_vector(NUM_LANES-1 downto 0);  -- RX data (diff-)
        sync_n          : out std_logic;                       -- Sync (active low)
        sysref          : in  std_logic;                       -- SYSREF signal
        
        -- Parallel Data Output
        data_out        : out std_logic_vector(DATA_WIDTH-1 downto 0);
        data_valid      : out std_logic;
        
        -- Status
        status          : out std_logic_vector(31 downto 0)
    );
end entity jesd204c_receiver;

architecture rtl of jesd204c_receiver is

    -- =========================================================================
    -- Constants
    -- =========================================================================
    constant SYNC_RESET_CYCLES : integer := 16;
    constant LANE_SYNC_TIMEOUT : integer := 1000;
    
    -- =========================================================================
    -- Component Declarations
    -- =========================================================================
    
    -- JESD204C Physical Layer (GTY Transceiver)
    component jesd204c_phy is
        generic (
            NUM_LANES   : integer := 16;
            LINE_RATE   : real := 16.0   -- Gbps
        );
        port (
            refclk      : in  std_logic;
            rx_p        : in  std_logic_vector(NUM_LANES-1 downto 0);
            rx_n        : in  std_logic_vector(NUM_LANES-1 downto 0);
            tx_p        : out std_logic_vector(NUM_LANES-1 downto 0);
            tx_n        : out std_logic_vector(NUM_LANES-1 downto 0);
            rx_data     : out std_logic_vector(NUM_LANES*64-1 downto 0);
            rx_valid    : out std_logic;
            tx_data     : in  std_logic_vector(NUM_LANES*64-1 downto 0);
            tx_valid    : in  std_logic;
            aligned     : out std_logic;
            lane_sync   : out std_logic_vector(NUM_LANES-1 downto 0)
        );
    end component jesd204c_phy;
    
    -- JESD204C Link Layer
    component jesd204c_link is
        generic (
            NUM_LANES   : integer := 16;
            DATA_WIDTH  : integer := 512   -- 16 lanes * 32 bits
        );
        port (
            clk         : in  std_logic;
            rst_n       : in  std_logic;
            -- PHY interface
            phy_data    : in  std_logic_vector(DATA_WIDTH-1 downto 0);
            phy_valid   : in  std_logic;
            -- Link control
            sync_n      : out std_logic;
            sysref      : in  std_logic;
            -- Frame data output
            frame_data  : out std_logic_vector(DATA_WIDTH-1 downto 0);
            frame_valid : out std_logic;
            -- Status
            frame_err   : out std_logic;
            code_err    : out std_logic_vector(NUM_LANES-1 downto 0)
        );
    end component jesd204c_link;
    
    -- JESD204C Transport Layer
    component jesd204c_transport is
        generic (
            NUM_LANES   : integer := 16;
            SAMPLE_WIDTH: integer := 12;
            NUM_SAMPLES : integer := 8    -- Samples per frame
        );
        port (
            clk         : in  std_logic;
            rst_n       : in  std_logic;
            -- Frame data input
            frame_data  : in  std_logic_vector(NUM_LANES*32-1 downto 0);
            frame_valid : in  std_logic;
            -- Sample data output
            sample_data : out std_logic_vector(NUM_SAMPLES*SAMPLE_WIDTH-1 downto 0);
            sample_valid: out std_logic;
            -- Status
            transport_err: out std_logic
        );
    end component jesd204c_transport;

    -- =========================================================================
    -- Signal Declarations
    -- =========================================================================
    
    -- Internal reset
    signal rst_n_i          : std_logic;
    
    -- Reference clock
    signal refclk           : std_logic;
    
    -- PHY signals
    signal phy_data         : std_logic_vector(NUM_LANES*64-1 downto 0);
    signal phy_valid        : std_logic;
    signal phy_aligned      : std_logic;
    signal phy_lane_sync    : std_logic_vector(NUM_LANES-1 downto 0);
    
    -- Link signals
    signal link_data        : std_logic_vector(NUM_LANES*32-1 downto 0);
    signal link_valid       : std_logic;
    signal link_frame_err   : std_logic;
    signal link_code_err    : std_logic_vector(NUM_LANES-1 downto 0);
    
    -- Transport signals
    signal transport_data   : std_logic_vector(8*12-1 downto 0);
    signal transport_valid  : std_logic;
    signal transport_err    : std_logic;
    
    -- Synchronization state machine
    type sync_state_t is (RESET, WAIT_SYSREF, SYNC_REQUEST, SYNC_WAIT, ALIGNED, ERROR);
    signal sync_state       : sync_state_t := RESET;
    signal sync_cnt         : integer range 0 to SYNC_RESET_CYCLES := 0;
    signal sync_timeout     : integer range 0 to LANE_SYNC_TIMEOUT := 0;
    
    -- SYSREF sampling
    signal sysref_sync      : std_logic_vector(2 downto 0) := (others => '0');
    signal sysref_detected  : std_logic := '0';
    
    -- Error counters
    signal frame_err_cnt    : unsigned(7 downto 0) := (others => '0');
    signal code_err_cnt     : unsigned(7 downto 0) := (others => '0');

begin

    -- =========================================================================
    -- Reset Synchronization
    -- =========================================================================
    rst_n_i <= rst_n;

    -- =========================================================================
    -- Reference Clock Buffer
    -- =========================================================================
    u_refclk_buf : entity work.ibufds
        port map (
            I  => refclk_p,
            IB => refclk_n,
            O  => refclk
        );

    -- =========================================================================
    -- JESD204C Physical Layer Instance
    -- =========================================================================
    u_phy : jesd204c_phy
        generic map (
            NUM_LANES   => NUM_LANES,
            LINE_RATE   => 16.0   -- 16 Gbps per lane
        )
        port map (
            refclk      => refclk,
            rx_p        => rx_p,
            rx_n        => rx_n,
            tx_p        => open,
            tx_n        => open,
            rx_data     => phy_data,
            rx_valid    => phy_valid,
            tx_data     => (others => '0'),
            tx_valid    => '0',
            aligned     => phy_aligned,
            lane_sync   => phy_lane_sync
        );

    -- =========================================================================
    -- JESD204C Link Layer Instance
    -- =========================================================================
    u_link : jesd204c_link
        generic map (
            NUM_LANES   => NUM_LANES,
            DATA_WIDTH  => NUM_LANES*32
        )
        port map (
            clk         => clk,
            rst_n       => rst_n_i,
            phy_data    => phy_data(NUM_LANES*32-1 downto 0),
            phy_valid   => phy_valid,
            sync_n      => sync_n,
            sysref      => sysref,
            frame_data  => link_data,
            frame_valid => link_valid,
            frame_err   => link_frame_err,
            code_err    => link_code_err
        );

    -- =========================================================================
    -- JESD204C Transport Layer Instance
    -- =========================================================================
    u_transport : jesd204c_transport
        generic map (
            NUM_LANES   => NUM_LANES,
            SAMPLE_WIDTH=> 12,
            NUM_SAMPLES => 8
        )
        port map (
            clk         => clk,
            rst_n       => rst_n_i,
            frame_data  => link_data,
            frame_valid => link_valid,
            sample_data => transport_data,
            sample_valid=> transport_valid,
            transport_err=> transport_err
        );

    -- =========================================================================
    -- SYSREF Synchronization
    -- =========================================================================
    process(clk, rst_n_i)
    begin
        if rst_n_i = '0' then
            sysref_sync <= (others => '0');
            sysref_detected <= '0';
        elsif rising_edge(clk) then
            sysref_sync <= sysref_sync(1 downto 0) & sysref;
            sysref_detected <= sysref_sync(2) and not sysref_sync(1);
        end if;
    end process;

    -- =========================================================================
    -- Synchronization State Machine
    -- =========================================================================
    process(clk, rst_n_i)
    begin
        if rst_n_i = '0' then
            sync_state <= RESET;
            sync_cnt <= 0;
            sync_timeout <= 0;
        elsif rising_edge(clk) then
            case sync_state is
                when RESET =>
                    if sync_cnt = SYNC_RESET_CYCLES then
                        sync_state <= WAIT_SYSREF;
                        sync_cnt <= 0;
                    else
                        sync_cnt <= sync_cnt + 1;
                    end if;
                    
                when WAIT_SYSREF =>
                    if sysref_detected = '1' then
                        sync_state <= SYNC_REQUEST;
                    end if;
                    
                when SYNC_REQUEST =>
                    if phy_aligned = '1' then
                        sync_state <= SYNC_WAIT;
                        sync_timeout <= 0;
                    elsif sync_timeout = LANE_SYNC_TIMEOUT then
                        sync_state <= ERROR;
                    else
                        sync_timeout <= sync_timeout + 1;
                    end if;
                    
                when SYNC_WAIT =>
                    if link_valid = '1' then
                        sync_state <= ALIGNED;
                    elsif sync_timeout = LANE_SYNC_TIMEOUT then
                        sync_state <= ERROR;
                    else
                        sync_timeout <= sync_timeout + 1;
                    end if;
                    
                when ALIGNED =>
                    if link_frame_err = '1' or transport_err = '1' then
                        sync_state <= ERROR;
                    end if;
                    
                when ERROR =>
                    sync_state <= RESET;
                    
                when others =>
                    sync_state <= RESET;
            end case;
        end if;
    end process;

    -- =========================================================================
    -- Error Counters
    -- =========================================================================
    process(clk, rst_n_i)
    begin
        if rst_n_i = '0' then
            frame_err_cnt <= (others => '0');
            code_err_cnt <= (others => '0');
        elsif rising_edge(clk) then
            if link_frame_err = '1' and frame_err_cnt /= 255 then
                frame_err_cnt <= frame_err_cnt + 1;
            end if;
            
            if link_code_err /= x"00" and code_err_cnt /= 255 then
                code_err_cnt <= code_err_cnt + 1;
            end if;
        end if;
    end process;

    -- =========================================================================
    -- Output Assignments
    -- =========================================================================
    data_out <= transport_data(DATA_WIDTH-1 downto 0);
    data_valid <= transport_valid and (sync_state = ALIGNED);

    -- =========================================================================
    -- Status Register
    -- =========================================================================
    process(frame_err_cnt, code_err_cnt, sync_state, phy_aligned)
        variable state_int : unsigned(2 downto 0);
    begin
        case sync_state is
            when RESET       => state_int := to_unsigned(0, 3);
            when WAIT_SYSREF => state_int := to_unsigned(1, 3);
            when SYNC_REQUEST=> state_int := to_unsigned(2, 3);
            when SYNC_WAIT   => state_int := to_unsigned(3, 3);
            when ALIGNED     => state_int := to_unsigned(4, 3);
            when ERROR       => state_int := to_unsigned(5, 3);
            when others      => state_int := to_unsigned(7, 3);
        end case;
        status <= std_logic_vector(frame_err_cnt) &
                  std_logic_vector(code_err_cnt) &
                  "00" &
                  std_logic_vector(state_int) &
                  "00" &
                  phy_aligned &
                  '0' & '0' & '0' & '0' & '0' & '0' & '0' & '0';
    end process;

end architecture rtl;
