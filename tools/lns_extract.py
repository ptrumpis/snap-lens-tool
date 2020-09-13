#!/usr/bin/env python3

import argparse
import sys
import os

package_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, package_path)

from parser.lns_parser import LnsParser

def extract(args):
    parser = LnsParser(args.input)
    files = parser.parse()
    output_name = os.path.splitext(os.path.basename(args.input))[0][:10] + "_extracted"
    write_files(files, output_name)

def write_files(files, dirname):
    os.mkdir(dirname)
    for path, data in files.items():
        full_path = dirname + path
        directory = os.path.dirname(full_path)
        os.makedirs(directory, exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(data)


parser = argparse.ArgumentParser(description="Extract or create Snapchat lens archives")
parser.add_argument("input", help="lens archive or directory")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-x", "--extract", action="store_true", help="extract an archive")
group.add_argument("-c", "--create", action="store_true", help="create an archive")
args = parser.parse_args()

if args.extract:
    extract(args)
elif args.create:
    raise NotImplementedError("LNS archive creation not supported")

