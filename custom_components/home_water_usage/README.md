# Home Water Usage Integration for Home Assistant

This integration allows you to manually track your home water usage and display it in Home Assistant's Energy dashboard.

## Features

- Manual entry of monthly water usage data
- Historical statistics for energy dashboard integration
- Persistent storage of usage data
- Input entities for easy data entry

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
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

## License

This integration is licensed under the MIT License.
