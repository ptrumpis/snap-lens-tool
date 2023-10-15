import os
import re
import sys

from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog

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
        output_path = os.path.join(file_dir, f"_{file_name}")

        lns_tool.extract(file_path, output=output_path)

        self.__convert_resources_to_xml(output_path)

    def __repack(self, dir_path):
        print(f"Re-packing Lens: {dir_path}")

        self.__convert_xml_to_resources(dir_path)

        lns_tool.create(dir_path)

    def __convert_resources_to_xml(self, dir_path):
        for root, dirs, files in os.walk(dir_path):
            for file_name in files:
                if file_name.endswith((".scn", ".mesh")):
                    resource_file = os.path.join(root, file_name)
                    print(f"Converting Resource: {resource_file}")

                    resource_dir = os.path.dirname(resource_file)
                    resource_name, resource_ext = os.path.splitext(os.path.basename(resource_file))
                    xml_file = os.path.join(resource_dir, f"_{resource_name}_{resource_ext}.xml")

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
                        resource_ext = ".scn"
                    elif xml_name.endswith("_mesh"):
                        resource_ext = ".mesh"
                    else:
                        continue

                    resource_file = os.path.join(xml_dir, f"_{xml_name}.{resource_ext}")
                    resource_tool.xml_to_resource(xml_file, resource_file)

    def __fallback(self, file_path):
        print(f"Fallback: {file_path}")


if __name__ == '__main__':
    app = App()
    app.run()
