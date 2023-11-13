#!/usr/bin/env python3

import argparse
import os
import re

import zstandard as zstd

from ..common.parser.lns_parser import LnsParser
from ..common.util.binary_writer import BinaryWriter


def extract(filename, output=None):
    parser = LnsParser(filename)
    files = parser.parse()
    if output is None:
        output_dir = os.path.dirname(filename)
        output_name = os.path.splitext(os.path.basename(filename))[0]
        output = os.path.join(output_dir, f"{output_name}_unpacked")

    write_files(files, output)


def write_files(files, dirname):
    os.mkdir(dirname)
    for path, data in files.items():
        full_path = dirname + path
        directory = os.path.dirname(full_path)
        os.makedirs(directory, exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(data)


def create(dirname, output=None):
    dirname = os.path.realpath(dirname)
    files = read_files(dirname)
    if output is None:
        output = f"{dirname}.lns"

    write_lns(output, files)


def read_files(dirname):
    files = {}
    real_path = os.path.realpath(dirname)
    pattern = r"^_.+\.xml$"
    for dirpath, dirnames, filenames in os.walk(real_path):
        for filename in filenames:
            if re.match(pattern, filename):
                continue

            full_path = dirpath + "/" + filename
            lns_path = full_path[len(real_path):].replace(os.sep, '/')
            with open(full_path, "rb") as f:
                files[lns_path] = f.read()
    return files


def write_lns(filename, files):
    fname_writer = BinaryWriter()
    fdata_writer = BinaryWriter()
    for fname, fdata in files.items():
        fname_writer.write_uint32(len(fname))
        fname_writer.write_string(fname)
        fname_writer.write_uint32(0)
        fname_writer.write_uint32(len(fdata))
        fname_writer.write_uint32(fdata_writer.size)  # offset
        fdata_writer.write_bytes(fdata)

    cctx = zstd.ZstdCompressor()
    compressed = cctx.compress(fdata_writer.get_bytes())

    lns_writer = BinaryWriter()
    lns_writer.write_bytes(b"LZC\0")
    lns_writer.write_uint32(1)
    lns_writer.write_uint32(len(files))
    lns_writer.write_uint32(0x48 + fname_writer.size)  # header size
    lns_writer.write_uint32(1)
    lns_writer.write_uint32(1)
    lns_writer.write_uint32(fdata_writer.size)
    lns_writer.write_uint32(len(compressed))
    lns_writer.write_bytes(bytes(32))
    lns_writer.write_uint32(2)
    lns_writer.write_uint32(fname_writer.size)
    lns_writer.write_bytes(fname_writer.get_bytes())
    lns_writer.write_uint32(1)
    lns_writer.write_uint32(len(compressed))
    lns_writer.write_bytes(compressed)
    lns_writer.to_file(filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract or create Snapchat lens archives")
    parser.add_argument("input", help="lens archive or directory")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-x", "--extract", action="store_true", help="extract an archive")
    group.add_argument("-c", "--create", action="store_true", help="create an archive")
    args = parser.parse_args()

    if args.extract:
        extract(args.input)
    elif args.create:
        create(args.input)
