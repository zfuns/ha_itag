from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from . import DOMAIN
from .coordinator import ITagClient

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities):
    mac = entry.data["mac"].upper()
    store = hass.data[DOMAIN]
    clients = store.setdefault("clients", {})
    client: ITagClient | None = clients.get(mac)
    if client is None:
        client = clients[mac] = ITagClient(hass, mac)
    async_add_entities([ITagBattery(mac, client),ITagRssi(mac, client)])

class ITagBattery(SensorEntity):
    _attr_name = "iTag Battery"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_should_poll = True

    def __init__(self, mac: str, client: ITagClient):
        self._mac = mac
        self._client = client
        self._attr_unique_id = f"itag_batt_{mac.replace(':','_')}_v2"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._mac)},
            name=f"iTag {self._mac}",
        )

    async def async_update(self):
        try:
            val = await self._client.read_battery()
        except Exception:
            val = None
        if val is not None:
            self._attr_native_value = val

#下面全部ai添加的信号功能
class ITagRssi(SensorEntity):
    _attr_name = "iTag RSSI"
    _attr_native_unit_of_measurement = "dBm"
    _attr_should_poll = True

    def __init__(self, mac: str, client: ITagClient):
        self._mac = mac
        self._client = client
        self._attr_unique_id = f"itag_rssi_{mac.replace(':','_')}_v2"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._mac)},
            name=f"iTag {self._mac}",
        )

    async def async_update(self):
        self._attr_native_value = getattr(self._client, "last_rssi", None)

