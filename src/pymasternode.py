"""Main module."""
import json
from pathlib import PosixPath
from typing import Dict, Union

import vultr
from vultr import Vultr


PATH_PROJECT_ROOT: object = PosixPath(__file__).parents[1]

with open(PATH_PROJECT_ROOT / "data" / "Settings.json", "r") as f:
    CONFIG: Dict[str, Union[str, int]] = json.load(f)

with open(PATH_PROJECT_ROOT / "data" / "api_key_vultr.txt", "r") as file:
    VULTR: Vultr = vultr.Vultr(file.read().strip())
