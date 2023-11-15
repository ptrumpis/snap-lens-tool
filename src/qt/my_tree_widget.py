import os

from PyQt5.QtCore import QFileInfo, pyqtSignal
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView


class MyTreeWidget(QTreeWidget):
    filesChanged = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self._files = {}
        self._folders = {}

        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)

    def getFiles(self):
        return list(self._files.keys())

    def getFolders(self):
        return list(self._folders.keys())

    def clear(self):
        super().clear()
        self._files.clear()
        self._folders.clear()

        self.filesChanged.emit()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.addFiles([url.toLocalFile().removeprefix("file:///") for url in event.mimeData().urls()])

    def selectedFiles(self):
        return [os.path.normpath(item.text(0)) for item in self.selectedItems()]

    def addFiles(self, files):
        if not isinstance(files, list):
            files = [files]

        for file in files:
            file = os.path.normpath(file)

            if file not in self._files and file not in self._folders:
                info = QFileInfo(file)
                if info.isFile():
                    item = QTreeWidgetItem([file, info.suffix(), "{:.2f} KB".format(info.size() / 1024.0)])
                    self._files[file] = item
                else:
                    item = QTreeWidgetItem([file, "Folder", ""])
                    self._folders[file] = item

                self.addTopLevelItem(item)

                self.filesChanged.emit()

    def addFolders(self, folders):
        return self.addFiles(folders)

    def removeFiles(self, files):
        if not isinstance(files, list):
            files = [files]

        for file in files:
            file = os.path.normpath(file)
            item = self._files.get(file) or self._folders.get(file)
            if item is not None:
                index = self.indexOfTopLevelItem(item)
                if index != -1:
                    self.takeTopLevelItem(index)

                self._files.pop(file, None)
                self._folders.pop(file, None)

                self.filesChanged.emit()

        def removeFolders(self, folders):
            return self.removeFiles(folders)