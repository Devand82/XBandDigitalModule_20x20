-- XBandDigitalModule_20x20 - AXI4-Lite Slave
-- File: axi4_lite_slave.vhd
-- Description: AXI4-Lite slave interface for register access
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity axi4_lite_slave is
    port (
        clk         : in  std_logic;
        rst_n       : in  std_logic;
        -- AXI4-Lite write address channel
        s_axi_awaddr  : in  std_logic_vector(11 downto 0);
        s_axi_awvalid : in  std_logic;
        s_axi_awready : out std_logic;
        -- AXI4-Lite write data channel
        s_axi_wdata   : in  std_logic_vector(31 downto 0);
        s_axi_wstrb   : in  std_logic_vector(3 downto 0);
        s_axi_wvalid  : in  std_logic;
        s_axi_wready  : out std_logic;
        -- AXI4-Lite write response channel
        s_axi_bresp   : out std_logic_vector(1 downto 0);
        s_axi_bvalid  : out std_logic;
        s_axi_bready  : in  std_logic;
        -- AXI4-Lite read address channel
        s_axi_araddr  : in  std_logic_vector(11 downto 0);
        s_axi_arvalid : in  std_logic;
        s_axi_arready : out std_logic;
        -- AXI4-Lite read data channel
        s_axi_rdata   : out std_logic_vector(31 downto 0);
        s_axi_rresp   : out std_logic_vector(1 downto 0);
        s_axi_rvalid  : out std_logic;
        s_axi_rready  : in  std_logic;
        -- Register interface (to register file)
        reg_addr      : out std_logic_vector(11 downto 0);
        reg_wdata     : out std_logic_vector(31 downto 0);
        reg_rdata     : in  std_logic_vector(31 downto 0);
        reg_we        : out std_logic;
        reg_re        : out std_logic
    );
end entity axi4_lite_slave;

architecture rtl of axi4_lite_slave is

    type aw_state_t is (AW_IDLE, AW_WAIT, AW_DONE);
    type w_state_t  is (W_IDLE, W_WAIT, W_DONE);
    type ar_state_t is (AR_IDLE, AR_WAIT, AR_DONE);

    signal aw_state : aw_state_t := AW_IDLE;
    signal w_state  : w_state_t  := W_IDLE;
    signal ar_state : ar_state_t := AR_IDLE;

    signal aw_ready_i : std_logic := '0';
    signal w_ready_i  : std_logic := '0';
    signal ar_ready_i : std_logic := '0';
    signal b_valid_i  : std_logic := '0';
    signal r_valid_i  : std_logic := '0';

    signal aw_addr    : std_logic_vector(11 downto 0) := (others => '0');
    signal w_data     : std_logic_vector(31 downto 0) := (others => '0');
    signal w_strb     : std_logic_vector(3 downto 0) := (others => '0');
    signal r_data_i   : std_logic_vector(31 downto 0) := (others => '0');

begin

    s_axi_awready <= aw_ready_i;
    s_axi_wready  <= w_ready_i;
    s_axi_bresp   <= "00";  -- OKAY
    s_axi_bvalid  <= b_valid_i;
    s_axi_arready <= ar_ready_i;
    s_axi_rdata   <= r_data_i;
    s_axi_rresp   <= "00";  -- OKAY
    s_axi_rvalid  <= r_valid_i;

    reg_addr <= aw_addr;
    reg_wdata <= w_data;

    -- Write address channel
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            aw_state <= AW_IDLE;
            aw_ready_i <= '0';
            aw_addr <= (others => '0');
        elsif rising_edge(clk) then
            case aw_state is
                when AW_IDLE =>
                    aw_ready_i <= '0';
                    if s_axi_awvalid = '1' then
                        aw_addr <= s_axi_awaddr;
                        aw_ready_i <= '1';
                        aw_state <= AW_WAIT;
                    end if;
                when AW_WAIT =>
                    aw_ready_i <= '0';
                    aw_state <= AW_DONE;
                when AW_DONE =>
                    if b_valid_i = '0' or s_axi_bready = '1' then
                        aw_state <= AW_IDLE;
                    end if;
            end case;
        end if;
    end process;

    -- Write data channel
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            w_state <= W_IDLE;
            w_ready_i <= '0';
            w_data <= (others => '0');
            w_strb <= (others => '0');
            reg_we <= '0';
        elsif rising_edge(clk) then
            reg_we <= '0';
            case w_state is
                when W_IDLE =>
                    w_ready_i <= '0';
                    if s_axi_wvalid = '1' then
                        w_data <= s_axi_wdata;
                        w_strb <= s_axi_wstrb;
                        w_ready_i <= '1';
                        w_state <= W_WAIT;
                    end if;
                when W_WAIT =>
                    w_ready_i <= '0';
                    reg_we <= '1';
                    w_state <= W_DONE;
                when W_DONE =>
                    if b_valid_i = '0' or s_axi_bready = '1' then
                        w_state <= W_IDLE;
                    end if;
            end case;
        end if;
    end process;

    -- Write response channel
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            b_valid_i <= '0';
        elsif rising_edge(clk) then
            if aw_state = AW_DONE and w_state = W_DONE and b_valid_i = '0' then
                b_valid_i <= '1';
            elsif b_valid_i = '1' and s_axi_bready = '1' then
                b_valid_i <= '0';
            end if;
        end if;
    end process;

    -- Read address channel
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            ar_state <= AR_IDLE;
            ar_ready_i <= '0';
            reg_re <= '0';
        elsif rising_edge(clk) then
            reg_re <= '0';
            case ar_state is
                when AR_IDLE =>
                    ar_ready_i <= '0';
                    if s_axi_arvalid = '1' then
                        reg_addr <= s_axi_araddr;
                        reg_re <= '1';
                        ar_ready_i <= '1';
                        ar_state <= AR_WAIT;
                    end if;
                when AR_WAIT =>
                    ar_ready_i <= '0';
                    r_data_i <= reg_rdata;
                    ar_state <= AR_DONE;
                when AR_DONE =>
                    if r_valid_i = '0' or s_axi_rready = '1' then
                        ar_state <= AR_IDLE;
                    end if;
            end case;
        end if;
    end process;

    -- Read data channel
    process(clk, rst_n)
    begin
        if rst_n = '0' then
            r_valid_i <= '0';
        elsif rising_edge(clk) then
            if ar_state = AR_DONE and r_valid_i = '0' then
                r_valid_i <= '1';
            elsif r_valid_i = '1' and s_axi_rready = '1' then
                r_valid_i <= '0';
            end if;
        end if;
    end process;

end architecture rtl;
