import os
from typing import Any

import validators
import yaml


class ConfigManager:
    """
    Handles configuration for m3u8 downloads.
    """

    def __init__(self, config_file: str = "downloads.yaml") -> None:
        self.config_file = config_file

    def load_config(self) -> list[dict[str, Any]]:
        """Loads the configuration from the file."""
        if not os.path.exists(self.config_file):
            return []
        try:
            with open(self.config_file) as f:
                return yaml.safe_load(f) or []
        except Exception as e:
            print(f"Error reading config file: {e}")
            return []

    def save_config(self, config_data: list[dict[str, Any]]) -> None:
        """Saves the configuration to the file."""
        try:
            with open(self.config_file, "w") as f:
                yaml.dump(config_data, f, default_flow_style=False)
            print(
                f"Configuration saved to {self.config_file}. "
                f"Total entries: {len(config_data)}"
            )
        except Exception as e:
            print(f"Error saving config: {e}")

    def add_entry(self, filename: str, url: str) -> bool:
        """Adds a new entry to the config. Returns True if successful."""
        if not validators.url(url):
            print(f"Error: Invalid URL format for '{url}'.")
            return False

        config_data = self.load_config()
        config_data.append({"filename": filename, "url": url})
        self.save_config(config_data)
        print(f"Added: {filename}")
        return True

    def interactive_generator(self) -> None:
        """Interactive config generator (migrated from gen_config.py)."""

        print("--- M3U8 Download Configuration Generator ---")

        while True:
            filename = input(
                "\nEnter filename (or press Enter to finish, 'q' to quit): "
            ).strip()

            if filename.lower() == "q" or not filename:
                break

            url = input(f"Enter m3u8 URL for '{filename}': ").strip()

            if self.add_entry(filename, url):
                pass
            else:
                print("Failed to add entry. Check URL format.")

        print("\nSession finished.")
