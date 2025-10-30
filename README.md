# Arris Router Status

A Home Assistant custom component for monitoring Arris router status via HACS.

This component connects to your Arris router (ARRIS-based modem) and extracts cable modem status information from the unauthenticated status page.

## Features

- **Cable Modem Status**: Shows if the modem is online and the DOCSIS version
- **Primary Downstream Channel**: Lock status and channel type
- **Channel Overview**: Number of DOCSIS 3.0 and 3.1 downstream/upstream channels

## Sensors

The component creates the following sensors:

- `sensor.cable_modem_status` - Overall modem status
- `sensor.primary_downstream_channel` - Primary downstream channel status  
- `sensor.docsis_3_0_downstream_channels` - Number of DOCSIS 3.0 downstream channels
- `sensor.docsis_3_0_upstream_channels` - Number of DOCSIS 3.0 upstream channels
- `sensor.docsis_3_1_downstream_channels` - Number of DOCSIS 3.1 downstream channels
- `sensor.docsis_3_1_upstream_channels` - Number of DOCSIS 3.1 upstream channels
- `sensor.isp_provider` - ISP provider (Virgin Media, Ziggo, etc.)

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

1. Copy the `custom_components/virgin_media_status` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration > Integrations
4. Click "Add Integration" and search for "Arris Router Status"

## Configuration

1. Go to Configuration > Integrations in Home Assistant
2. Click "Add Integration"
3. Search for "Arris Router Status"
4. Enter your router's IP address (default: 192.168.100.1)
5. Click Submit

The component will automatically detect your Arris router and start monitoring the status.

## Requirements

- Arris router in modem mode (ARRIS-based)
- Router accessible at the configured IP address
- Unauthenticated status page must be available

## Supported Routers

This component has been tested with:
- Arris ARRIS routers in modem mode
- Default IP: 192.168.100.1

The status page should contain information like:
```
Cable Modem Status
Item                        Status      Comments
Cable Modem Status          Online      DOCSIS 3.1
Primary downstream channel  Locked      SC-QAM
Channel Overview            Downstream  Upstream
DOCSIS 3.0 channels         32          5
DOCSIS 3.1 channels         1           1
```

## Troubleshooting

### Component Not Loading
- Ensure the router IP address is correct
- Check that your router is in modem mode
- Verify the status page is accessible from your Home Assistant instance

### No Data in Sensors
- Check the Home Assistant logs for parsing errors
- Verify the router status page format matches expected structure
- The component may need adjustment for different router firmware versions

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