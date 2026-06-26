import os
import sys

# Add src to sys.path to ensure we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from m3u8_downloader.downloader import M3U8Downloader


def test_downloader_import() -> None:
    """Test if the M3U8Downloader can be imported."""
    assert M3U8Downloader is not None


def test_dummy_logic() -> None:
    """A placeholder test to ensure pytest is working."""
    assert sum([1]) == 1
