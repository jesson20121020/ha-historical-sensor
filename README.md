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

You can add data programmatically using these services:

#### Add Single Data Point
```yaml
service: home_water_usage.add_water_usage
data:
  year_month: "2024-01"
  usage: 25.5
```

#### Set Historical Data (Node-RED Compatible)
```yaml
service: home_water_usage.set_historical_data
data:
  data_points:
    - year_month: "2023-12"
      usage: 22.3
    - year_month: "2024-01"
      usage: 18.7
    - year_month: "2024-02"
      usage: 31.2
```

### Node-RED Integration

For Node-RED users, you can use the provided flow example or create a custom flow:

#### Quick Start with Example Flow

1. **Import the flow**: Import `node-red-flow-example.json` into your Node-RED
2. **Configure the HTTP Request node**:
   - Update URL to your HA IP: `http://your-ha-ip:8123/api/services/home_water_usage/set_historical_data`
   - Add your HA token: `Authorization: Bearer YOUR_LONG_LIVED_ACCESS_TOKEN`
3. **Deploy and test**: Click the inject node to send sample data

#### Custom Flow Setup

1. **HTTP Request Node**:
   - Method: POST
   - URL: `http://your-ha-ip:8123/api/services/home_water_usage/set_historical_data`
   - Headers: `Authorization: Bearer YOUR_LONG_LIVED_ACCESS_TOKEN`
   - Content-Type: `application/json`

2. **Payload Example**:
```json
{
  "data_points": [
    {"year_month": "2023-12", "usage": 22.3},
    {"year_month": "2024-01", "usage": 18.7},
    {"year_month": "2024-02", "usage": 31.2},
    {"year_month": "2024-03", "usage": 25.8}
  ]
}
```

3. **Trigger Options**:
   - Inject node for manual updates
   - Schedule node for periodic updates
   - MQTT/Webhook triggers for external data sources

This provides a simple way to integrate with external data sources through Node-RED.

## Requirements

- Home Assistant 2025.12.0 or later

## Technical Details

This integration uses the `homeassistant-historical-sensor` library to provide historical water usage statistics to Home Assistant's energy dashboard. The integration stores usage data persistently and calculates cumulative statistics for long-term tracking.

## License

This integration is licensed under the MIT License.
