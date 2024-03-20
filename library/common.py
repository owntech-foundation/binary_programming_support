"""
Copyright (c) 2021-2024 LAAS-CNRS

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation, either version 2.1 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.

SPDX-License-Identifier: LGLPV2.1
"""

"""
@brief  This is a python file that is used to find Twist devices and get their pid and vid

@author Luiz Villa <luiz.villa@laas.fr>
"""


import serial
from serial.tools import list_ports


device_port = None
ser = None
last_send = ""

def find_device(target_vid, target_pid, name=None):
    """
    Finds a device with the specified VID and PID.

    Args:
        target_vid (int): The vendor ID (VID) of the device.
        target_pid (int): The product ID (PID) of the device.
        name (str, optional): The name of the device. Defaults to None.

    Returns:
        str: The port to which the device is connected, or None if not found.
    """

    ports = serial.tools.list_ports.comports()
    for port in ports:
        if (port.vid == target_vid and port.pid == target_pid):
            if (name != None):
                if (port.description == name):
                    return port.device
                return None
            return port.device
    return None


def get_pid_vid(port_name):
    """
    Gets the PID and VID of a device connected to the specified port.

    Args:
        port_name (str): The name of the port.

    Returns:
        tuple: A tuple containing the VID and PID of the device, or (None, None) if not found.
    """
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.device == port_name:
            return port.vid, port.pid
    return None, None
