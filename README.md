# Arris Router Status

A Home Assistant custom component for monitoring Arris router status via HACS.

This component connects to your Arris router (ARRIS-based modem) and extracts comprehensive cable modem status, configuration, and service flow information using unauthenticated API endpoints.

## Features

- **ISP Provider Detection**: Automatically detects your ISP (Virgin Media, Ziggo, Telekom Austria, etc.)
- **Cable Modem Status**: Complete modem operational status and registration information
- **Channel Information**: Accurate DOCSIS 3.0 and 3.1 channel counts matching router UI
- **Configuration Data**: Router configuration including DOCSIS mode, network access, and CPE limits
- **Service Flow Parameters**: Primary downstream and upstream service flow details
- **No Authentication Required**: Uses public API endpoints for data collection

## Sensors

The component creates the following sensors:

### Status & Operational Data
- `sensor.cable_modem_status` - Overall modem status (Online/Offline)
- `sensor.primary_downstream_channel` - Primary downstream channel lock status
- `sensor.cable_modem_registration` - Modem registration state
- `sensor.wan_ip_provision_mode` - WAN IP provisioning method (DHCP/Static/PPPoE)
- `sensor.fail_safe_mode` - Fail-safe mode status
- `sensor.no_rf_detected` - RF signal detection status

### DOCSIS Information
- `sensor.docsis_version` - Current DOCSIS version (3.0/3.1)
- `sensor.docsis_mode` - DOCSIS operational mode

### Channel Counts
- `sensor.docsis_3_0_downstream_channels` - Number of DOCSIS 3.0 downstream channels
- `sensor.docsis_3_0_upstream_channels` - Number of DOCSIS 3.0 upstream channels
- `sensor.docsis_3_1_downstream_channels` - Number of DOCSIS 3.1 downstream channels
- `sensor.docsis_3_1_upstream_channels` - Number of DOCSIS 3.1 upstream channels
- `sensor.total_downstream_channels` - Total downstream channels
- `sensor.total_upstream_channels` - Total upstream channels

### Configuration Data
- `sensor.isp_provider` - ISP provider name
- `sensor.network_access` - Network access configuration
- `sensor.max_cpes` - Maximum number of CPEs allowed
- `sensor.baseline_privacy` - Baseline privacy setting
- `sensor.config_file` - Configuration file identifier

### Service Flow Parameters
- `sensor.primary_downstream_sfid` - Primary downstream Service Flow ID
- `sensor.primary_downstream_max_traffic_rate` - Primary downstream max traffic rate
- `sensor.primary_downstream_max_traffic_burst` - Primary downstream max traffic burst
- `sensor.primary_downstream_min_traffic_rate` - Primary downstream min traffic rate
- `sensor.primary_upstream_sfid` - Primary upstream Service Flow ID
- `sensor.primary_upstream_max_traffic_rate` - Primary upstream max traffic rate
- `sensor.primary_upstream_max_traffic_burst` - Primary upstream max traffic burst
- `sensor.primary_upstream_min_traffic_rate` - Primary upstream min traffic rate
- `sensor.primary_upstream_max_concatenated_burst` - Primary upstream max concatenated burst
- `sensor.primary_upstream_scheduling_type` - Primary upstream scheduling type

## How It Works

The component communicates with your Arris router using unauthenticated API endpoints:

1. **Main Page Access**: Connects to the router's web interface to establish session state
2. **Status Endpoint**: Calls `connection_troubleshoot_data.php` for modem operational data
3. **Network Status Endpoint**: Calls `ajaxGet_device_networkstatus_data.php` for comprehensive status, configuration, and channel data
4. **Data Parsing**: Extracts all sensor values from the JSON responses
5. **Sensor Updates**: Updates all sensors every 30 seconds with current router data

No authentication is required as the component uses public API endpoints that provide status information without login credentials.

## Installation

## How It Works

The component communicates with your Arris router using unauthenticated API endpoints:

1. **Main Page Access**: Connects to the router's web interface to establish session state
2. **Status Endpoint**: Calls `connection_troubleshoot_data.php` for modem operational data
3. **Network Status Endpoint**: Calls `ajaxGet_device_networkstatus_data.php` for comprehensive status, configuration, and channel data
4. **Data Parsing**: Extracts all sensor values from the JSON responses
5. **Sensor Updates**: Updates all sensors every 30 seconds with current router data

No authentication is required as the component uses public API endpoints that provide status information without login credentials.

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/richardctrimble/ha_arris_router_status`
6. Select "Integration" as the category
7. Click "Add"
8. Search for "Arris Router Status" and install it
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/ha_arris_router_status` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration > Integrations
4. Click "Add Integration" and search for "Arris Router Status"

## Configuration

1. Go to Configuration > Integrations in Home Assistant
2. Click "Add Integration"
3. Search for "Arris Router Status"
4. Enter your router's IP address (default: 192.168.100.1)
5. Click Submit

## Requirements

- Arris router in modem mode (ARRIS-based firmware)
- Router accessible at the configured IP address (default: 192.168.100.1)
- Network connectivity between Home Assistant and router
- No authentication required - uses public API endpoints

## Supported Routers

This component has been tested with:
- Arris routers with ARRIS firmware (various models)
- Default IP: 192.168.100.1
- ISP Provider detection works for: Virgin Media, Ziggo, Telekom Austria, Yallo, Sunrise, Virgin Media Ireland
- Channel and configuration data available on routers using the ajaxGet_device_networkstatus_data.php endpoint

## Authentication Requirements

**No Authentication Required**: This component uses unauthenticated API endpoints that provide comprehensive status and configuration data without requiring login credentials. All sensor data is collected automatically without user intervention.

## Troubleshooting

### All Sensors Show "Unavailable"
- Check that the router IP address is correct (default: 192.168.100.1)
- Verify network connectivity between Home Assistant and the router
- Ensure the router is powered on and functioning
- Check router firmware - must be ARRIS-based with the ajaxGet_device_networkstatus_data.php endpoint

### Component Not Loading
- Ensure the router IP address is reachable from your network
- Check that your router uses ARRIS firmware
- Verify the custom_components directory structure is correct
- Restart Home Assistant after installation

### Incorrect Channel Counts
- The component uses direct channel counts from the router's API
- Compare with your router's web interface at the same time
- If counts don't match, the router firmware may be different
- Check router logs for any API endpoint changes

### ISP Provider Shows "Unknown Provider"
- The component maps customer IDs to provider names
- If your ISP isn't recognized, it will show "Liberty Global International (ID: X)"
- This doesn't affect other sensor functionality

### Connection Timeouts
- Increase timeout settings if your network is slow
- Check for network congestion or firewall rules
- Ensure the router isn't overloaded with requests

## Contributing

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Test with your Arris router
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This is an unofficial integration not affiliated with Arris. Use at your own risk.