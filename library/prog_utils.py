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
@brief  This is a python file with the functions for programming the Twist boards remotely

@author Guillaume Arthaut <guillaume.arthaud@laas.fr>
@author Jean Alinei <jean.alinei@owntech.org>
"""

import subprocess
import re
import time
import serial
import common

import progress_bar

def touch_serial_port(port, baudrate):
    """
    Touches the serial port by forcing a reset.

    Args:
        port (str): The serial port to touch.
        baudrate (int): The baudrate to use for the serial communication.

    Returns:
        None
    """

    print("Forcing reset using %dbps open/close on port %s" % (baudrate, port))
    try:
        s = serial.Serial(port=port, baudrate=baudrate)
        s.setDTR(False)
        s.close()
    except IOError as e:
        print("Wait and retry")
    except TypeError as e:
        print(f"Error while touching the port {port}")
    except:
        pass
    time.sleep(0.4)  # DO NOT REMOVE THAT (required by SAM-BA based boards)

def wait_for_reboot(vid, pid):
    """
    Waits for the reboot of the board in bootloader mode.

    Args:
        vid (str): The vendor ID of the board.
        pid (str): The product ID of the board.

    Returns:
        None
    """

    print("Rebooting board in bootloader mode...")
    elapsed=0
    port_found = False
    while elapsed < 15 and port_found == False:
        spin_port = common.find_device(vid, pid)
        if spin_port != None:
            port_found = True
        time.sleep(0.25)
        elapsed += 0.25

    if port_found == False:
        print("Error! Unable to find selected board after reboot.")
        exit(-1)

    time.sleep(1)
    print("Board ready.")

def execute_cmd_prog(cmd, match_pattern_linebline=None, match_callback_linebline=None, match_pattern_end=None, match_callback_end=None, debug=False, timeout=None):
    """
    Executes a command and captures its output.

    Args:
        cmd (str): The command to execute.
        match_pattern_linebline (pattern): A regular expression pattern for matching lines during execution.
        match_callback_linebline (function): A callback function for handling matched lines.
        match_pattern_end (pattern): A regular expression pattern for matching the end of the command output.
        match_callback_end (function): A callback function for handling the end of output.
        debug (bool): Whether to print debug information.
        timeout (float): The maximum time to wait for the command to finish.

    Returns:
        tuple: A tuple containing the return code of the command and the output from callback functions.
    """

    if debug:
        print("cmd >", cmd)
    process = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    start_time = time.time()
    old_output_line = ""
    whole_output_buffer = ""
    match_callback_ret = []

    while True:
        output_line = process.stdout.readline()
        whole_output_buffer += output_line

        if timeout and (time.time() - start_time) > timeout:
            process.kill()
            raise TimeoutError(f"Timeout reached after {timeout} seconds")

        if (match_pattern_linebline is not None and match_callback_linebline is not None):
            matchPattern = match_pattern_linebline.findall(output_line)
            if matchPattern:
                match_callback_ret.append(match_callback_linebline(matchPattern))

        if debug:
            if (output_line != "\n"):
                print(output_line)

        if not output_line:
            break

        if (old_output_line != output_line):
            start_time = time.time()
            old_output_line = output_line

    process.wait()  # Wait for the process to finish

    if (match_pattern_end is not None and match_callback_end is not None):
        matchPattern = match_pattern_end.findall(whole_output_buffer)
        if matchPattern:
            match_callback_ret.append(match_callback_end(matchPattern))
    return process.returncode, match_callback_ret

def match_bootloader_action(matchPattern):

    """
    Matches a pattern for bootloader action.

    Args:
        matchPattern (pattern): The matched pattern.

    Returns:
        None
    """

    speed = "0 B/s"
    if 0 <= 6 < len(matchPattern[0]):
        if (matchPattern[0][5] != "" and matchPattern[0][6] != ""):
            speed = matchPattern[0][5] + " " + matchPattern[0][6]
        progress_bar.progress_bar(float(matchPattern[0][4]), 100, prefix='Program upload:', suffix='Complete ' + speed, length=40)
    return

def match_info(matchPattern):
    """
    Matches information pattern.

    Args:
        matchPattern (pattern): The matched pattern.

    Returns:
        str: Information from the matched pattern.
    """

    return matchPattern[0]

def reset_bootloader(port):
    """
    Resets the bootloader.

    Args:
        port (str): The port to which the bootloader is connected.

    Returns:
        int: 0 if successful, 1 if there's an error.
    """

    try:
        ret = execute_cmd_prog("./3rdParties/mcumgr.exe --conntype=serial --connstring=dev=" + port + ",baud=115200,mtu=128 reset", timeout=10)
        if (ret[0] == 0):
            print(f"Reset target")
        else:
            return 1 #ko
    except TimeoutError as e:
        print("\nError:", e)
        return 1 #ko

def check_hash_bootloader(port, desired_hash):
    """
    Checks the hash of the bootloader.

    Args:
        port (str): The port to which the bootloader is connected.
        desired_hash (str): The desired hash.

    Returns:
        int: 0 if successful and hashes match, 1 if there's an error, 2 if hashes do not match but bootloader exists.
    """
    patternImageInfo = re.compile(r"\s*(image=(\d))\s(slot=(\d))\n\s*(version:\s(\d.\d.\d))\n\s*(bootable:\s(.*))\n\s*(flags:\s(.*))\n\s*(hash:\s([0-9a-f]{64}))")
    try:
        ret = execute_cmd_prog("./3rdParties/mcumgr.exe --conntype=serial --connstring=dev=" + port + ",baud=115200,mtu=128 image list", match_pattern_end=patternImageInfo, match_callback_end=match_info, debug=False, timeout=10)
        if (ret[0] == 0):
            print(f"\nBootloader is here")
        else:
            return 1 #ko

        if (ret[1] != []): #First upload
            if (0 <= 11 < len(ret[1][0])):
                if(ret[1][0][11] == desired_hash):
                    print("Hash match! The desired program is already in the flash.")
                    return 0 #ok program match
                else:
                    return 2 #ok but need to flash
        return 1 #ko

    except TimeoutError as e:
        print("\nError:", e)
        return 1 #ko

def flash_prog_bootloader(firm_bin, port):
    """
    Flashes a program onto the bootloader.

    Args:
        firm_bin (str): The binary file of the program.
        port (str): The port to which the bootloader is connected.

    Returns:
        int: 0 if successful, 1 if there's an error.
    """

    patternBootloader = re.compile(r"(\d+\.?\d*) (\w+B|B) \/ (\d+\.?\d*) (\w+B|B) (?:\[.*?\]|).*?(\d+\.?\d*)%(?: (\d+\.?\d*) ((?:\w+B|B)\/s)|)")
    try:
        ret = execute_cmd_prog("./3rdParties/mcumgr.exe --conntype=serial --connstring=dev=" + port + ",baud=115200,mtu=128 image upload -e " + firm_bin, match_pattern_linebline=patternBootloader, match_callback_linebline=match_bootloader_action, debug=False, timeout=10)
        if (ret[0] == 0):
            print(f"\nSuccessfully flashed {firm_bin}")
            return 0 #yes
        else:
            return 1 #ko
    except TimeoutError as e:
            print("\nError:", e)
            return 1 #ko


def flash_prog_procedure(firm_bin, port, hash=None):
    """
    Flashes a program onto the bootloader using a specified procedure.

    Args:
        firm_bin (str): The binary file of the program.
        port (str): The port to which the bootloader is connected.
        hash (str): The hash of the program.

    Returns:
        tuple: A tuple containing the result code (0 for success, 1 for failure), message, and success status.
    """

    vid, pid = common.get_pid_vid(port)

    touch_serial_port(port, 1200)
    time.sleep(1)

    wait_for_reboot(vid, pid)

    new_port = common.find_device(vid, pid)

    if (hash != None):
        hash_ret = check_hash_bootloader(new_port, hash)
        if (hash_ret == 0):
            reset_ret = reset_bootloader(new_port)
            if (reset_ret == 1):
                return 1, "Failure", False
            return 0, "Success programm already in flash", True
        elif (hash_ret == 1):
            return 1, "Failure", False
        #if 2 we continue

    prog_ret = flash_prog_bootloader(firm_bin, new_port)
    if (prog_ret == 1):
        return 1, "Failure", False
    time.sleep(5)

    reset_ret = reset_bootloader(new_port)
    if (reset_ret == 1):
        return 1, "Failure", False

    return 0, "Success", True