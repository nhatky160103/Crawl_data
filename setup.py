import configparser
import logging
import sys


def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def setup_logging(config):
    logging.basicConfig(filename=config.get('logging', 'file'),
                        level=getattr(logging, config.get('logging', 'level')),
                        format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S')

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


def support():
    usage_text = """
Usage: python main.py [OPTION]...

 SGX Derivatives files downloader create by Dinh Nhat Ky (Hust) that supports both automatic and manual modes.

Options:
    --check=DATE           Check files for a specific date.
                           DATE should be in the format YYYYMMDD.

    --automation           Run the program in automation mode, 
                           include download the daily files and re-download the missing files .

    --config=FILE_NAME     Load configuration from the specified FILE_NAME.
                           The default configuration file is config.cfg.

    --history=DATE         Download historical data.
                           DATE can be a single date or a comma-separated list of dates.
                           Example: 20240829 (August 29, 2024) or 20240902 (September 2, 2024).

    --init_dict            Create a dictionary of dates and URL indices for historical file downloads.

    --update               Download the latest available files.

    --support              Print support and contact information.

    -h, --help             Display this help information.

Examples:
    python main.py --init_dict
    python main.py --check=20240829
    python main.py --automation
    python main.py --history=20240829,20240902
    python main.py --update
    python main.py -h or python main.py --help
    python main.py --support


Please note: To download historical files, you must first initialize the dictionary using the --init_dict option.
If you wish to use a different configuration file, run the following command: 
python main.py --config [path to config file] [option]
Example: python main.py --config=custom.cfg --check 20240902

    """

    print(usage_text)
