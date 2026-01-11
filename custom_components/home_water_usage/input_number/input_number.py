from datetime import datetime

from homeassistant.components.input_number import InputNumber
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import DiscoveryInfoType

from ..const import DOMAIN, NAME


class WaterUsageInput(InputNumber):
    """Input number for water usage entry."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        super().__init__(
            {
                "name": f"{NAME} - Monthly Usage",
                "min": 0,
                "max": 1000,
                "step": 0.1,
                "unit_of_measurement": "m³",
                "mode": "box",
                "unique_id": f"input_number.{DOMAIN}_usage",
                "entity_id": f"input_number.{DOMAIN}_usage",
            }
        )
        self.hass = hass
        self.config_entry = config_entry
        self._sensor = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        # Get sensor instance
        self._sensor = self.hass.data[DOMAIN][self.config_entry.entry_id].get("sensor")


class YearMonthInput(InputNumber):
    """Input number for year-month selection."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        current_year = datetime.now().year
        super().__init__(
            {
                "name": f"{NAME} - Year-Month",
                "min": 202001,  # 2020-01
                "max": (current_year + 1) * 100 + 12,  # Next year December
                "step": 1,
                "mode": "box",
                "unique_id": f"input_number.{DOMAIN}_year_month",
                "entity_id": f"input_number.{DOMAIN}_year_month",
            }
        )
        self.hass = hass
        self.config_entry = config_entry
        self._sensor = None
        self._usage_input = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        # Get sensor instance
        self._sensor = self.hass.data[DOMAIN][self.config_entry.entry_id].get("sensor")

        # Listen for state changes to trigger data saving
        async def _state_changed_listener(event):
            if self._sensor and self._usage_input:
                try:
                    year_month_int = int(self.state)
                    year = year_month_int // 100
                    month = year_month_int % 100

                    if 1 <= month <= 12:
                        year_month_str = f"{year:04d}-{month:02d}"
                        usage = float(self._usage_input.state)

                        self._sensor.add_water_usage(year_month_str, usage)
                        # Trigger historical update
                        await self._sensor.async_update_historical()
                        await self._sensor.async_write_historical()
                except (ValueError, AttributeError):
                    pass

        self.async_on_remove(
            self.hass.bus.async_listen("state_changed", _state_changed_listener)
        )

    def set_usage_input(self, usage_input):
        """Set reference to usage input entity."""
        self._usage_input = usage_input


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
):
    """Set up the input_number platform."""
    usage_input = WaterUsageInput(hass, config_entry)
    year_month_input = YearMonthInput(hass, config_entry)

    # Link inputs together
    year_month_input.set_usage_input(usage_input)

    async_add_devices([usage_input, year_month_input])

    # Store input instances
    hass.data[DOMAIN][config_entry.entry_id]["usage_input"] = usage_input
    hass.data[DOMAIN][config_entry.entry_id]["year_month_input"] = year_month_input
