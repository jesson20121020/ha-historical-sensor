import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.input_number import InputNumber
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.statistics import StatisticsRow
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import DiscoveryInfoType
from homeassistant.util import dt as dtutil

from ..homeassistant_historical_sensor import (
    HistoricalSensor,
    HistoricalState,
    PollUpdateMixin,
)

from ..const import DOMAIN, NAME, PLATFORM

LOGGER = logging.getLogger(__name__)

STORAGE_KEY = f"{DOMAIN}_data"
STORAGE_VERSION = 1


class WaterUsageSensor(PollUpdateMixin, HistoricalSensor, SensorEntity):
    """Water usage historical sensor."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        super().__init__()

        self.hass = hass
        self.config_entry = config_entry

        self._attr_has_entity_name = True
        self._attr_name = NAME
        self._attr_unique_id = f"{PLATFORM}.{DOMAIN}"
        self._attr_entity_id = f"{PLATFORM}.{DOMAIN}"
        self._attr_device_class = SensorDeviceClass.WATER
        self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS

        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, float] = {}  # year_month -> usage

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        await self._load_data()

    async def _load_data(self) -> None:
        """Load stored water usage data."""
        data = await self._store.async_load()
        if data:
            self._data = data.get("usage_data", {})
        else:
            self._data = {}

    async def _save_data(self) -> None:
        """Save water usage data."""
        await self._store.async_save({"usage_data": self._data})

    def add_water_usage(self, year_month: str, usage: float) -> None:
        """Add water usage for a specific year-month."""
        self._data[year_month] = usage
        # Save data asynchronously
        self.hass.async_create_task(self._save_data())

    async def async_update_historical(self) -> None:
        """Update historical states from stored data."""
        historical_states = []

        for year_month, usage in self._data.items():
            try:
                # Parse year_month (format: "2024-01")
                year, month = map(int, year_month.split('-'))

                # Create timestamp for the end of the month
                if month == 12:
                    end_of_month = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_of_month = datetime(year, month + 1, 1) - timedelta(days=1)

                # Convert to timestamp
                timestamp = dtutil.as_utc(end_of_month).timestamp()

                historical_states.append(
                    HistoricalState(state=usage, timestamp=timestamp)
                )
            except ValueError:
                LOGGER.warning(f"Invalid year_month format: {year_month}")

        self._attr_historical_states = sorted(historical_states, key=lambda x: x.timestamp)

    def get_statistic_metadata(self) -> StatisticMetaData:
        """Return statistic metadata."""
        meta = super().get_statistic_metadata()
        meta["has_sum"] = True
        return meta

    async def async_calculate_statistic_data(
        self, hist_states: list[HistoricalState], *, latest: StatisticsRow | None = None
    ) -> list[StatisticData]:
        """Calculate statistic data from historical states."""
        accumulated = latest["sum"] if latest else 0

        ret = []
        for state in hist_states:
            accumulated += state.state

            dt = datetime.fromtimestamp(state.timestamp, tz=dtutil.UTC)

            ret.append(
                StatisticData(
                    start=dt,
                    state=state.state,
                    sum=accumulated,
                )
            )

        return ret


class WaterUsageInput(InputNumber):
    """Input number for water usage entry."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        config = {
            "name": f"{NAME} - Monthly Usage",
            "min": 0,
            "max": 1000,
            "step": 0.1,
            "unit_of_measurement": "m³",
            "mode": "box",
            "editable": True,
            "id": f"input_number.{DOMAIN}_usage",
            "unique_id": f"input_number.{DOMAIN}_usage",
        }
        super().__init__(config)
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
        config = {
            "name": f"{NAME} - Year-Month",
            "min": 202001,  # 2020-01
            "max": (current_year + 1) * 100 + 12,  # Next year December
            "step": 1,
            "mode": "box",
            "editable": True,
            "id": f"input_number.{DOMAIN}_year_month",
            "unique_id": f"input_number.{DOMAIN}_year_month",
        }
        super().__init__(config)
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
    """Set up the sensor platform."""
    sensor = WaterUsageSensor(hass, config_entry)

    async_add_devices([sensor])

    # Store sensor instance
    hass.data[DOMAIN][config_entry.entry_id]["sensor"] = sensor

    # Create input_number entities via service calls
    await _create_input_entities(hass, config_entry)


async def _create_input_entities(hass: HomeAssistant, config_entry: ConfigEntry):
    """Create input_number entities using HA services."""
    try:
        # Create water usage input
        await hass.services.async_call(
            "input_number",
            "create",
            {
                "obj_id": f"{DOMAIN}_usage",
                "name": f"{NAME} - Monthly Usage",
                "min": 0,
                "max": 1000,
                "step": 0.1,
                "unit_of_measurement": "m³",
                "mode": "box",
                "editable": True,
            }
        )

        # Create year-month input
        current_year = datetime.now().year
        await hass.services.async_call(
            "input_number",
            "create",
            {
                "obj_id": f"{DOMAIN}_year_month",
                "name": f"{NAME} - Year-Month",
                "min": 202001,
                "max": (current_year + 1) * 100 + 12,
                "step": 1,
                "mode": "box",
                "editable": True,
            }
        )

        # Set up automation to handle input changes
        await _setup_input_automation(hass, config_entry)

    except Exception as e:
        LOGGER.error(f"Failed to create input entities: {e}")


async def _setup_input_automation(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up automation to handle input number changes."""
    automation_config = {
        "alias": f"{NAME} - Data Input Handler",
        "trigger": [
            {
                "platform": "state",
                "entity_id": f"input_number.{DOMAIN}_year_month"
            }
        ],
        "condition": [
            {
                "condition": "and",
                "conditions": [
                    {
                        "condition": "template",
                        "value_template": "{{ states('input_number.home_water_usage_year_month') | int > 0 }}"
                    },
                    {
                        "condition": "template",
                        "value_template": "{{ states('input_number.home_water_usage_usage') | float > 0 }}"
                    }
                ]
            }
        ],
        "action": [
            {
                "service": f"{DOMAIN}.add_water_usage",
                "data": {
                    "year_month": "{{ states('input_number.home_water_usage_year_month') }}",
                    "usage": "{{ states('input_number.home_water_usage_usage') }}"
                }
            }
        ]
    }

    try:
        await hass.services.async_call("automation", "create", automation_config)
    except Exception as e:
        LOGGER.error(f"Failed to create automation: {e}")
