import logging
from datetime import datetime, timedelta
from typing import Any

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

from .homeassistant_historical_sensor import (
    HistoricalSensor,
    HistoricalState,
    PollUpdateMixin,
)

from .const import DOMAIN, NAME, PLATFORM

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


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
):
    """Set up the sensor platform."""
    sensor = WaterUsageSensor(hass, config_entry)
    async_add_devices([sensor])

    # Store sensor instance for input entities to access
    hass.data[DOMAIN][config_entry.entry_id]["sensor"] = sensor
