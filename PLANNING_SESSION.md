# Planning Session: m3u8 Downloader

**Date:** 6/26/2026

## Goals
Initial goal is to create a simple m3u8 downloader.

## Decisions and Requirements

### 1. Configuration Generator (`gen_config.py`)
- **Interface**: Interactive Python script that prompts the user for a filename and an m3u8 URL.
- **Storage Format**: YAML (`downloads.yaml`) for human readability.
- **Behavior**: The script will **append** new entries to the existing `downloads.yaml` file.
- **Validation**: The generator will validate that the provided link is a valid URL before saving.

### 2. Downloader (`downloader.py`)
- **Core Engine**: Use `ffmpeg` for downloading to ensure the highest quality and robustness.
- **Workflow**:
    - Reads entries from `downloads.yaml`.
    - **Retry Logic**: Implement a retry mechanism on failure (crucial requirement).
    - **Cleanup**: Automatic deletion of the entry from `downloads.yaml` upon successful download is deferred for a later stage.
- **Output Organization**:
    - All downloads will be placed in a `downloads/` directory.
    - Downloads will be organized into date-based subfolders: `downloads/YYYY-MM-DD/<filename>`.
- **Observability**:
    - Use `tqdm` for real-time progress bars.
    - Implement detailed logging for better maintenance and debugging.

### 3. Infrastructure & Tooling
- **Dependency Management**: Support for `uv` or `pip` (using `requirements.txt` or `pyproject.toml`).
- **Libraries**: `PyYAML`, `tqdm`, `validators`, etc.

## Summary of Interview
- **User**: Wants a simple downloader that starts with a Python script and a YAML file.
- **User**: Prefers YAML for readability.
- **User**: Wants interactive input for the generator.
- **User**: Wants `ffmpeg` for quality.
- **User**: Wants date-based folder structure under `downloads/`.
- **User**: Emphasized the importance of retry logic for error handling.
- **User**: Decided against cleanup (deleting from YAML) for this initial phase.
