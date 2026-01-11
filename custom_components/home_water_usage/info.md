# Home Water Usage

[![GitHub Release](https://img.shields.io/github/release/your_username/ha-home-water-usage.svg)](https://github.com/your_username/ha-home-water-usage/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Manual water usage tracking integration for Home Assistant with energy dashboard support.

## Features

- Manual entry of monthly water usage
- Persistent data storage
- Historical statistics for energy dashboard
- Input entities for easy data entry
- HACS compatible

## Installation

### HACS

1. Add this repository as a custom repository in HACS
2. Search for "Home Water Usage" and install
3. Restart Home Assistant

### Manual

1. Copy the `custom_components/home_water_usage` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Usage

After installation, add the integration through Settings > Integrations.

The integration creates input entities for entering water usage data and a sensor that provides historical statistics for the energy dashboard.
