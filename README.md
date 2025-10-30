# Arris Router Status

A Home Assistant custom component for monitoring Arris router status via HACS.

This component connects to your Arris router (ARRIS-based modem) and extracts cable modem status information. It currently provides ISP provider detection and attempts to extract status data from various endpoints.

## Features

- **ISP Provider Detection**: Automatically detects your ISP (Virgin Media, Ziggo, Telekom Austria, etc.)
- **Cable Modem Status**: Shows modem status when accessible (may require authentication)
- **Channel Information**: DOCSIS channel counts when data is available

## Current Status

✅ **Working**: ISP Provider detection  
⚠️ **Limited**: Status data extraction (requires router authentication for full data)  
🔄 **In Development**: Alternative data collection methods

## Sensors

The component creates the following sensors:

- `sensor.isp_provider` - ISP provider (Virgin Media, Ziggo, etc.) - ✅ Working
- `sensor.cable_modem_status` - Overall modem status - ⚠️ Limited
- `sensor.primary_downstream_channel` - Primary downstream channel status - ⚠️ Limited
- `sensor.docsis_3_0_downstream_channels` - Number of DOCSIS 3.0 downstream channels - ⚠️ Limited
- `sensor.docsis_3_0_upstream_channels` - Number of DOCSIS 3.0 upstream channels - ⚠️ Limited
- `sensor.docsis_3_1_downstream_channels` - Number of DOCSIS 3.1 downstream channels - ⚠️ Limited
- `sensor.docsis_3_1_upstream_channels` - Number of DOCSIS 3.1 upstream channels - ⚠️ Limited

## Installation

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
- Router accessible at the configured IP address
- Network connectivity between Home Assistant and router

## Supported Routers

This component has been tested with:
- Arris routers with ARRIS firmware
- Default IP: 192.168.100.1
- ISP Provider detection works for: Virgin Media, Ziggo, Telekom Austria, Yallo, Sunrise

## Authentication Requirements

**Current Limitation**: The ARRIS router firmware requires authentication to access full status data. The component currently:

- ✅ Successfully detects ISP provider from the login page
- ⚠️ Attempts multiple endpoints for status data but may show "Unavailable" if authentication is required

**Future Enhancement**: SNMP support or authenticated API access may be added in future versions.

## Troubleshooting

### ISP Provider Shows Correctly But Status Shows "Unavailable"
- This is expected behavior for routers requiring authentication
- The component successfully detects your ISP but cannot access detailed status data
- Check router firmware version and authentication requirements

### Component Not Loading
- Ensure the router IP address is correct
- Check that your router uses ARRIS firmware
- Verify network connectivity to the router

### Connection Issues
- Ensure Home Assistant can reach the router IP
- Check firewall settings on your network
- Verify the router hasn't changed IP addresses

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