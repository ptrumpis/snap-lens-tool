#!/usr/bin/env python3

import sys
import os.path
from ..parser.resource_parser import ResourceParser, ArrayData
import json
import numpy as np

def replace_bytes(d, filetype):
    for key, val in d.items():
        if type(val) == ArrayData:
            if filetype == ".scn":
                if key == "defines":
                    d[key] = val.as_strings()
                else:
                    d[key] = "<bytes>"
            else:
                d[key] = "<bytes>"
        elif issubclass(type(val), np.generic):
            d[key] = val.item()
        elif type(val) == np.ndarray:
            d[key] = val.tolist()
        elif type(val) == dict:
            replace_bytes(val, filetype)

filename = sys.argv[1]
filetype = os.path.splitext(filename)[1]
parser = ResourceParser(filename)
parsed = parser.parse()
replace_bytes(parsed, filetype)
print(json.dumps(parsed, indent=2))

