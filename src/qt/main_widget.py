import os

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from .download_widget import DownloadWidget
from ..core.lens_packer import LensPacker
from ..core.lens_patcher import LensPatcher


class MainWidget(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.packer = LensPacker(self.log)
        self.patcher = LensPatcher(self.log)

        uic.loadUi('main.ui', self)

        self.addFilesButton.clicked.connect(self.onAddFilesButtonClicked)
        self.addFolderButton.clicked.connect(self.onAddFolderButtonClicked)
        self.removeButton.clicked.connect(self.onRemoveButtonClicked)
        self.clearButton.clicked.connect(self.onClearButtonClicked)
        self.unpackButton.clicked.connect(self.onUnpackButtonClicked)
        self.repackButton.clicked.connect(self.onRepackButtonClicked)
        self.disableFallbackButton.clicked.connect(self.onDisableFallbackButtonClicked)
        self.downloadButton.clicked.connect(self.onDownloadButtonClicked)
        self.treeWidget.itemSelectionChanged.connect(self.onItemSelectionChanged)
        self.treeWidget.filesChanged.connect(self.onFilesChanged)

        self.toggleButtons()

    def onAddFilesButtonClicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly | QFileDialog.ExistingFile
        files, _ = QFileDialog.getOpenFileNames(self, "Select lens files", "",
                                                "Lens files (*.lns);;All Files (*)", options=options)
        if not files:
            return

        self.treeWidget.addFiles(files)

    def onAddFolderButtonClicked(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder", "")
        if not folder:
            return

        self.treeWidget.addFolders(folder)

    def onRemoveButtonClicked(self):
        selectedFiles = self.treeWidget.selectedFiles()
        self.treeWidget.removeFiles(selectedFiles)

    def onClearButtonClicked(self):
        self.treeWidget.clear()

    def onUnpackButtonClicked(self):
        files = self.treeWidget.getFiles()
        if not files:
            return

        initialDir = os.path.dirname(files[0])
        targetDir = QFileDialog.getExistingDirectory(self, "Select target directory for unpacking", initialDir)
        if targetDir is None:
            return

        targetDir = os.path.normpath(targetDir)
        for file in files:
            outputName = os.path.splitext(os.path.basename(file))[0]
            outputPath = os.path.join(targetDir, outputName)
            i = 1
            while (os.path.exists(outputPath)):
                outputPath = os.path.join(targetDir, f"{outputName} ({i})")

            self.packer.unpack(file, outputPath)

    def onRepackButtonClicked(self):
        folders = self.treeWidget.getFolders()
        if not folders:
            return

        initialDir = folders[0]
        targetDir = QFileDialog.getExistingDirectory(self, "Select target directory for re-packing", initialDir)
        if targetDir is None:
            return

        targetDir = os.path.normpath(targetDir)
        for folder in folders:
            outputName = f"{os.path.basename(folder)}.lns"
            outputPath = os.path.join(targetDir, outputName)
            i = 1
            while (os.path.exists(outputPath)):
                outputPath = os.path.join(targetDir, f"{os.path.basename(folder)} ({i}).lns")

            self.packer.pack(folder, outputPath)

    def onDisableFallbackButtonClicked(self):
        files = self.treeWidget.getFiles()
        if not files:
            return

        initialDir = os.path.dirname(files[0])
        targetDir = QFileDialog.getExistingDirectory(self, "Select target directory for saving", initialDir)
        if targetDir is None:
            return

        targetDir = os.path.normpath(targetDir)
        for file in files:
            outputName, outputExt = os.path.splitext(os.path.basename(file))
            outputPath = os.path.join(targetDir, f"{outputName}{outputExt}")
            i = 1
            while (os.path.exists(outputPath)):
                outputPath = os.path.join(targetDir, f"{outputName} ({i}){outputExt}")

            self.patcher.open(file)
            self.patcher.disable_fallback()
            self.patcher.write(outputPath)
            self.patcher.close()

    def onDownloadButtonClicked(self):
        downloadWidget = DownloadWidget(self, self.log)
        downloadWidget.show()

    def onItemSelectionChanged(self):
        self.toggleButtons()

    def onFilesChanged(self):
        self.toggleButtons()

    def toggleButtons(self):
        self.clearButton.setEnabled(self.treeWidget.topLevelItemCount())
        self.removeButton.setEnabled(len(self.treeWidget.selectedItems()) > 0)
        self.unpackButton.setEnabled(len(self.treeWidget.getFiles()) > 0)
        self.repackButton.setEnabled(len(self.treeWidget.getFolders()) > 0)
        self.disableFallbackButton.setEnabled(len(self.treeWidget.getFiles()) > 0)

    def log(self, message):
        # self.log_output.appendPlainText(message)
        print(message)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selectedFiles = self.treeWidget.selectedFiles()
            self.treeWidget.removeFiles(selectedFiles)
        elif event.key() == Qt.Key_Escape:
            self.treeWidget.clearSelection()
        else:
            super().keyPressEvent(event)
