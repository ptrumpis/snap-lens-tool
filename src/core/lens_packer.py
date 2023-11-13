import os
import re

from ..tools.lns_tool import create, extract
from ..tools.resource_tool import resource_to_xml, xml_to_resource


class LensPacker:
    def __init__(self, log_function=print):
        self.log_function = log_function

    def log(self, str):
        if self.log_function:
            self.log_function(str)

    def pack(self, input_dir, output_file):
        self.log(f"Packing Lens: {input_dir}")
        self._dir_to_resources(input_dir)
        create(input_dir, output_file)

    def unpack(self, input_file, output_dir):
        self.log(f"Unpacking Lens: {input_file}")
        extract(input_file, output_dir)
        self._dir_to_xml(output_dir)

    def _dir_to_xml(self, dir_path):
        for root, dirs, files in os.walk(dir_path):
            for file_name in files:
                if file_name.endswith((".scn", ".mesh")):
                    resource_file = os.path.join(root, file_name)

                    self.log(f"Converting Resource to XML: {resource_file}")

                    resource_dir = os.path.dirname(resource_file)
                    resource_name, resource_ext = os.path.splitext(os.path.basename(resource_file))
                    postfix = resource_ext.lstrip('.')
                    xml_file = os.path.join(resource_dir, f"_{resource_name}_{postfix}.xml")

                    resource_to_xml(resource_file, xml_file)

    def _dir_to_resources(self, dir_path):
        pattern = r"^_.+\.xml$"
        for root, dirs, files in os.walk(dir_path):
            for file_name in files:
                if re.match(pattern, file_name):
                    xml_file = os.path.join(root, file_name)

                    self.log(f"Converting XML to Resource: {xml_file}")

                    xml_dir = os.path.dirname(xml_file)
                    xml_name = os.path.splitext(os.path.basename(xml_file))[0]
                    if xml_name.endswith("_scn"):
                        resource_name = xml_name[1:-len("_scn")]
                        resource_ext = ".scn"
                    elif xml_name.endswith("_mesh"):
                        resource_name = xml_name[1:-len("_mesh")]
                        resource_ext = ".mesh"
                    else:
                        continue

                    resource_file = os.path.join(xml_dir, f"{resource_name}{resource_ext}")

                    xml_to_resource(xml_file, resource_file)
