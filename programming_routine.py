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

@author Luiz Villa <luiz.villa@laas.fr>
"""

from library import common, prog_utils


Twist_vid = 0x2fe3
Twist_pid = 0x0100


Twist_port = common.find_device(Twist_vid, Twist_pid)
program_bin = "example_bin_core.bin"

ret_prog = prog_utils.flash_prog_procedure(program_bin, Twist_port)
