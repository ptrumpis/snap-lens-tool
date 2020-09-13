#!/usr/bin/env python3

import argparse
import sys
import os
import json
import numpy as np

package_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, package_path)

from parser.resource_parser import ResourceParser, ArrayData
from parser.mesh_parser import MeshParser

def default_array_parser(key, val):
    return "<array>"

def make_mesh_array_parser(json):
    vert_dtype, _ = MeshParser.build_dtype(json)
    face_dtype = [("face", ("H", 3))]
    def mesh_array_parser(key, val):
        if key == "vertices":
            array = val.as_dtype(vert_dtype)
            array = [[attr.tolist() for attr in vert] for vert in array]
            return array
        elif key == "indices":
            array = val.as_dtype(face_dtype)
            array = [face[0].tolist() for face in array]
            return array
        return "<unknown array type>"
    return mesh_array_parser

def scn_array_parser(key, val):
    if key == "defines":
        return val.as_strings()
    return "<unknown array type>"

def replace_bytes(d, array_parser=default_array_parser):
    for key, val in d.items():
        if type(val) == ArrayData:
            d[key] = array_parser(key, val)
        elif issubclass(type(val), np.generic):
            d[key] = val.item()
        elif type(val) == np.ndarray:
            d[key] = val.tolist()
        elif type(val) == dict:
            replace_bytes(val, array_parser)


parser = argparse.ArgumentParser(description="Print resource data (.mesh/.scn) as json")
parser.add_argument("input", help=".mesh or .scn file")
parser.add_argument("-v", dest="print_arrays", action="store_true", help="print array data")
args = parser.parse_args()

parser = ResourceParser(args.input)
parsed = parser.parse()
filetype = os.path.splitext(args.input)[1]

array_parser = default_array_parser
if args.print_arrays:
    if filetype == ".mesh":
        array_parser = make_mesh_array_parser(parsed)
    elif filetype == ".scn":
        array_parser = scn_array_parser

replace_bytes(parsed, array_parser)
print(json.dumps(parsed, indent=2))

