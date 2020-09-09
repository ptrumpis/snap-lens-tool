#!/usr/bin/env python3

import sys
from ..parser.resource_parser import ResourceParser
import json
import numpy as np

def replace_bytes(d):
    for key, val in d.items():
        if type(val) == bytes:
            d[key] = "<bytes>"
        elif issubclass(type(val), np.generic):
            d[key] = val.item()
        elif type(val) == np.ndarray:
            d[key] = val.tolist()
        elif type(val) == dict:
            replace_bytes(val)

parser = ResourceParser(sys.argv[1])
parsed = parser.parse()
replace_bytes(parsed)
print(json.dumps(parsed, indent=2))

