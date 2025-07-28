import argparse
import sys
import os

IS_PRODUCTION = getattr(sys, 'frozen', False)

if IS_PRODUCTION:
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-ui', action='store_true', help='Run without UI and append only new channels')
    args = parser.parse_args()

    if args.no_ui:
        from scraper.channel_scraper import fetch_channel_ids, save_new_channels_to_file, load_config
        channel_id, api_key, output_file = load_config(CONFIG_FILE)
        channels = fetch_channel_ids(channel_id, api_key)
        save_new_channels_to_file(channels, output_file)
    else:
        from ui.app_ui import AppUI
        from PySide6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        screen = app.primaryScreen()
        screen_size = screen.size()
        # Desired window size and aspect ratio
        desired_width, desired_height = 600, 800

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
        sys.exit(app.exec())

if __name__ == "__main__":
    main()