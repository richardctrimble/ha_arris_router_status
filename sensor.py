"""Arris Router Status sensor platform."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp
import json

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
	CoordinatorEntity,
	DataUpdateCoordinator,
	UpdateFailed,
)
from homeassistant.helpers.entity import EntityCategory

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

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
		key="docsis_version",
		name="DOCSIS Version",
		icon="mdi:network",
	),
	SensorEntityDescription(
		key="cable_modem_registration",
		name="Cable Modem Registration",
		icon="mdi:check-network",
	),
	SensorEntityDescription(
		key="wan_ip_provision_mode",
		name="WAN IP Provision Mode",
		icon="mdi:ip-network",
	),
	SensorEntityDescription(
		key="fail_safe_mode",
		name="Fail Safe Mode",
		icon="mdi:alert-circle",
	),
	SensorEntityDescription(
		key="no_rf_detected",
		name="No RF Detected",
		icon="mdi:antenna",
	),
	SensorEntityDescription(
		key="docsis_3_0_downstream",
		name="DOCSIS 3.0 Downstream Channels",
		icon="mdi:download-network",
		native_unit_of_measurement="channels",
	),
	SensorEntityDescription(
		key="docsis_3_0_upstream",
		name="DOCSIS 3.0 Upstream Channels",
		icon="mdi:upload-network",
		native_unit_of_measurement="channels",
	),
	SensorEntityDescription(
		key="docsis_3_1_downstream",
		name="DOCSIS 3.1 Downstream Channels",
		icon="mdi:download-network",
		native_unit_of_measurement="channels",
	),
	SensorEntityDescription(
		key="docsis_3_1_upstream",
		name="DOCSIS 3.1 Upstream Channels",
		icon="mdi:upload-network",
		native_unit_of_measurement="channels",
	),
	SensorEntityDescription(
		key="total_downstream_channels",
		name="Total Downstream Channels",
		icon="mdi:download-multiple",
		native_unit_of_measurement="channels",
	),
	SensorEntityDescription(
		key="total_upstream_channels",
		name="Total Upstream Channels",
		icon="mdi:upload-multiple",
		native_unit_of_measurement="channels",
	),
	SensorEntityDescription(
		key="last_update_time",
		name="Last Update Time",
		icon="mdi:clock-outline",
		device_class=SensorDeviceClass.TIMESTAMP,
		entity_category=EntityCategory.DIAGNOSTIC,
	),
	SensorEntityDescription(
		key="isp_provider",
		name="ISP Provider",
		icon="mdi:account-network",
	),
	SensorEntityDescription(
		key="network_access",
		name="Network Access",
		icon="mdi:network",
	),
	SensorEntityDescription(
		key="max_cpes",
		name="Maximum Number of CPEs",
		icon="mdi:devices",
	),
	SensorEntityDescription(
		key="baseline_privacy",
		name="Baseline Privacy",
		icon="mdi:shield",
	),
	SensorEntityDescription(
		key="docsis_mode",
		name="DOCSIS Mode",
		icon="mdi:network",
	),
	SensorEntityDescription(
		key="config_file",
		name="Config File",
		icon="mdi:file-document",
	),
	SensorEntityDescription(
		key="primary_downstream_sfid",
		name="Primary Downstream SFID",
		icon="mdi:download",
	),
	SensorEntityDescription(
		key="primary_downstream_max_traffic_rate",
		name="Primary Downstream Max Traffic Rate",
		icon="mdi:download",
	),
	SensorEntityDescription(
		key="primary_downstream_max_traffic_burst",
		name="Primary Downstream Max Traffic Burst",
		icon="mdi:download",
	),
	SensorEntityDescription(
		key="primary_downstream_min_traffic_rate",
		name="Primary Downstream Min Traffic Rate",
		icon="mdi:download",
	),
	SensorEntityDescription(
		key="primary_upstream_sfid",
		name="Primary Upstream SFID",
		icon="mdi:upload",
	),
	SensorEntityDescription(
		key="primary_upstream_max_traffic_rate",
		name="Primary Upstream Max Traffic Rate",
		icon="mdi:upload",
	),
	SensorEntityDescription(
		key="primary_upstream_max_traffic_burst",
		name="Primary Upstream Max Traffic Burst",
		icon="mdi:upload",
	),
	SensorEntityDescription(
		key="primary_upstream_min_traffic_rate",
		name="Primary Upstream Min Traffic Rate",
		icon="mdi:upload",
	),
	SensorEntityDescription(
		key="primary_upstream_max_concatenated_burst",
		name="Primary Upstream Max Concatenated Burst",
		icon="mdi:upload",
	),
	SensorEntityDescription(
		key="primary_upstream_scheduling_type",
		name="Primary Upstream Scheduling Type",
		icon="mdi:upload",
	),
]


class ArrisDataUpdateCoordinator(DataUpdateCoordinator):
	"""Class to manage fetching data from Arris router."""

	def __init__(self, hass: HomeAssistant, host: str, scan_interval: int) -> None:
		"""Initialize."""
		super().__init__(
			hass,
			_LOGGER,
			name=DOMAIN,
			update_interval=timedelta(seconds=scan_interval),
		)
		self.host = host

	async def _async_update_data(self) -> dict[str, Any]:
		"""Update data via library."""
		try:
			async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
				data: dict[str, Any] = {}

				# 1) Try the connection_troubleshoot_data endpoint which provides simple modem state
				try:
					ct_url = f"http://{self.host}/php/connection_troubleshoot_data.php"
					payload = {"userData": json.dumps({"connectionData": ""})}
					async with session.post(ct_url, data=payload) as resp:
						if resp.status == 200:
							try:
								json_data = await resp.json()
								_LOGGER.debug("connection_troubleshoot_data returned: %s", json_data)
								# Common keys: js_cm_oper_value, js_cm_reg_value, js_NoRF_Detected, js_wan_ip_prov_mode
								if isinstance(json_data, dict):
									oper = json_data.get("js_cm_oper_value")
									reg = json_data.get("js_cm_reg_value")
									wan_ip_mode = json_data.get("js_wan_ip_prov_mode")
									fail_safe = json_data.get("js_fail_safe_mode")
									no_rf = json_data.get("js_NoRF_Detected")

									# Simple human readable mapping for operational status
									if oper is not None:
										try:
											oper_val = int(oper)
											if oper_val >= 3:
												data["cable_modem_status"] = "Online"
											else:
												data["cable_modem_status"] = "Offline"
										except (ValueError, TypeError):
											data["cable_modem_status"] = str(oper)

									# Registration status mapping
									if reg is not None:
										try:
											reg_val = int(reg)
											reg_map = {
												0: "Unregistered",
												1: "Other",
												2: "Registered",
												3: "Not Registered",
												4: "Registration Complete",
												5: "Access Denied",
												6: "Operational",
											}
											data["cable_modem_registration"] = reg_map.get(reg_val, f"Unknown ({reg_val})")
										except (ValueError, TypeError):
											data["cable_modem_registration"] = str(reg)

									# WAN IP provision mode mapping
									if wan_ip_mode is not None:
										try:
											mode_val = int(wan_ip_mode)
											mode_map = {
												0: "DHCP",
												1: "Static",
												2: "PPPoE",
											}
											data["wan_ip_provision_mode"] = mode_map.get(mode_val, f"Unknown ({mode_val})")
										except (ValueError, TypeError):
											data["wan_ip_provision_mode"] = str(wan_ip_mode)

									# Fail safe mode
									if fail_safe is not None:
										data["fail_safe_mode"] = "Active" if str(fail_safe) == "1" else "Inactive"

									# No RF detected
									if no_rf is not None:
										data["no_rf_detected"] = "Yes" if str(no_rf) == "1" else "No"

							except (ValueError, KeyError, TypeError) as err:
								_LOGGER.debug("Error parsing connection_troubleshoot_data JSON: %s", err)
						else:
							_LOGGER.debug("%s returned HTTP %s", ct_url, resp.status)
				except (aiohttp.ClientError, asyncio.TimeoutError) as err:
					_LOGGER.debug("Error calling connection_troubleshoot_data: %s", err)

				# 2) Try ajaxGet_device_networkstatus_data.php - contains all status and config data
				try:
					dn_url = f"http://{self.host}/php/ajaxGet_device_networkstatus_data.php"
					payload = {"userData": json.dumps({"networkStatusData": ""})}
					async with session.post(dn_url, data=payload) as resp:
						_LOGGER.debug("ajaxGet_device_networkstatus_data.php status: %s", resp.status)
						if resp.status == 200:
							# This endpoint returns JSON array with all the data we need
							j = await resp.json()
							_LOGGER.debug("ajaxGet_device_networkstatus_data returned JSON array with length: %s", len(j) if hasattr(j, '__len__') else 'N/A')
							_LOGGER.debug("Full JSON response: %s", j)
							try:
								if isinstance(j, list) and len(j) >= 30:
									_LOGGER.debug("JSON array meets requirements (>=30 elements), extracting data")
									# Extract config and status data by index
									# Index mapping based on endpoint response
									data["primary_downstream_channel"] = j[2] if j[2] == "Locked" else None
									data["isp_provider"] = self._map_customer_id(j[4]) if isinstance(j[4], int) else None
									data["network_access"] = j[5]
									data["max_cpes"] = j[6]
									data["baseline_privacy"] = j[7]
									data["docsis_version"] = j[8]  # Also set as docsis_version for compatibility
									data["docsis_mode"] = j[8]
									data["config_file"] = j[9]
									data["primary_downstream_sfid"] = j[10]
									data["primary_downstream_max_traffic_rate"] = j[11]
									data["primary_downstream_max_traffic_burst"] = j[12]
									data["primary_downstream_min_traffic_rate"] = j[13]
									data["primary_upstream_sfid"] = j[14]
									data["primary_upstream_max_traffic_rate"] = j[15]
									data["primary_upstream_max_traffic_burst"] = j[16]
									data["primary_upstream_min_traffic_rate"] = j[17]
									data["primary_upstream_max_concatenated_burst"] = j[18]
									data["primary_upstream_scheduling_type"] = j[19]

									# Channel counts are provided directly at the end
									# Array indices: [25]=US 3.0, [26]=DS 3.0, [27]=DS 3.1, [28]=US 3.1
									if len(j) >= 29:
										upstream_3_0_count = int(j[25]) if str(j[25]).isdigit() else 0
										downstream_3_0_count = int(j[26]) if str(j[26]).isdigit() else 0
										downstream_3_1_count = int(j[27]) if str(j[27]).isdigit() else 0
										upstream_3_1_count = int(j[28]) if str(j[28]).isdigit() else 0

										data['docsis_3_0_downstream'] = downstream_3_0_count
										data['docsis_3_0_upstream'] = upstream_3_0_count
										data['docsis_3_1_downstream'] = downstream_3_1_count
										data['docsis_3_1_upstream'] = upstream_3_1_count
										data['total_downstream_channels'] = downstream_3_0_count + downstream_3_1_count
										data['total_upstream_channels'] = upstream_3_0_count + upstream_3_1_count
									else:
										_LOGGER.warning("JSON array too short for channel counts (need >=29, got %s)", len(j))
								else:
									_LOGGER.warning("JSON response is not a list or too short (need >=30 elements, got type=%s, len=%s)", 
													type(j).__name__, len(j) if hasattr(j, '__len__') else 'N/A')

							except (ValueError, KeyError, TypeError, IndexError) as err:
								_LOGGER.error("Error parsing ajaxGet_device_networkstatus_data JSON: %s", err)
						else:
							_LOGGER.warning("%s returned HTTP %s", dn_url, resp.status)
				except (aiohttp.ClientError, asyncio.TimeoutError) as err:
					_LOGGER.debug("Error calling ajaxGet_device_networkstatus_data: %s", err)

			# Store the last update time in UTC with timezone info
			data["last_update_time"] = datetime.now(timezone.utc)

			_LOGGER.debug("Data dictionary contains %d keys", len(data))
			return data
		except asyncio.TimeoutError as err:
				raise UpdateFailed(f"Timeout communicating with router at {self.host}") from err
		except aiohttp.ClientError as err:
				raise UpdateFailed(f"Error communicating with router: {err}") from err

	def _map_customer_id(self, customer_id: int) -> str:
		"""Map customer ID to ISP provider name."""
		provider_map = {
			6: "Virgin Media (VTR)",
			8: "Virgin Media",
			20: "Ziggo",
			41: "Virgin Media Ireland",
			44: "Telekom Austria",
			50: "Yallo",
			51: "Sunrise",
		}
		return provider_map.get(customer_id, f"Unknown ISP ID={customer_id}")


async def async_setup_entry(
	hass: HomeAssistant,
	config_entry: ConfigEntry,
	async_add_entities: AddEntitiesCallback,
) -> None:
	"""Set up the Arris Router Status sensors."""
	host = config_entry.data[CONF_HOST]
	scan_interval = config_entry.options.get(
		CONF_SCAN_INTERVAL, config_entry.data.get(CONF_SCAN_INTERVAL, 30)
	)
    
	coordinator = ArrisDataUpdateCoordinator(hass, host, scan_interval)
	await coordinator.async_config_entry_first_refresh()

	entities = []
	for description in SENSOR_DESCRIPTIONS:
		try:
			sensor = ArrisSensor(coordinator, description)
			entities.append(sensor)
			_LOGGER.debug("Created sensor: %s (category: %s)", description.key, 
						 description.entity_category.value if description.entity_category else "default")
		except Exception as err:
			_LOGGER.error("Failed to create sensor %s: %s", description.key, err)

	_LOGGER.info("Created %d total sensors", len(entities))
	async_add_entities(entities)

	async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
		"""Update options."""
		await hass.config_entries.async_reload(entry.entry_id)

	config_entry.async_on_unload(
		config_entry.add_update_listener(async_update_options)
	)


class ArrisSensor(CoordinatorEntity, SensorEntity):
	"""Arris Router Status sensor."""

	def __init__(
		self,
		coordinator: ArrisDataUpdateCoordinator,
		description: SensorEntityDescription,
	) -> None:
		"""Initialize the sensor."""
		super().__init__(coordinator)
		self.entity_description = description
		self._attr_unique_id = f"{DOMAIN}_{description.key}"
		self._attr_device_info = {
			"identifiers": {(DOMAIN, coordinator.host)},
			"name": "Arris Router",
			"manufacturer": "ARRIS",
			"model": "Cable Modem",
		}
		if description.entity_category:
			self._attr_entity_category = description.entity_category

	@property
	def native_value(self) -> str | int | datetime | None:
		"""Return the state of the sensor."""
		value = self.coordinator.data.get(self.entity_description.key)
		# For timestamp sensors, return the datetime object directly
		if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP and isinstance(value, datetime):
			return value
		return value

	@property
	def available(self) -> bool:
		"""Return if entity is available."""
		is_available = self.coordinator.last_update_success and self.native_value is not None
		if not is_available:
			_LOGGER.debug("Sensor %s unavailable: last_update_success=%s, native_value=%s", 
						 self.entity_description.key, self.coordinator.last_update_success, self.native_value)
		return is_available