import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Home Water Usage from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    # Register services
    await _register_services(hass)

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def _register_services(hass: HomeAssistant):
    """Register integration services."""
    async def add_water_usage_service(call):
        """Service to add water usage data."""
        year_month = call.data.get("year_month")
        usage = call.data.get("usage")

        if not year_month or not usage:
            LOGGER.error("Missing year_month or usage parameter")
            return

        # Find sensor instance
        for entry_id, entry_data in hass.data[DOMAIN].items():
            sensor = entry_data.get("sensor")
            if sensor:
                sensor.add_water_usage(str(year_month), float(usage))
                await sensor.async_update_historical()
                await sensor.async_write_historical()
                break

    hass.services.async_register(DOMAIN, "add_water_usage", add_water_usage_service)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
