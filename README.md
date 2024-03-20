# binary_programming_support Library
A minimalist library to support binary programming in Windows using our bootloader

## Functions

### `common.py`

#### `find_device(target_vid, target_pid, name=None)`
Finds a device with the specified VID and PID.

- `target_vid`: The vendor ID (VID) of the device.
- `target_pid`: The product ID (PID) of the device.
- `name` (optional): The name of the device.

Returns the port to which the device is connected, or None if not found.

#### `get_pid_vid(port_name)`
Gets the PID and VID of a device connected to the specified port.

- `port_name`: The name of the port.

Returns a tuple containing the VID and PID of the device, or (None, None) if not found.

### `prog_utils.py`

#### `flash_prog_procedure(firm_bin, port, hash=None)`
Executes the programming procedure for flashing firmware onto a device.

- `firm_bin`: The path to the firmware binary file.
- `port`: The port to which the device is connected.
- `hash` (optional): The hash value of the firmware for verification.

Returns a tuple containing the status code, message, and success indicator.

## Dependencies

- `pyserial`: For interacting with serial ports.
- `subprocess`: For executing commands.
- `re`: For regular expressions.

## License

This library is licenced under LGPLV2.1

