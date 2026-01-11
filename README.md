# Home Water Usage Integration

[![GitHub Release](https://img.shields.io/github/release/jesson20121020/ha-historical-sensor.svg)](https://github.com/jesson20121020/ha-historical-sensor/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

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

### Setup Input Entities

First, create the following input entities in your HA configuration (via YAML or UI):

#### Option 1: Via YAML (configuration.yaml)
```yaml
input_number:
  home_water_usage_usage:
    name: "Home Water Usage - Monthly Usage"
    min: 0
    max: 1000
    step: 0.1
    unit_of_measurement: "m³"
    mode: box

  home_water_usage_year_month:
    name: "Home Water Usage - Year-Month"
    min: 202001
    max: 202512
    step: 1
    mode: box
```

#### Option 2: Via HA UI
1. Go to Settings > Devices & Services > Helpers
2. Click "Add Helper" > "Number"
3. Create two number helpers with the specifications above

### Using the Integration

1. **Automatic Sample Data**: The integration automatically generates 12 months of sample water usage data (15-35 m³ per month) for testing purposes.

2. The integration creates:
   - `sensor.home_water_usage`: Historical water usage statistics sensor with sample data

3. **Optional Manual Data Entry** (after setting up input entities):
   - Set the monthly usage value in `input_number.home_water_usage_usage`
   - Set the year-month in `input_number.home_water_usage_year_month` (format: YYYYMM)
   - Or use the service `home_water_usage.add_water_usage` with parameters:
     - `year_month`: Year-month string (e.g., "2024-01")
     - `usage`: Water usage in cubic meters

4. The sensor will appear in the Energy dashboard under water consumption with historical data visible immediately.

### Service Usage

You can also add data programmatically using the service:

```yaml
service: home_water_usage.add_water_usage
data:
  year_month: "2024-01"
  usage: 25.5
```

## Requirements

- Home Assistant 2025.12.0 or later

## Technical Details

This integration uses the `homeassistant-historical-sensor` library to provide historical water usage statistics to Home Assistant's energy dashboard. The integration stores usage data persistently and calculates cumulative statistics for long-term tracking.

## License

This integration is licensed under the MIT License.
