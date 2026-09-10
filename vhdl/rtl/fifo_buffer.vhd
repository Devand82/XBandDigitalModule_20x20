-- XBandDigitalModule_20x20 - FIFO Buffer
-- File: fifo_buffer.vhd
-- Description: Asynchronous FIFO for clock domain crossing
-- Author: FPGA/VHDL Engineer
-- Date: 2026-09-09
-- Version: 1.0

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity fifo_buffer is
    generic (
        DATA_WIDTH  : integer := 32;
        DEPTH       : integer := 4096;
        ADDR_WIDTH  : integer := 12
    );
    port (
        -- Write port
        wr_clk      : in  std_logic;
        rd_clk      : in  std_logic;
        rst_n       : in  std_logic;
        -- Write port
        wr_data     : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        wr_en       : in  std_logic;
        -- Read port
        rd_data     : out std_logic_vector(DATA_WIDTH-1 downto 0);
        rd_en       : in  std_logic;
        -- Status
        full        : out std_logic;
        empty       : out std_logic;
        level       : out std_logic_vector(15 downto 0)
    );
end entity fifo_buffer;

architecture rtl of fifo_buffer is
    type ram_t is array (0 to DEPTH-1) of std_logic_vector(DATA_WIDTH-1 downto 0);
    signal ram          : ram_t := (others => (others => '0'));
    signal wr_ptr       : unsigned(ADDR_WIDTH-1 downto 0) := (others => '0');
    signal rd_ptr       : unsigned(ADDR_WIDTH-1 downto 0) := (others => '0');
    signal wr_ptr_gray  : unsigned(ADDR_WIDTH-1 downto 0) := (others => '0');
    signal rd_ptr_gray  : unsigned(ADDR_WIDTH-1 downto 0) := (others => '0');
    signal wr_ptr_sync  : unsigned(ADDR_WIDTH-1 downto 0) := (others => '0');
    signal rd_ptr_sync  : unsigned(ADDR_WIDTH-1 downto 0) := (others => '0');
    signal full_i       : std_logic := '0';
    signal empty_i      : std_logic := '1';

    function bin2gray(b : unsigned) return unsigned is
        variable g : unsigned(b'range);
    begin
        g(b'high) := b(b'high);
        for i in b'high-1 downto 0 loop
            g(i) := b(i+1) xor b(i);
        end loop;
        return g;
    end function;

begin
    full <= full_i;
    empty <= empty_i;
    level <= std_logic_vector(to_unsigned(DEPTH, 16)) when full_i = '1' else
             std_logic_vector(to_unsigned(0, 16)) when empty_i = '1' else
             std_logic_vector(resize(wr_ptr - rd_ptr, 16));

    -- Write process
    process(wr_clk, rst_n)
    begin
        if rst_n = '0' then
            wr_ptr <= (others => '0');
        elsif rising_edge(wr_clk) then
            if wr_en = '1' and full_i = '0' then
                ram(to_integer(wr_ptr)) <= wr_data;
                wr_ptr <= wr_ptr + 1;
            end if;
        end if;
    end process;

    -- Read process
    process(rd_clk, rst_n)
    begin
        if rst_n = '0' then
            rd_ptr <= (others => '0');
        elsif rising_edge(rd_clk) then
            if rd_en = '1' and empty_i = '0' then
                rd_ptr <= rd_ptr + 1;
            end if;
        end if;
    end process;
    rd_data <= ram(to_integer(rd_ptr));

    -- Binary to Gray conversion for write pointer
    process(wr_clk, rst_n)
    begin
        if rst_n = '0' then
            wr_ptr_gray <= (others => '0');
        elsif rising_edge(wr_clk) then
            wr_ptr_gray <= bin2gray(wr_ptr);
        end if;
    end process;

    -- Binary to Gray conversion for read pointer
    process(rd_clk, rst_n)
    begin
        if rst_n = '0' then
            rd_ptr_gray <= (others => '0');
        elsif rising_edge(rd_clk) then
            rd_ptr_gray <= bin2gray(rd_ptr);
        end if;
    end process;

    -- Synchronize write pointer to read clock domain
    process(rd_clk, rst_n)
    begin
        if rst_n = '0' then
            wr_ptr_sync <= (others => '0');
        elsif rising_edge(rd_clk) then
            wr_ptr_sync <= wr_ptr_gray;
        end if;
    end process;

    -- Synchronize read pointer to write clock domain
    process(wr_clk, rst_n)
    begin
        if rst_n = '0' then
            rd_ptr_sync <= (others => '0');
        elsif rising_edge(wr_clk) then
            rd_ptr_sync <= rd_ptr_gray;
        end if;
    end process;

    -- Full flag (write domain)
    process(wr_clk, rst_n)
    begin
        if rst_n = '0' then
            full_i <= '0';
        elsif rising_edge(wr_clk) then
            if bin2gray(wr_ptr + 1) = (rd_ptr_sync(ADDR_WIDTH-1 downto 1) &
                                       (rd_ptr_sync(0) xor wr_ptr_sync(0))) then
                full_i <= '1';
            else
                full_i <= '0';
            end if;
        end if;
    end process;

    -- Empty flag (read domain)
    process(rd_clk, rst_n)
    begin
        if rst_n = '0' then
            empty_i <= '1';
        elsif rising_edge(rd_clk) then
            if bin2gray(rd_ptr) = wr_ptr_sync then
                empty_i <= '1';
            else
                empty_i <= '0';
            end if;
        end if;
    end process;
end architecture rtl;
