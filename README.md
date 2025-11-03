# Arris Router Status -- Broken for now

A Home Assistant custom component for monitoring Arris router status via HACS.

It seems to work wel enough but the router seems to lock up after a while and then will not respond to UI at all untill the router is rebooted.. 
Sad but thats the way.. I added a refresh interval to see if it might work if we do on poll so often.

## Sadly due to the above this is not a useful add on 

This component connects to your Arris router (ARRIS-based modem) and extracts comprehensive cable modem status, configuration, and service flow information using unauthenticated API endpoints.

## Features

- **ISP Provider Detection**: Automatically detects your ISP (Virgin Media, Ziggo, Telekom Austria, etc.)
- **Cable Modem Status**: Complete modem operational status and registration information
- **Channel Information**: Accurate DOCSIS 3.0 and 3.1 channel counts matching router UI
- **Configuration Data**: Router configuration including DOCSIS mode, network access, and CPE limits
- **Service Flow Parameters**: Primary downstream and upstream service flow details
- **No Authentication Required**: Uses public API endpoints for data collection

## Sensors

The component creates 30 sensors:

### Status Sensors (13 sensors)
Dynamic values that may change frequently:
- Cable modem status, registration, WAN IP mode, fail-safe mode, RF detection
- DOCSIS version and channel counts (3.0/3.1 downstream/upstream, totals)

### Diagnostic Sensors (1 sensor)
- Last Update Time (UTC timestamp of last successful router poll)

### Service Flow & Configuration Sensors (16 sensors)
Router configuration and service flow parameters from API:
- ISP provider, network access, max CPEs, baseline privacy, DOCSIS mode, config file
- Primary service flow parameters (SFID, traffic rates, burst limits, scheduling)

## Installation

### HACS (Recommended)
1. Add `https://github.com/richardctrimble/ha_arris_router_status` as custom repository
2. Install "Arris Router Status" integration
3. Restart Home Assistant

### Manual
1. Copy `custom_components/ha_arris_router_status` to your HA `custom_components` directory
2. Restart Home Assistant
3. Add integration via Configuration > Integrations

## Configuration

Add the integration and enter your router IP (default: 192.168.100.1).

## Requirements

- Arris router in modem mode (ARRIS-based firmware)
- Router accessible at configured IP address
- No authentication required

## Supported Routers

- Arris routers with ARRIS firmware (various models) **in modem mode only**
- Default IP: 192.168.100.1
- ISP detection: Virgin Media, Ziggo, Telekom Austria, Yallo, Sunrise, Virgin Media Ireland

**Note**: Tested only in modem mode. Router mode functionality not tested.

## Troubleshooting

### All Sensors Show "Unavailable"
- Verify router IP address and network connectivity
- Ensure router is ARRIS-based with `ajaxGet_device_networkstatus_data.php` endpoint

### Incorrect Channel Counts
- Compare with router web interface
- Router firmware differences may cause discrepancies

### ISP Provider Shows "Unknown ISP ID=X"
- Component maps known customer IDs to provider names
- Unknown ISPs show as "Unknown ISP ID=X"

## Contributing

Fork, create feature branch, test with Arris router, submit PR.

## License

MIT License - see LICENSE file.

## Disclaimer


Unofficial integration not affiliated with Arris. Use at your own risk.

