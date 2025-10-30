"""Virgin Media Router Status sensor platform."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
	CoordinatorEntity,
	DataUpdateCoordinator,
	UpdateFailed,
)

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

SENSOR_DESCRIPTIONS = [
	SensorEntityDescription(
		key="cable_modem_status",
		name="Cable Modem Status",
		icon="mdi:router-wireless",
	),
	SensorEntityDescription(
		key="primary_downstream_channel",
		name="Primary Downstream Channel",
		icon="mdi:download",
	),
	SensorEntityDescription(
		key="docsis_3_0_downstream",
		name="DOCSIS 3.0 Downstream Channels",
		icon="mdi:download-network",
	),
	SensorEntityDescription(
		key="docsis_3_0_upstream",
		name="DOCSIS 3.0 Upstream Channels",
		icon="mdi:upload-network",
	),
	SensorEntityDescription(
		key="docsis_3_1_downstream",
		name="DOCSIS 3.1 Downstream Channels",
		icon="mdi:download-network",
	),
	SensorEntityDescription(
		key="docsis_3_1_upstream",
		name="DOCSIS 3.1 Upstream Channels",
		icon="mdi:upload-network",
	),
]


class VirginMediaDataUpdateCoordinator(DataUpdateCoordinator):
	"""Class to manage fetching data from Virgin Media router."""

	def __init__(self, hass: HomeAssistant, host: str) -> None:
		"""Initialize."""
		super().__init__(
			hass,
			_LOGGER,
			name=DOMAIN,
			update_interval=SCAN_INTERVAL,
		)
		self.host = host

	async def _async_update_data(self) -> dict[str, Any]:
		"""Update data via library."""
		try:
			async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
				url = f"http://{self.host}"
				async with session.get(url) as response:
					if response.status != 200:
						raise UpdateFailed(f"Error communicating with router: {response.status}")
                    
					html = await response.text()
					return self._parse_status_page(html)
		except asyncio.TimeoutError as err:
			raise UpdateFailed(f"Timeout communicating with router at {self.host}") from err
		except aiohttp.ClientError as err:
			raise UpdateFailed(f"Error communicating with router: {err}") from err

	def _parse_status_page(self, html: str) -> dict[str, Any]:
		"""Parse the router status page HTML."""
		soup = BeautifulSoup(html, 'html.parser')
		data = {}
        
		try:
			# Look for table rows containing status information
			rows = soup.find_all('tr')
            
			for row in rows:
				cells = row.find_all(['td', 'th'])
				if len(cells) >= 2:
					key = cells[0].get_text(strip=True).lower()
					value = cells[1].get_text(strip=True)
                    
					# Map the status items to our sensor keys
					if "cable modem status" in key:
						data["cable_modem_status"] = value
					elif "primary downstream channel" in key:
						data["primary_downstream_channel"] = value
					elif "docsis 3.0 channels" in key and "downstream" in key:
						data["docsis_3_0_downstream"] = value
					elif "docsis 3.0 channels" in key and "upstream" in key:
						data["docsis_3_0_upstream"] = value
					elif "docsis 3.1 channels" in key and "downstream" in key:
						data["docsis_3_1_downstream"] = value
					elif "docsis 3.1 channels" in key and "upstream" in key:
						data["docsis_3_1_upstream"] = value

			# Alternative parsing method - look for specific text patterns
			if not data:
				text = soup.get_text()
				lines = text.split('\n')
                
				for i, line in enumerate(lines):
					line = line.strip()
					if "Cable Modem Status" in line and i + 1 < len(lines):
						next_line = lines[i + 1].strip()
						if next_line and "Online" in next_line:
							data["cable_modem_status"] = next_line
					elif "Primary downstream channel" in line and i + 1 < len(lines):
						next_line = lines[i + 1].strip()
						if next_line and "Locked" in next_line:
							data["primary_downstream_channel"] = next_line
					elif "DOCSIS 3.0 channels" in line:
						# Look for numbers in the next few lines
						for j in range(1, 4):
							if i + j < len(lines):
								check_line = lines[i + j].strip()
								if check_line.isdigit():
									if "docsis_3_0_downstream" not in data:
										data["docsis_3_0_downstream"] = check_line
									else:
										data["docsis_3_0_upstream"] = check_line
									break
					elif "DOCSIS 3.1 channels" in line:
						# Look for numbers in the next few lines
						for j in range(1, 4):
							if i + j < len(lines):
								check_line = lines[i + j].strip()
								if check_line.isdigit():
									if "docsis_3_1_downstream" not in data:
										data["docsis_3_1_downstream"] = check_line
									else:
										data["docsis_3_1_upstream"] = check_line
									break

			_LOGGER.debug("Parsed data: %s", data)
			return data
            
		except Exception as err:
			_LOGGER.error("Error parsing status page: %s", err)
			raise UpdateFailed(f"Error parsing status page: {err}") from err


async def async_setup_entry(
	hass: HomeAssistant,
	config_entry: ConfigEntry,
	async_add_entities: AddEntitiesCallback,
) -> None:
	"""Set up the Virgin Media Router Status sensors."""
	host = config_entry.data[CONF_HOST]
    
	coordinator = VirginMediaDataUpdateCoordinator(hass, host)
	await coordinator.async_config_entry_first_refresh()

	entities = []
	for description in SENSOR_DESCRIPTIONS:
		entities.append(VirginMediaSensor(coordinator, description))

	async_add_entities(entities)


class VirginMediaSensor(CoordinatorEntity, SensorEntity):
	"""Virgin Media Router Status sensor."""

	def __init__(
		self,
		coordinator: VirginMediaDataUpdateCoordinator,
		description: SensorEntityDescription,
	) -> None:
		"""Initialize the sensor."""
		super().__init__(coordinator)
		self.entity_description = description
		self._attr_unique_id = f"{DOMAIN}_{description.key}"
		self._attr_device_info = {
			"identifiers": {(DOMAIN, coordinator.host)},
			"name": "Virgin Media Router",
			"manufacturer": "Virgin Media/ARRIS",
			"model": "Cable Modem",
		}

	@property
	def native_value(self) -> str | None:
		"""Return the state of the sensor."""
		return self.coordinator.data.get(self.entity_description.key)

	@property
	def available(self) -> bool:
		"""Return if entity is available."""
		return self.coordinator.last_update_success and self.native_value is not None
