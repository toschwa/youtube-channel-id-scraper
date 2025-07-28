from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QVBoxLayout, QMessageBox, QAbstractItemView, QProgressDialog, QHBoxLayout,
    QComboBox, QFrame, QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap
import os
import json
import urllib.request
from scraper.channel_scraper import fetch_channel_ids
from main import CONFIG_FILE, BASE_DIR

THUMB_CACHE_DIR = os.path.join(BASE_DIR, "thumb_cache")
os.makedirs(THUMB_CACHE_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(BASE_DIR, "channels.yml")

class FetchChannelsThread(QThread):
    result = Signal(list)
    error = Signal(str)
    progress = Signal(int, int)  # current, total

    def __init__(self, channel_id, api_key):
        super().__init__()
        self.channel_id = channel_id
        self.api_key = api_key

    def run(self):
        import concurrent.futures

        def fetch_thumb(ch):
            thumb_url = ch.get('thumbnail')
            cache_path = os.path.join(THUMB_CACHE_DIR, f"{ch['id']}.jpg")
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, "rb") as f:
                        ch['icon_data'] = f.read()
                    return ch
                except Exception:
                    pass  # fallback to download
            if thumb_url:
                try:
                    data = urllib.request.urlopen(thumb_url).read()
                    ch['icon_data'] = data
                    with open(cache_path, "wb") as f:
                        f.write(data)
                except Exception:
                    ch['icon_data'] = None
            else:
                ch['icon_data'] = None
            return ch

        try:
            channels = fetch_channel_ids(self.channel_id, self.api_key)
            total = len(channels)
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                results = []
                for idx, ch in enumerate(executor.map(fetch_thumb, channels)):
                    results.append(ch)
                    self.progress.emit(idx + 1, total)
            self.result.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class AppUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Channel ID Scraper")
        self.channels = []
        self.setup_ui()
        self.load_config_on_startup()
        self.fetch_thread = None
        self.progress_dialog = None

    def setup_ui(self):
        layout = QVBoxLayout()

        # Channel ID
        self.label_channel_id = QLabel("Channel ID:")
        self.entry_channel_id = QLineEdit()
        layout.addWidget(self.label_channel_id)
        layout.addWidget(self.entry_channel_id)

        # Channel ID help link
        self.link_channel_id = QLabel(
            '<a href="https://www.youtube.com/account_advanced">Find your Channel ID</a>'
        )
        self.link_channel_id.setOpenExternalLinks(True)
        self.link_channel_id.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        layout.addWidget(self.link_channel_id)

        # API Key
        self.label_api_key = QLabel("API Key:")
        self.entry_api_key = QLineEdit()
        self.entry_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.label_api_key)
        layout.addWidget(self.entry_api_key)

        # API Key help link
        self.link_api_key = QLabel(
            '<a href="https://console.cloud.google.com/apis/api/youtube.googleapis.com/credentials">Get your API Key</a>'
        )
        self.link_api_key.setOpenExternalLinks(True)
        self.link_api_key.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        layout.addWidget(self.link_api_key)

        # Output File
        self.label_output_file = QLabel("Output Filepath:")
        output_file_layout = QHBoxLayout()
        self.entry_output_file = QLineEdit()
        self.button_browse_output = QPushButton("Browse")
        self.button_browse_output.clicked.connect(self.browse_output_file)
        output_file_layout.addWidget(self.entry_output_file)
        output_file_layout.addWidget(self.button_browse_output)
        layout.addWidget(self.label_output_file)
        layout.addLayout(output_file_layout)

        # Save Config Button
        self.button_save_config = QPushButton("Save Config")
        self.button_save_config.clicked.connect(self.save_config)
        layout.addWidget(self.button_save_config)
        self.button_save_config.setToolTip("Saves Channel ID and API Key to config.json")

        # Extra padding above divider
        layout.addSpacing(12)

        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(divider)

        # Extra padding below divider
        layout.addSpacing(12)

        # Sort ComboBox
        sort_layout = QHBoxLayout()
        self.button_fetch = QPushButton("Fetch Channels")
        self.button_fetch.clicked.connect(self.fetch_channels)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Sort: Alphabetically", "Sort: By Subscription Date"])
        self.sort_combo.currentIndexChanged.connect(self.sort_and_display_channels)
        sort_layout.addWidget(self.button_fetch, 2)  # 2/3 of space
        sort_layout.addStretch(0)
        sort_layout.addWidget(self.sort_combo, 1)    # 1/3 of space
        layout.addLayout(sort_layout)

        # Loading label
        self.loading_label = QLabel("")
        layout.addWidget(self.loading_label)

        # List Widget for channels
        self.listbox_channels = QListWidget()
        self.listbox_channels.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.listbox_channels.setIconSize(QSize(48, 48))
        self.listbox_channels.itemSelectionChanged.connect(self.update_selected_count)
        layout.addWidget(self.listbox_channels)

        # Selected count label
        self.selected_count_label = QLabel("Selected: 0")
        layout.addWidget(self.selected_count_label)

        # Save Button
        self.button_save = QPushButton("Save Selected Channels")
        self.button_save.clicked.connect(self.save_selected_channels)
        layout.addWidget(self.button_save)

        self.setLayout(layout)

    def fetch_channels(self):
        channel_id = self.entry_channel_id.text()
        api_key = self.entry_api_key.text()

        if not channel_id or not api_key:
            QMessageBox.critical(self, "Input Error", "Please enter both Channel ID and API Key.")
            return

        self.loading_label.setText("Loading channels, please wait...")
        self.button_fetch.setEnabled(False)
        self.listbox_channels.clear()

        self.progress_dialog = QProgressDialog("Fetching channels...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowTitle("Loading")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()

        self.fetch_thread = FetchChannelsThread(channel_id, api_key)
        self.fetch_thread.result.connect(self.on_channels_fetched)
        self.fetch_thread.error.connect(self.on_fetch_error)
        self.fetch_thread.progress.connect(self.on_fetch_progress)
        self.fetch_thread.finished.connect(self.progress_dialog.close)
        self.progress_dialog.canceled.connect(self.fetch_thread.terminate)
        self.fetch_thread.start()

    def on_fetch_progress(self, current, total):
        if self.progress_dialog:
            percent = int((current / total) * 100) if total else 0
            self.progress_dialog.setMaximum(100)
            self.progress_dialog.setValue(percent)
            self.progress_dialog.setLabelText(f"Downloading thumbnails... ({current}/{total})")

    def on_channels_fetched(self, channels):
        self.loading_label.setText("")
        self.button_fetch.setEnabled(True)
        self.channels = channels  # Store for sorting
        if self.progress_dialog:
            self.progress_dialog.close()
        self.sort_and_display_channels()

    def sort_and_display_channels(self):
        self.listbox_channels.clear()
        if self.sort_combo.currentIndex() == 0:
            # Alphabetically by title
            sorted_channels = sorted(self.channels, key=lambda ch: ch['title'].lower())
        else:
            # By subscription date (descending, most recent first)
            sorted_channels = sorted(
                self.channels,
                key=lambda ch: ch.get('publishedAt') or "",
                reverse=True
            )
        for ch in sorted_channels:
            icon = None
            if ch.get('icon_data'):
                pixmap = QPixmap()
                pixmap.loadFromData(ch['icon_data'])
                icon = QIcon(pixmap)
            # Custom widget for each item
            widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(10, 6, 10, 6)
            label_title = QLabel(ch['title'])
            label_id = QLabel(ch['id'])
            label_id.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label_id.setStyleSheet("color: gray; font-family: monospace;")
            layout.addWidget(label_title, 2)
            layout.addWidget(label_id, 1)
            widget.setLayout(layout)
            item = QListWidgetItem()
            if icon:
                item.setIcon(icon)
            item.setSizeHint(QSize(0, self.listbox_channels.iconSize().height() + 16))
            item.setData(32, ch['id'])  # 32 is Qt.UserRole
            self.listbox_channels.addItem(item)
            self.listbox_channels.setItemWidget(item, widget)
        self.update_selected_count()

    def update_selected_count(self):
        count = len(self.listbox_channels.selectedItems())
        self.selected_count_label.setText(f"Selected: {count}")

    def on_fetch_error(self, error_msg):
        self.loading_label.setText("")
        self.button_fetch.setEnabled(True)
        if self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.critical(self, "Fetch Error", error_msg)

    def load_config_on_startup(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                self.entry_channel_id.setText(config.get("channel_id", ""))
                self.entry_api_key.setText(config.get("api_key", ""))
                self.entry_output_file.setText(config.get("output_file", OUTPUT_FILE))
            except Exception as e:
                QMessageBox.warning(self, "Config Error", f"Failed to load config: {e}")

    def save_config(self):
        config = {
            "channel_id": self.entry_channel_id.text(),
            "api_key": self.entry_api_key.text(),
            "output_file": self.entry_output_file.text()
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            QMessageBox.information(self, "Config Saved", "Configuration saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save config: {e}")

    def browse_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Select Output File", "", "YAML Files (*.yml);;All Files (*)")
        if file_path:
            self.entry_output_file.setText(file_path)

    def save_selected_channels(self):
        output_file = self.entry_output_file.text() or OUTPUT_FILE
        selected_items = self.listbox_channels.selectedItems()
        selected_channels = [item.data(32) for item in selected_items]

        if not selected_channels:
            QMessageBox.warning(self, "Selection Error", "No channels selected.")
            return

        try:
            with open(output_file, "w") as f:
                for channel in selected_channels:
                    f.write(f"- {channel}\n")
            QMessageBox.information(self, "Success", f"Selected channels saved to {output_file}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = AppUI()
    window.show()
    sys.exit(app.exec_())