#!/usr/bin/env python3

import sys
import os
from lxml import etree as ET
from enum import Enum

package_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, package_path)

from common.parser.resource_parser import ResourceParser
from common.util.binary_reader import BinaryReader, BinaryReaderError

class XmlResourceBuilder:
    def __init__(self):
        self.root = ET.Element("resource")
        self.stack = [self.root]
        self.arrays = []
        self.parent = self.root

    def start_block(self, key=None):
        block = ET.SubElement(self.parent, "block")
        if key is not None:
            block.set("key", key)
        self.stack.append(self.parent)
        self.parent = block

    def finish_block(self):
        self.parent = self.stack.pop()

    def add_value(self, key, value, tag, sub_tag=None):
        el = ET.SubElement(self.parent, tag, key=key)
        if sub_tag is None:
            el.text = str(value)
        else:
            for n in value:
                sub_el = ET.SubElement(el, sub_tag)
                sub_el.text = str(n)

    def add_array(self, key, offset, size):
        el = ET.SubElement(self.parent, "bytes", key=key)
        self.arrays.append((offset, size, el))

    # infer whether an array contains bytes, strings, or something else
    def infer_arrays(self, data, header_size):
        self.arrays.sort(key=lambda x: x[0])
        for (offset, size, el), i in zip(self.arrays, range(len(self.arrays))):
            # "size" represents the number of elements (of unknown length) in the array
            # "true size" is the number of bytes in the array
            if i == len(self.arrays) - 1:
                true_size = header_size - offset
            else:
                true_size = self.arrays[i+1][0] - offset

            raw = data[header_size+offset:header_size+offset+true_size]

            if true_size == size:
                el.text = raw.hex()
            else:
                el.tag = "array"
                reader = BinaryReader(raw)
                strings = []
                is_string_array = True

                # try to read array as strings, and deem it not a string array if it fails
                try:
                    for _ in range(size):
                        string_len = reader.read_uint32()
                        string = reader.read_string(string_len)
                        strings.append(string)
                    is_string_array = reader.finished()
                except (UnicodeDecodeError, BinaryReaderError) as e:
                    is_string_array = False

                if is_string_array:
                    for string in strings:
                        sub_el = ET.SubElement(el, "string")
                        sub_el.text = string
                elif true_size % size != 0:
                    raise ValueError("Failed to infer array structure")
                else:
                    reader.seek(0)
                    while not reader.finished():
                        sub_el = ET.SubElement(el, "bytes")
                        sub_el.text = reader.read_bytes(true_size // size).hex()

    def finished(self):
        return len(self.stack) == 0


parser = ResourceParser(sys.argv[1])
xml = parser.parse(XmlResourceBuilder)

ET.dump(xml)
