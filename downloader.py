import yaml
import os
import subprocess
import logging
import datetime
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def download_m3u8(filename, url, base_download_dir="downloads"):
    """
    Downloads an m3u8 stream using ffmpeg.
    """
    # Create date-based subfolder
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    target_dir = os.path.join(base_download_dir, date_str)
    os.makedirs(target_dir, exist_ok=True)

    # Prepare output file path
    # We assume filename doesn't have extension, but ffmpeg will handle it if we specify .mp4
    output_file = os.path.join(target_dir, f"{filename}.mp4")

    # ffmpeg command
    # -protocol_whitelist all: allows all protocols (needed for m3u8)
    # -i: input URL
    # -c copy: copy streams without re-encoding (fastest and preserves quality)
    # -bsf:a aac_adtsc: bitstream filter for audio compatibility
    command = [
        "ffmpeg",
        "-protocol_whitelist",
        "file,http,https,tcp,tls,crypto",
        "-i",
        url,
        "-c",
        "copy",
        "-bsf:a",
        "aac_adtsc",
        "-y",  # Overwrite if exists
        output_file,
    ]

    logger.info(f"Starting download: {filename}")
    logger.info(f"URL: {url}")
    logger.info(f"Output: {output_file}")

    retries = 3
    attempt = 0
    success = False

    while attempt < retries and not success:
        attempt += 1
        try:
            # We use subprocess.run. Since ffmpeg doesn't easily report progress to tqdm
            # without complex parsing, we'll rely on ffmpeg's own logging and
            # use tqdm as a simple "active" indicator or just rely on the logs.
            # For a more advanced version, we'd parse ffmpeg stderr.

            # Let's use a simple progress bar to indicate the process is running
            with tqdm(total=1, desc=f"Downloading {filename}", unit="task") as pbar:
                result = subprocess.run(
                    command, capture_output=True, text=True, check=False
                )

                if result.returncode == 0:
                    logger.info(f"Successfully downloaded: {filename}")
                    success = True
                    pbar.update(1)
                else:
                    logger.error(f"Attempt {attempt} failed for {filename}")
                    logger.error(f"FFmpeg Error: {result.stderr}")
                    if attempt < retries:
                        logger.info(f"Retrying in 5 seconds...")
                        import time

                        time.sleep(5)
                    else:
                        logger.error(f"All {retries} attempts failed for {filename}.")
        except Exception as e:
            logger.error(f"An error occurred during download attempt {attempt}: {e}")
            if attempt < retries:
                import time

                time.sleep(5)
            else:
                logger.error(f"Failed to download {filename} after {retries} attempts.")

    return success


def process_downloads(config_file="downloads.yaml", base_download_dir="downloads"):
    if not os.path.exists(config_file):
        logger.error(f"Configuration file '{config_file}' not found.")
        return

    try:
        with open(config_file, "r") as f:
            config_data = yaml.safe_load(f) or []
    except Exception as e:
        logger.error(f"Error reading config file: {e}")
        return

    if not config_data:
        logger.info("No downloads found in the configuration file.")
        return

    # We work on a copy because we might modify the original list
    remaining_downloads = list(config_data)
    completed_downloads = []
    failed_downloads = []

    logger.info(f"Found {len(config_data)} downloads to process.")

    for entry in config_data:
        filename = entry.get("filename")
        url = entry.get("url")

        if not filename or not url:
            logger.warning(f"Skipping invalid entry: {entry}")
            continue

        success = download_m3u8(filename, url, base_download_dir)

        if success:
            completed_downloads.append(entry)
        else:
            failed_downloads.append(entry)

    # Update the config file: Remove successfully downloaded entries
    # The user requested: "the downloader delete that video which it downloaded"
    # We only keep entries that failed or haven't been attempted yet (though here we attempt all)
    # In this implementation, we'll keep only the failed ones in the YAML.

    try:
        with open(config_template_path := config_file, "w") as f:
            yaml.dump(failed_downloads, f, default_flow_style=False)

        logger.info("--- Download Session Summary ---")
        logger.info(f"Successfully completed: {len(completed_downloads)}")
        logger.info(f"Failed: {len(failed_downloads)}")

        if failed_downloads:
            logger.info(
                f"The '{config_file}' has been updated to keep only failed downloads."
            )
        else:
            logger.info(f"All downloads succeeded. '{config_file}' is now empty.")
            if os.path.exists(config_file) and len(failed_downloads) == 0:
                # Optional: delete file if empty
                pass

    except Exception as e:
        logger.error(f"Error updating configuration file: {e}")


if __name__ == "__main__":
    process_downloads()
