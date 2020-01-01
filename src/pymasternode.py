# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Main module."""

import json
from pathlib import PosixPath
from typing import Dict, Union

import vultr
from vultr import Vultr

PATH_PROJECT_ROOT: object = PosixPath(__file__).parents[1]

with open(PATH_PROJECT_ROOT / "data" / "Settings.json") as f:
    CONFIG: Dict[str, Union[str, int]] = json.load(f)

with open(PATH_PROJECT_ROOT / "data" / "api_key_vultr.txt") as file:
    VULTR: Vultr = vultr.Vultr(file.read().strip())
