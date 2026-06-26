from . import config_manager, downloader

# Re-export classes for backward compatibility
ConfigManager = config_manager.ConfigManager
DownloadOrchestrator = downloader.DownloadOrchestrator
DownloadRequest = downloader.DownloadRequest
DownloadResult = downloader.DownloadResult
M3U8Downloader = downloader.M3U8Downloader

__all__ = [
    "ConfigManager",
    "DownloadOrchestrator",
    "DownloadRequest",
    "DownloadResult",
    "M3U8Downloader",
]
