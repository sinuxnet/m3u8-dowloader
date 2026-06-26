import datetime
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Optional

import yaml
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DownloadRequest:
    """The Interface: What a caller must provide to initiate a download."""

    filename: str
    url: str
    base_download_dir: str = "downloads"


@dataclass(frozen=True)
class DownloadResult:
    """The Interface: The structured output of a download attempt."""

    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    attempts_made: int = 0


class M3U8Downloader:
    """
    A deep module for downloading m3u8 streams.
    The implementation (ffmpeg, retries, directory management) is hidden
    behind the simple download() interface.
    """

    def download(self, request: DownloadRequest, retries: int = 3) -> DownloadResult:
        """
        Downloads an m3u8 stream using ffmpeg.

        Returns a DownloadResult which provides leverage to the caller
        by encoding the outcome and error details.
        """
        # Create date-based subfolder
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        target_dir = os.path.join(request.base_download_dir, date_str)
        os.makedirs(target_dir, exist_ok=True)

        # Prepare output file path
        output_file = os.path.join(target_dir, f"{request.filename}.mp4")

        # ffmpeg command
        command = [
            "ffmpeg",
            "-protocol_whitelist",
            "file,http,https,tcp,tls,crypto",
            "-i",
            request.url,
            "-c",
            "copy",
            "-bsf:a",
            "aac_adtsc",
            "-y",
            output_file,
        ]

        logger.info(f"Starting download: {request.filename}")
        logger.info(f"URL: {request.url}")
        logger.info(f"Output: {output_file}")

        attempt = 0
        success = False
        last_error = None

        while attempt < retries and not success:
            attempt += 1
            try:
                with tqdm(
                    total=1,
                    desc=f"Downloading {request.filename}",
                    unit="task",
                    leave=False,
                ) as pbar:
                    result = subprocess.run(
                        command, capture_output=True, text=True, check=False
                    )

                    if result.returncode == 0:
                        logger.info(f"Successfully downloaded: {request.filename}")
                        success = True
                        pbar.update(1)
                    else:
                        last_error = result.stderr
                        logger.error(f"Attempt {attempt} failed for {request.filename}")
                        if attempt < retries:
                            logger.info("Retrying in 5 seconds...")
                            time.sleep(5)
                        else:
                            logger.error(
                                f"All {retries} attempts failed for {request.filename}."
                            )
            except Exception as e:
                last_error = str(e)
                logger.error(
                    f"An error occurred during download attempt {attempt}: {e}"
                )
                if attempt < retries:
                    time.sleep(5)
                else:
                    logger.error(
                        f"Failed to download {request.filename} "
                        f"after {retries} attempts."
                    )

        return DownloadResult(
            success=success,
            output_path=output_file if success else None,
            error_message=last_error,
            attempts_made=attempt,
        )


class DownloadOrchestrator:
    """
    Orchestrates the processing of multiple downloads from a configuration file.
    """

    def __init__(self, downloader: M3U8Downloader):
        self.downloader = downloader

    def process_config(
        self, config_file: str, base_download_dir: str = "downloads"
    ) -> None:
        if not os.path.exists(config_file):
            logger.error(f"Configuration file '{config_file}' not found.")
            return

        try:
            with open(config_file) as f:
                config_data: list[dict[str, Any]] = yaml.safe_load(f) or []
        except Exception as e:
            logger.error(f"Error reading config file: {e}")
            return

        if not config_data:
            logger.info("No downloads found in the configuration to process.")
            return

        logger.info(f"Found {len(config_data)} downloads to process.")

        completed_downloads: list[dict[str, Any]] = []
        failed_downloads: list[dict[str, Any]] = []

        for entry in config_data:
            filename = entry.get("filename")
            url = entry.get("url")

            if not filename or not url:
                logger.warning(f"Skipping invalid entry: {entry}")
                continue

            request = DownloadRequest(
                filename=filename, url=url, base_download_dir=base_download_dir
            )

            result = self.downloader.download(request)

            if result.success:
                completed_downloads.append(entry)
            else:
                failed_downloads.append(entry)
                logger.error(
                    f"Failed download: {filename}. Error: {result.error_message}"
                )

        try:
            with open(config_file, "w") as f:
                yaml.dump(failed_downloads, f, default_flow_style=False)

            logger.info("--- Download Session Summary ---")
            logger.info(f"Successfully completed: {len(completed_downloads)}")
            logger.info(f"Failed: {len(failed_downloads)}")

            if failed_downloads:
                logger.info(
                    f"The '{config_file}' has been updated to keep failed downloads."
                )
            else:
                logger.info(f"All downloads succeeded. '{config_file}' is now empty.")
        except Exception as e:
            logger.error(f"Error updating configuration file: {e}")
