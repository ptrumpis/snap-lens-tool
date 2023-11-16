import json
from io import BytesIO

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton, QDialog, QVBoxLayout, QLineEdit, QLabel, QFileDialog

from ..core.lens_crawler import LensCrawler


class DownloadWidget(QDialog):
    def __init__(self, parent, log_function=print):
        super().__init__(parent)
        self.download_url = None
        self.log_function = log_function

        self.setWindowTitle("Lens Download")
        self.layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Lens Share URL")

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_data)

        self.label_lens_name = QLabel()
        self.label_lens_id = QLabel()
        self.label_thumbnail = QLabel()
        self.label_snapcode = QLabel()

        self.download_button = QPushButton("Download Lens Resource")
        self.download_button.clicked.connect(self.download_resource)
        self.download_button.setEnabled(False)

        self.layout.addWidget(self.url_input)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.label_lens_name)
        self.layout.addWidget(self.label_lens_id)
        self.layout.addWidget(self.label_thumbnail)
        self.layout.addWidget(self.label_snapcode)
        self.layout.addWidget(self.download_button)

        self.setLayout(self.layout)

    def log(self, str):
        if self.log_function:
            self.log_function(str)

    def search_data(self):
        url = self.url_input.text().strip()
        if url:
            lens_crawler = LensCrawler(self.log_function)
            lens = lens_crawler.get_lens(url)
            if lens is not None:
                self.log(f"Lens Meta {lens}")

                lens_name = lens["lens_name"]
                lens_id = lens["lens_id"]
                thumbnail_url = lens["thumbnail_media_url"]
                snapcode_url = lens["snapcode_url"]
                archive_link = lens["lens_url"]

                self.label_lens_name.setText(f"Lens Name: {lens_name}")
                self.label_lens_name.setAlignment(Qt.AlignCenter)

                self.label_lens_id.setText(f"Lens ID: {lens_id}")
                self.label_lens_id.setAlignment(Qt.AlignCenter)

                self.label_thumbnail.setPixmap(self.image_url_to_pixmap(thumbnail_url))
                self.label_thumbnail.setAlignment(Qt.AlignCenter)

                self.label_snapcode.setPixmap(self.image_url_to_pixmap(snapcode_url, 150))
                self.label_snapcode.setAlignment(Qt.AlignCenter)

                self.download_button.setEnabled(True)
                self.download_url = archive_link

    def image_url_to_pixmap(self, url, max_size=200):
        try:
            response = requests.get(url)
            response.raise_for_status()

            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data.getvalue())

            return pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio)
        except requests.HTTPError as e:
            self.log(e)
        except Exception as e:
            self.log(f"Error loading image: {e}")

        return None

    def download_resource(self):
        if self.download_url is not None:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Lens Resource", "",
                                                       "Lens Files (*.lns);;All Files (*)")
            if save_path:
                response = requests.get(self.download_url)
                with open(save_path, "wb") as file:
                    file.write(response.content)
