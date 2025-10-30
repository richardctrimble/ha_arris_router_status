"""Arris Router Status sensor platform."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
import json
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
	SensorEntityDescription(
		key="total_downstream_channels",
		name="Total Downstream Channels",
		icon="mdi:download-multiple",
	),
	SensorEntityDescription(
		key="total_upstream_channels",
		name="Total Upstream Channels",
		icon="mdi:upload-multiple",
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
				# Get the main page to extract ISP provider and to allow JS-driven session state
				html_content = ""
				try:
					async with session.get(f"http://{self.host}/") as response:
						if response.status == 200:
							html_content = await response.text()
						else:
							_LOGGER.debug("Failed to get main page: HTTP %s", response.status)
				except Exception as e:
					_LOGGER.debug("Error getting main page: %s", e)

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
										except Exception:
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
										except Exception:
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
										except Exception:
											data["wan_ip_provision_mode"] = str(wan_ip_mode)

									# Fail safe mode
									if fail_safe is not None:
										data["fail_safe_mode"] = "Active" if str(fail_safe) == "1" else "Inactive"

									# No RF detected
									if no_rf is not None:
										data["no_rf_detected"] = "Yes" if str(no_rf) == "1" else "No"

									# Store raw values as attributes
									data["js_cm_oper_value"] = oper
									data["js_cm_reg_value"] = reg
									data["js_wan_ip_prov_mode"] = wan_ip_mode
									data["js_fail_safe_mode"] = fail_safe
									data["js_NoRF_Detected"] = no_rf
							except Exception as err:
								_LOGGER.debug("Error parsing connection_troubleshoot_data JSON: %s", err)
						else:
							_LOGGER.debug("%s returned HTTP %s", ct_url, resp.status)
				except Exception as err:
					_LOGGER.debug("Error calling connection_troubleshoot_data: %s", err)

				# 2) Try ajaxGet_device_networkstatus_data.php - contains all status and config data
				try:
					dn_url = f"http://{self.host}/php/ajaxGet_device_networkstatus_data.php"
					async with session.post(dn_url) as resp:
						if resp.status == 200:
							# This endpoint returns JSON array with all the data we need
							j = await resp.json()
							_LOGGER.debug("ajaxGet_device_networkstatus_data returned, len=%s", len(j) if hasattr(j, '__len__') else 'n')
							try:
								if isinstance(j, list) and len(j) >= 30:
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

							except Exception as err:
								_LOGGER.debug("Unexpected format from %s: %s", dn_url, err)
						else:
							_LOGGER.debug("%s returned HTTP %s", dn_url, resp.status)
				except Exception as err:
					_LOGGER.debug("Error calling ajaxGet_device_networkstatus_data: %s", err)

				return data
		except asyncio.TimeoutError as err:
				raise UpdateFailed(f"Timeout communicating with router at {self.host}") from err
		except aiohttp.ClientError as err:
				raise UpdateFailed(f"Error communicating with router: {err}") from err

	def _has_status_data(self, content: str) -> bool:
		"""Check if content contains status data."""
		status_indicators = ["Online", "DOCSIS", "Cable Modem", "Locked", "Downstream", "Upstream"]
		return any(indicator in content for indicator in status_indicators)

	def _parse_status_page(self, html: str, main_html: str = "") -> dict[str, Any]:
		"""Parse the router status page HTML."""
		soup = BeautifulSoup(html, 'html.parser')
		data = {}
        
		try:
			_LOGGER.debug("Parsing HTML content (first 1000 chars): %s", html[:1000])
			
			# Look for table rows containing status information
			rows = soup.find_all('tr')
			_LOGGER.debug("Found %d table rows", len(rows))
            
			for row in rows:
				cells = row.find_all(['td', 'th'])
				if len(cells) >= 2:
					key = cells[0].get_text(strip=True).lower()
					value = cells[1].get_text(strip=True)
					_LOGGER.debug("Found table row: %s = %s", key, value)
                    
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

			# Try alternative parsing methods
			if not any(k in data for k in ["cable_modem_status", "primary_downstream_channel", "docsis_3_0_downstream"]):
				_LOGGER.debug("Table parsing failed, trying alternative methods")
				
				# Look for div elements with status information
				divs = soup.find_all('div')
				for div in divs:
					text = div.get_text(strip=True)
					if "Cable Modem Status" in text and "Online" in text:
						data["cable_modem_status"] = "Online"
					elif "Primary downstream channel" in text and "Locked" in text:
						data["primary_downstream_channel"] = "Locked"
				
				# Look for spans
				spans = soup.find_all('span')
				for span in spans:
					text = span.get_text(strip=True)
					if text.isdigit():
						# Try to find context for numbers
						parent = span.parent
						if parent:
							parent_text = parent.get_text(strip=True).lower()
							if "docsis 3.0" in parent_text and "downstream" in parent_text:
								data["docsis_3_0_downstream"] = text
							elif "docsis 3.0" in parent_text and "upstream" in parent_text:
								data["docsis_3_0_upstream"] = text
							elif "docsis 3.1" in parent_text and "downstream" in parent_text:
								data["docsis_3_1_downstream"] = text
							elif "docsis 3.1" in parent_text and "upstream" in parent_text:
								data["docsis_3_1_upstream"] = text

			# Parse ISP Provider from main page HTML
			if main_html:
				data["isp_provider"] = self._parse_isp_provider(main_html)
			else:
				data["isp_provider"] = self._parse_isp_provider(html)

			_LOGGER.debug("Final parsed data: %s", data)
			return data
			
		except Exception as err:
			_LOGGER.error("Error parsing status page: %s", err)
			raise UpdateFailed(f"Error parsing status page: {err}") from err

	def _parse_isp_provider(self, html: str) -> str:
		"""Parse ISP provider from JavaScript customer ID."""
		try:
			# Look for the JavaScript code that sets the customer ID
			import re
			
			# Find customerId() function calls or customer ID assignments
			customer_patterns = [
				r'customerId\(\)\s*==\s*(\d+)',
				r'customerId\s*=\s*(\d+)',
				r'customerId\(\)\s*===\s*(\d+)',
			]
			
			for pattern in customer_patterns:
				matches = re.findall(pattern, html, re.IGNORECASE)
				if matches:
					customer_id = int(matches[0])
					
					# Map customer ID to provider name
					provider_map = {
						6: "Virgin Media (VTR)",
						8: "Virgin Media",
						20: "Ziggo",
						41: "Virgin Media Ireland",
						44: "Telekom Austria",
						50: "Yallo",
						51: "Sunrise",
					}
					
					return provider_map.get(customer_id, f"Liberty Global International (ID: {customer_id})")
			
			# Fallback: try to find provider names in the JavaScript
			if "CustNameVM" in html:
				return "Virgin Media"
			elif "CustNameZiggo" in html:
				return "Ziggo"
			elif "CustNameTMAustria" in html:
				return "Telekom Austria"
			elif "CustNameYallo" in html:
				return "Yallo"
			elif "CustNameSunrise" in html:
				return "Sunrise"
			elif "CustNameVMIE" in html:
				return "Virgin Media Ireland"
			elif "CustNameVTR" in html:
				return "Virgin Media (VTR)"
			else:
				return "Unknown Provider"
				
		except Exception as err:
			_LOGGER.warning("Error parsing ISP provider: %s", err)
			return "Unknown Provider"

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
		return provider_map.get(customer_id, f"Liberty Global International (ID: {customer_id})")


async def async_setup_entry(
	hass: HomeAssistant,
	config_entry: ConfigEntry,
	async_add_entities: AddEntitiesCallback,
) -> None:
	"""Set up the Arris Router Status sensors."""
	host = config_entry.data[CONF_HOST]
    
	coordinator = ArrisDataUpdateCoordinator(hass, host)
	await coordinator.async_config_entry_first_refresh()

	entities = []
	for description in SENSOR_DESCRIPTIONS:
		entities.append(ArrisSensor(coordinator, description))

	async_add_entities(entities)


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

	@property
	def native_value(self) -> str | None:
		"""Return the state of the sensor."""
		return self.coordinator.data.get(self.entity_description.key)

	@property
	def available(self) -> bool:
		"""Return if entity is available."""
		return self.coordinator.last_update_success and self.native_value is not None
