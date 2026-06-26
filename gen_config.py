import yaml
import validators
import os


def generate_config(config_file="downloads.yaml"):
    print("--- M3U8 Download Configuration Generator ---")

    # Load existing config if it exists
    config_data = []
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f) or []
        except Exception as e:
            print(f"Error reading existing config: {e}")
            config_data = []

    while True:
        filename = input(
            "\nEnter filename (or press Enter to finish, 'q' to quit): "
        ).strip()
        if filename.lower() == "q":
            break
        if not filename:
            break

        url = input(f"Enter m3u8 URL for '{filename}': ").strip()

        if not validators.url(url):
            print("Error: Invalid URL format. Please try again.")
            continue

        # Add new entry
        config_data.append({"filename": filename, "url": url})
        print(f"Added: {filename}")

    # Save back to file
    try:
        with open(config_file, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False)
        print(
            f"\nConfiguration saved to {config_file}. Total entries: {len(config_data)}"
        )
    except Exception as e:
        print(f"Error saving config: {e}")


if __name__ == "__main__":
    generate_config()
