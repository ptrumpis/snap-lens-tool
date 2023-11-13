import os
import re
import shutil
import tempfile

from lxml import etree

from .lens_packer import LensPacker


class LensPatcher:
    def __init__(self, log_function=print):
        self.log_function = log_function
        self.packer = LensPacker(log_function)
        self.temp_dir = None
        self.temp_file = None

    def __del__(self):
        self.close()

    def log(self, str):
        if self.log_function:
            self.log_function(str)

    def open(self, input):
        if self.temp_dir is not None:
            raise Exception('Call close() method before opening another file.')

        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, os.path.splitext(os.path.basename(input))[0])

        self.log(f"Using Temp Dir: {self.temp_dir}")

        self.packer.unpack(input, self.temp_file)

    def write(self, output):
        temp_packed_file = f"{self.temp_file}.lns"
        if os.path.exists(temp_packed_file):
            os.remove(temp_packed_file)

        self.packer.pack(self.temp_file, temp_packed_file)
        self.log(f"Writing Lens to: {output}")

        try:
            shutil.copy(temp_packed_file, output)
        except FileNotFoundError as e:
            self.log(f"Error copying file: {e}")
        except Exception as e:
            self.log(f"General error: {e}")

    def close(self):
        if self.temp_dir is not None:
            self.log(f"Removing Temp Dir: {self.temp_dir}")

            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            self.temp_file = None

    def disable_fallback(self):
        if self.temp_file is None:
            raise Exception('No file has been opened.')

        self.log(f"Trying to disable LensMode Fallback on: {self.temp_file}")

        xml_file = os.path.join(self.temp_file, f"_scene_scn.xml")
        if not os.path.exists(xml_file) or not os.path.isfile(xml_file):
            self.log(f"Could not find {xml_file}")
            return False

        lens_mode_ctrl = self._find_lens_mode_controller_js(xml_file)
        if lens_mode_ctrl is None:
            self.log(f"Unable to detect LensModeController.js file")
            return False

        lens_mode_ctrl_path = os.path.normpath(os.path.join(self.temp_file, lens_mode_ctrl))
        self.log(f"Found LensModeController: {lens_mode_ctrl}")

        self._set_fallback_false(lens_mode_ctrl_path)
        self.log(f"LensMode Fallback has been disabled")

        return True

    def _find_lens_mode_controller_js(self, scene_xml_file):
        target_name = "Scripts/LensModeController.js"
        target_path = None

        tree = etree.parse(scene_xml_file)
        root = tree.getroot()

        for block in root.findall('.//block'):
            name_element = block.find('./string[@key="name"]')

            if name_element is not None and name_element.text == target_name:
                fileinfo_element = block.find('.//block[@key="fileinfo"]')

                if fileinfo_element is not None:
                    path_element = fileinfo_element.find('./string[@key="path"]')

                    if path_element is not None:
                        target_path = path_element.text
                        break

        return target_path

    def _set_fallback_false(self, lens_mode_ctrl_file):
        with open(lens_mode_ctrl_file, 'r') as file:
            code = file.read()

        code = re.sub(r'(function setLensMode\(isFallback\)\s*{(\s*))', r'\1isFallback = false;\n\2', code, count=1)

        with open(lens_mode_ctrl_file, 'w') as file:
            file.write(code)
