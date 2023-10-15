import os
import re
import shutil
import sys
import tempfile

from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog
from lxml import etree

import src.lns_tool as lns_tool
import src.resource_tool as resource_tool
from src.qt.dialog import Ui_Dialog


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.Dialog = QDialog()
        self.ui = Ui_Dialog()
        self.init_ui()

    def init_ui(self):
        self.ui.setupUi(self.Dialog)
        self.ui.unpackButton.clicked.connect(self.unpack_clicked)
        self.ui.repackButton.clicked.connect(self.repack_clicked)
        self.ui.fallbackButton.clicked.connect(self.fallback_clicked)

    def unpack_clicked(self):
        file_dialog = QFileDialog(self.Dialog)
        file_dialog.setNameFilter("LNS-Files (*.lns)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            selected_file = os.path.normpath(selected_file)
            self.__unpack(selected_file)

    def repack_clicked(self):
        dir_dialog = QFileDialog.getExistingDirectory(self.Dialog, 'Select unpacked lens folder')
        if dir_dialog:
            dir_dialog = os.path.normpath(dir_dialog)
            self.__repack(dir_dialog)

    def fallback_clicked(self):
        file_dialog = QFileDialog(self.Dialog)
        file_dialog.setNameFilter("LNS-Files (*.lns)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            selected_file = os.path.normpath(selected_file)
            self.__fallback(selected_file)

    def run(self):
        self.Dialog.show()
        sys.exit(self.app.exec_())

    def __unpack(self, file_path):
        print(f"Unpacking Lens: {file_path}")

        file_dir = os.path.dirname(file_path)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = os.path.join(file_dir, f"{file_name}_unpacked")

        lns_tool.extract(file_path, output=output_path)

        self.__convert_resources_to_xml(output_path)

    def __repack(self, dir_path):
        print(f"Re-packing Lens: {dir_path}")

        self.__convert_xml_to_resources(dir_path)

        lns_tool.create(dir_path, file_ext=".lns")

    def __convert_resources_to_xml(self, dir_path):
        for root, dirs, files in os.walk(dir_path):
            for file_name in files:
                if file_name.endswith((".scn", ".mesh")):
                    resource_file = os.path.join(root, file_name)
                    print(f"Converting Resource: {resource_file}")

                    resource_dir = os.path.dirname(resource_file)
                    resource_name, resource_ext = os.path.splitext(os.path.basename(resource_file))
                    postfix = resource_ext.lstrip('.')
                    xml_file = os.path.join(resource_dir, f"_{resource_name}_{postfix}.xml")
                    print(f"To XML: {xml_file}")

                    resource_tool.resource_to_xml(resource_file, xml_file)

    def __convert_xml_to_resources(self, dir_path):
        pattern = r"^_.+\.xml$"
        for root, dirs, files in os.walk(dir_path):
            for file_name in files:
                if re.match(pattern, file_name):
                    xml_file = os.path.join(root, file_name)
                    print(f"Converting XML: {xml_file}")

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
                    print(f"To Resource: {resource_file}")

                    resource_tool.xml_to_resource(xml_file, resource_file)

    def __fallback(self, file_path):
        print(f"Patching Fallback Mode on: {file_path}")

        temp_dir = tempfile.mkdtemp()
        print("Using temp dir:", temp_dir)

        lens_dir = os.path.dirname(file_path)
        lens_file, lens_ext = os.path.splitext(os.path.basename(file_path))
        lens_path = os.path.join(temp_dir, lens_file)

        lns_tool.extract(file_path, output=lens_path)

        scn_file = os.path.join(lens_path, f"scene.scn")
        xml_file = os.path.join(lens_path, f"_scene.xml")

        if not os.path.exists(scn_file) or not os.path.isfile(scn_file):
            print(f"Could not find {scn_file}")
            return

        resource_tool.resource_to_xml(scn_file, xml_file)

        if not os.path.exists(xml_file) or not os.path.isfile(xml_file):
            print(f"Could not find {xml_file}")
            return

        lens_mode_ctrl = self.__find_lens_mode_controller_js(xml_file)
        if lens_mode_ctrl is None:
            print(f"Unable to detect LensModeController.js file")
            return

        lens_mode_ctrl_path = os.path.normpath(os.path.join(lens_path, lens_mode_ctrl))
        print(f"Found LensModeController: {lens_mode_ctrl}")

        self.__set_fallback_false(lens_mode_ctrl_path)

        lns_tool.create(lens_path, file_ext=lens_ext)

        src_file = f"{lens_path}{lens_ext}"
        dst_file = os.path.join(lens_dir, f"{lens_file}_patched{lens_ext}")

        try:
            shutil.copy(src_file, dst_file)
            print(f"Patched Lens: {dst_file}")
        except FileNotFoundError as e:
            print(f"Error copying file: {e}")
        except Exception as e:
            print(f"General error: {e}")

        shutil.rmtree(temp_dir)

    def __find_lens_mode_controller_js(self, scene_xml_file):
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

    def __set_fallback_false(self, lens_mode_ctrl_file):
        with open(lens_mode_ctrl_file, 'r') as file:
            code = file.read()

        code = re.sub(r'(function setLensMode\(isFallback\)\s*{(\s*))', r'\1isFallback = false;\n\2', code, count=1)

        with open(lens_mode_ctrl_file, 'w') as file:
            file.write(code)


if __name__ == '__main__':
    app = App()
    app.run()
