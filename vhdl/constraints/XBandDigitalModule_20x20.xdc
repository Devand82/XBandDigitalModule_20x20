# XBandDigitalModule_20x20 - FPGA Constraints
# File: XBandDigitalModule_20x20.xdc
# Description: Timing and placement constraints for XQRVC1902
# Tool: Vivado 2024.1+
# Date: 2026-09-09

## Clock Constraints
# System clock 100 MHz
create_clock -period 10.000 -name sys_clk -waveform {0.000 5.000} [get_ports sys_clk]

# JESD204C reference clock 10.4 GHz (derived from LMX2615-SP)
create_clock -period 0.096 -name jesd_refclk -waveform {0.000 0.048} [get_ports jesd_refclk_p]

# JESD204C device clock (10.4 GHz / 66 = 157.576 MHz)
create_clock -period 6.347 -name jesd_device_clk -waveform {0.000 3.174]

# DDC processing clock 500 MHz
create_clock -period 2.000 -name ddc_clk -waveform {0.000 1.000]

# SpaceWire clock 100 MHz
create_clock -period 10.000 -name spw_clk -waveform {0.000 5.000]

## Clock Domain Crossings
set_clock_groups -asynchronous -group [get_clocks sys_clk] -group [get_clocks jesd_refclk]
set_clock_groups -asynchronous -group [get_clocks sys_clk] -group [get_clocks ddc_clk]
set_clock_groups -asynchronous -group [get_clocks sys_clk] -group [get_clocks spw_clk]

## False Paths
set_false_path -from [get_ports sys_rst_n]
set_false_path -to [get_ports led_*]

## JESD204C Constraints
# Lane-to-lane skew < 5 ps
set_max_delay 0.005 -from [get_cells u_jesd204c_receiver/u_phy/gty_channel_*] -to [get_cells u_jesd204c_receiver/u_phy/gty_channel_*]

# SYSREF to device clock setup/hold
set_setup_time 0.100 -to [get_ports jesd_sysref]
set_hold_time 0.100 -to [get_ports jesd_sysref]

## I/O Standards
# LVDS for differential signals
set_property IOSTANDARD LVDS [get_ports {jesd_refclk_*}]
set_property IOSTANDARD LVDS [get_ports {jesd_tx_p[*]}]
set_property IOSTANDARD LVDS [get_ports {jesd_rx_p[*]}]
set_property IOSTANDARD LVDS [get_ports {jesd_sysref}]

# LVCMOS 3.3V for single-ended
set_property IOSTANDARD LVCMOS33 [get_ports {sys_clk}]
set_property IOSTANDARD LVCMOS33 [get_ports {sys_rst_n}]
set_property IOSTANDARD LVCMOS33 [get_ports {led_*}]
set_property IOSTANDARD LVCMOS33 [get_ports {uart_*}]
set_property IOSTANDARD LVCMOS33 [get_ports {spi_*}]

# LVCMOS 1.8V for SpaceWire
set_property IOSTANDARD LVCMOS18 [get_ports {spw0_*}]
set_property IOSTANDARD LVCMOS18 [get_ports {spw1_*}]

## Pin Assignments
# System
set_property PACKAGE_PIN H19 [get_ports sys_clk]
set_property PACKAGE_PIN G19 [get_ports sys_rst_n]

# JESD204C (GTY banks 64-65)
set_property PACKAGE_PIN A10 [get_ports {jesd_refclk_p}]
set_property PACKAGE_PIN A9 [get_ports {jesd_refclk_n}]

# LEDs
set_property PACKAGE_PIN E18 [get_ports led_power]
set_property PACKAGE_PIN E17 [get_ports led_fpga_done]
set_property PACKAGE_PIN D18 [get_ports led_error]
set_property PACKAGE_PIN D17 [get_ports led_heartbeat]

# UART
set_property PACKAGE_PIN C18 [get_ports uart_tx]
set_property PACKAGE_PIN C17 [get_ports uart_rx]

# SPI (to LMK04832-SP)
set_property PACKAGE_PIN B18 [get_ports spi_lmk_mosi]
set_property PACKAGE_PIN B17 [get_ports spi_lmk_miso]
set_property PACKAGE_PIN A18 [get_ports spi_lmk_sclk]
set_property PACKAGE_PIN A17 [get_ports spi_lmk_cs_n]

# SPI (to TPS7H3014-SP)
set_property PACKAGE_PIN D16 [get_ports spi_pwr_mosi]
set_property PACKAGE_PIN C16 [get_ports spi_pwr_miso]
set_property PACKAGE_PIN E16 [get_ports spi_pwr_sclk]
set_property PACKAGE_PIN D15 [get_ports spi_pwr_cs_n]

## Configuration
set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]
set_property CONFIG_MODE SPIx4 [current_design]
set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design]

## Unused Pins
set_property PACKAGE_PIN F19 [get_ports {gpio[0]}]
set_property PACKAGE_PIN F18 [get_ports {gpio[1]}]
set_property PACKAGE_PIN G18 [get_ports {gpio[2]}]
set_property PACKAGE_PIN G17 [get_ports {gpio[3]}]
set_property PACKAGE_PIN H17 [get_ports {gpio[4]}]
set_property PACKAGE_PIN H16 [get_ports {gpio[5]}]
set_property PACKAGE_PIN J17 [get_ports {gpio[6]}]
set_property PACKAGE_PIN J16 [get_ports {gpio[7]}]

## Power Nets
set_property PACKAGE_PIN L19 [get_ports VCCINT]
set_property PACKAGE_PIN K19 [get_ports VCCINT]
set_property PACKAGE_PIN M19 [get_ports VCCAUX]
set_property PACKAGE_PIN M18 [get_ports VCCAUX]

## Bitstream Settings
set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
set_property BITSTREAM.CONFIG.PERSIST NO [current_design]
