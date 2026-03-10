"""Sensor platform for Luxembourg Spritpreise."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_VEHICLE_NAME,
    CONF_TANK_SIZE,
    ATTR_PRICE,
    ATTR_PREVIOUS_PRICE,
    ATTR_DIFF,
    ATTR_DIFF_PCT,
    ATTR_TANK_COST,
    ATTR_TANK_DIFF,
    ATTR_ARTICLE_TITLE,
    ATTR_ARTICLE_LINK,
    ATTR_ARTICLE_DATE,
    ATTR_LAST_CHECK,
    ATTR_STATUS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    vehicle_name = entry.data[CONF_VEHICLE_NAME]
    tank_size = entry.data[CONF_TANK_SIZE]

    async_add_entities([
        SP95PriceSensor(coordinator, entry, vehicle_name, tank_size),
    ])


class SP95PriceSensor(CoordinatorEntity, SensorEntity):
    """Main sensor: SP95 price with all calculated attributes."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "€/L"
    _attr_icon = "mdi:gas-station"
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, vehicle_name: str, tank_size: int) -> None:
        super().__init__(coordinator)
        self._vehicle_name = vehicle_name
        self._tank_size = tank_size
        self._entry = entry
        self._previous_price: float | None = None

        slug = vehicle_name.lower().replace(" ", "_")
        self._attr_unique_id = f"{DOMAIN}_{slug}_sp95_price"
        self._attr_name = f"SP95 Preis"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._vehicle_name,
            manufacturer="Luxembourg Spritpreise",
            model="lesfrontaliers.lu RSS",
            entry_type="service",
        )

    @property
    def native_value(self) -> float | None:
        """Current SP95 price."""
        return self.coordinator.data.get("price")

    @property
    def extra_state_attributes(self) -> dict:
        """All calculated attributes for the Lovelace card."""
        data = self.coordinator.data or {}
        current = data.get("price")

        # Track previous price across updates
        if current and self._previous_price is None:
            self._previous_price = current

        prev = self._previous_price
        diff = round(current - prev, 3) if (current and prev) else None
        diff_pct = round(((current - prev) / prev) * 100, 1) if (current and prev and prev > 0) else None
        tank_size = self._entry.data.get(CONF_TANK_SIZE, self._tank_size)
        tank_cost = round(current * tank_size, 2) if current else None
        tank_diff = round(diff * tank_size, 2) if diff is not None else None

        # Update previous price after calculation
        if current and current != prev:
            self._previous_price = current

        return {
            ATTR_PRICE: current,
            ATTR_PREVIOUS_PRICE: prev,
            ATTR_DIFF: diff,
            ATTR_DIFF_PCT: diff_pct,
            ATTR_TANK_COST: tank_cost,
            ATTR_TANK_DIFF: tank_diff,
            ATTR_ARTICLE_TITLE: data.get("title"),
            ATTR_ARTICLE_LINK: data.get("link"),
            ATTR_ARTICLE_DATE: data.get("pub_date"),
            ATTR_LAST_CHECK: data.get("last_check"),
            ATTR_STATUS: data.get("status"),
            "vehicle_name": self._vehicle_name,
            "tank_size": tank_size,
            "trend": self._trend(diff),
        }

    def _trend(self, diff: float | None) -> str:
        if diff is None:
            return "unknown"
        if diff > 0.005:
            return "rising"
        if diff < -0.005:
            return "falling"
        return "stable"
