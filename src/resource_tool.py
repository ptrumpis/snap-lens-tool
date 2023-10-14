#!/usr/bin/env python3

import argparse

from lxml import etree as ET

from common.parser.resource_parser import ResourceParser
from common.serializer.resource_serializer import ResourceSerializer
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
                true_size = len(data) - header_size - offset
            else:
                true_size = self.arrays[i + 1][0] - offset

            raw = data[header_size + offset:header_size + offset + true_size]

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
                    raise ValueError(f"Failed to infer array structure at offset {header_size + offset}")
                else:
                    reader.seek(0)
                    while not reader.finished():
                        sub_el = ET.SubElement(el, "bytes")
                        sub_el.text = reader.read_bytes(true_size // size).hex()

    def finished(self):
        return len(self.stack) == 0


def resource_to_xml(filename, outfile):
    parser = ResourceParser(filename)
    xml = parser.parse(XmlResourceBuilder)
    xml = ET.ElementTree(xml)
    xml.write(outfile, pretty_print=True)


def _xml_to_resource_rec(serializer, node):
    key = node.attrib["key"] if "key" in node.attrib else None
    if node.tag == "block":
        serializer.begin(key)
        for child in node:
            _xml_to_resource_rec(serializer, child)
        serializer.end()
    elif node.tag == "bool8":
        if node.text.lower() == "true":
            value = True
        elif node.text.lower() == "false":
            value = False
        else:
            raise ValueError("Unexpected value for bool8")
        serializer.write_bool8(key, value)
    elif node.tag == "bytes":
        value = "" if node.text is None else node.text
        value = bytes.fromhex(value)
        serializer.write_bytes(key, value)
    elif node.tag == "float64":
        serializer.write_float64(key, node.text)
    elif node.tag == "float32":
        serializer.write_float32(key, node.text)
    elif node.tag == "uint32":
        serializer.write_uint32(key, node.text)
    elif node.tag == "int32":
        serializer.write_int32(key, node.text)
    elif node.tag == "uint64":
        serializer.write_uint64(key, node.text)
    elif node.tag == "int64":
        serializer.write_int64(key, node.text)
    elif node.tag == "mat2f":
        values = [child.text for child in node]
        serializer.write_mat2f(key, values)
    elif node.tag == "mat3f":
        values = [child.text for child in node]
        serializer.write_mat3f(key, values)
    elif node.tag == "mat4f":
        values = [child.text for child in node]
        serializer.write_mat4f(key, values)
    elif node.tag == "quatf":
        values = [child.text for child in node]
        serializer.write_quatf(key, values)
    elif node.tag == "string":
        value = "" if node.text is None else node.text
        serializer.write_string(key, value)
    elif node.tag == "vec2f":
        values = [child.text for child in node]
        serializer.write_vec2f(key, values)
    elif node.tag == "vec3f":
        values = [child.text for child in node]
        serializer.write_vec3f(key, values)
    elif node.tag == "vec4f":
        values = [child.text for child in node]
        serializer.write_vec4f(key, values)
    elif node.tag == "vec4b":
        values = [child.text for child in node]
        serializer.write_vec4b(key, values)
    elif node.tag == "array":
        if len(node) == 0:
            serializer.write_bytes_array(key, [])
        else:
            sub_tag = node[0].tag
            arr = []
            for child in node:
                if child.tag != sub_tag:
                    raise ValueError("Array contains multiple types")
                arr.append(child.text)

            if sub_tag == "bytes":
                arr = [bytes.fromhex(x) for x in arr]
                serializer.write_bytes_array(key, arr)
            elif sub_tag == "string":
                serializer.write_string_array(key, arr)
            else:
                raise ValueError("Array contains invalid type: " + sub_tag)
    else:
        raise ValueError("Tag not recognized: " + node.tag)


def xml_to_resource(filename, outfile=None):
    with open(filename, "rb") as f:
        xml = ET.parse(f)
    serializer = ResourceSerializer()

    for child in xml.getroot():
        _xml_to_resource_rec(serializer, child)

    serializer.finalize()
    serializer.to_file(outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert Snapchat lens resource files (.scn, .mesh) to and from xml")
    parser.add_argument("input", help="input filename")
    parser.add_argument("output", help="output filename")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-r", "--resource", action="store_true", help="convert resource file to xml")
    group.add_argument("-x", "--xml", action="store_true", help="convert xml to resource file")
    args = parser.parse_args()

    if args.resource:
        resource_to_xml(args.input, args.output)
    elif args.xml:
        xml_to_resource(args.input, args.output)
