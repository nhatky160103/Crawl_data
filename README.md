# SGX Derivatives Files Downloader

## Introduction

The `SGX Derivatives Files Downloader` is a tool designed to automatically download derivative contract data files from the SGX website. The program supports both automatic and manual modes for downloading data.

## Features

- **Check Files**: Verify if all necessary files for a specific date have been downloaded.
- **Automation**: Run the program in automation mode to download daily files and re-download any missing files.
- **Download History**: Download historical data for specific dates.
- **Create Dictionary**: Create a dictionary mapping dates to URL indices for historical file downloads.
- **Update Latest**: Download the latest available files.

## Requirements

- Python 3.x
- Libraries: `requests`, `tqdm`, `schedule`, `keyboard`, `configparser`, `logging`

## Installation

1. Install the required libraries using pip:
    ```bash
    pip install requests tqdm schedule keyboard
    ```

2. Create a configuration file (`config.cfg`) to specify settings such as download directories and schedule times.

## Usage

To use the program, run it with one of the following options:

- **Initialize Dictionary**: Create a dictionary of dates and URL indices for historical file downloads.
    ```bash
    python main.py --init_dict
    ```

- **Check Files**: Verify if files for a specific date are downloaded. Replace `YYYYMMDD` with the desired date.
    ```bash
    python main.py --check=YYYYMMDD
    ```

- **Automation**: Run the program in automation mode to handle daily downloads and re-download missing files.
    ```bash
    python main.py --automation
    ```

- **Download History**: Download historical data for specific dates. Replace `YYYYMMDD` with the desired date or a comma-separated list of dates.
    ```bash
    python main.py --history=YYYYMMDD,YYYYMMDD
    ```

- **Update Latest**: Download the latest available files.
    ```bash
    python main.py --update
    ```

- **Support**: Print support and contact information.
    ```bash
    python main.py --support
    ```

- **Help**: Display help information.
    ```bash
    python main.py -h or python main.py --help
    ```

## Configuration

The program reads configuration settings from a file (`config.cfg`). Example settings include:

- `downloader`: Configuration for download directories and chunk sizes.
- `network`: Network timeout settings.
- `history`: File paths for tracking downloaded indices and missing files.
- `automation`: Scheduling times for automatic downloads and re-downloads.
- `logging`: Logging configuration.



## Contact
For support or questions, please contact Dinh Nhat Ky at dinhnhatky16012003@gmail.com.