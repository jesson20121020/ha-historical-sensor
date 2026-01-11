# Home Water Usage Integration

[![GitHub Release](https://img.shields.io/github/release/jesson20121020/ha-historical-sensor.svg)](https://github.com/jesson20121020/ha-historical-sensor/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Manual water usage tracking integration for Home Assistant with energy dashboard support.

## Features

- Manual entry of monthly water usage data
- Historical statistics for energy dashboard integration
- Persistent data storage using HA Store
- Input entities for easy data entry
- HACS compatible

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS:
   ```
   https://github.com/jesson20121020/ha-historical-sensor
   ```
2. Search for "Home Water Usage" and install
3. Restart Home Assistant
4. Add the integration through Settings > Integrations

### Manual Installation

1. Copy the `custom_components/home_water_usage` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Add the integration through Settings > Integrations

## Configuration

After installation, add the "Home Water Usage" integration through the Home Assistant UI.

## Usage

1. The integration creates:
   - A sensor entity that provides historical water usage statistics
   - Two input number entities for data entry:
     - "Home Water Usage - Monthly Usage": Enter the water usage in cubic meters
     - "Home Water Usage - Year-Month": Enter the year and month in YYYYMM format (e.g., 202401 for January 2024)

2. To add water usage data:
   - Set the monthly usage value in the "Monthly Usage" input
   - Set the year-month in the "Year-Month" input
   - The data will be automatically saved and statistics updated

3. The sensor will appear in the Energy dashboard under water consumption

## Requirements

- Home Assistant 2025.12.0 or later
- `homeassistant-historical-sensor` library

## Technical Details

This integration uses the `homeassistant-historical-sensor` library to provide historical water usage statistics to Home Assistant's energy dashboard. The integration stores usage data persistently and calculates cumulative statistics for long-term tracking.

## License

This integration is licensed under the MIT License.
