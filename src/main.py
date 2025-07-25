import sys
import argparse
from scraper.channel_scraper import fetch_channel_ids, save_new_channels_to_file, load_config
from ui.app_ui import AppUI
from PyQt5.QtWidgets import QApplication

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-ui', action='store_true', help='Run without UI and append only new channels')
    args = parser.parse_args()

    if args.no_ui:
        channel_id, api_key, output_file = load_config()
        channels = fetch_channel_ids(channel_id, api_key)
        save_new_channels_to_file(channels, output_file)
    else:
        app = QApplication(sys.argv)
        screen = app.primaryScreen()
        screen_size = screen.size()
        # Desired window size and aspect ratio
        desired_width, desired_height = 600, 800
        aspect_ratio = desired_width / desired_height

        # Check if screen can support the desired size
        if screen_size.width() < desired_width or screen_size.height() < desired_height:
            # Scale down while keeping aspect ratio
            scale_w = screen_size.width() / desired_width
            scale_h = screen_size.height() / desired_height
            scale = min(scale_w, scale_h, 1.0)
            width = int(desired_width * scale)
            height = int(desired_height * scale)
        else:
            width, height = desired_width, desired_height

        window = AppUI()
        window.resize(width, height)
        window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()