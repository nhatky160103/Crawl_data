import argparse
from utilities import *
from setup import *


def main():
    parser = argparse.ArgumentParser(description="SGX Derivatives files downloader")

    parser.add_argument('--check', type=str, help='Input the date that you want check to download')
    parser.add_argument('--automation', action='store_true', help='Run the automation process')
    parser.add_argument('--config', type=str, default="resource/config.cfg",
                        help='Load config from FILE_NAME, default file is config.cfg')
    parser.add_argument('--history', type=str,
                        help='Download historical data. DATE could be one or several dates split by comma')
    parser.add_argument('--init_dict', action='store_true',
                        help='Create the dictionary mapping each date to the correct url index, must input start index')
    parser.add_argument('--update', action='store_true', help='Download latest available files')

    parser.add_argument('--support', action='store_true', help='Print support information')

    args = parser.parse_args()

    config = load_config(args.config)
    setup_logging(config)

    try:
        if args.check:
            date = args.check
            if not is_valid_date(date):
                print('Invalid date, Please double check the date entered !')
            else:
                check = check_files(date, config)
                if check:
                    print(f"All data for {date} have already been downloaded.")
                else:
                    print(f"Some data for {date} is missing. Please run: --history {date} to download the this files.")

        if args.automation:
            start_automation(config)

        if args.history:
            dates = args.history.split(',')
            for date in dates:
                if is_valid_date(date):
                    download_history(date, config)
                else:
                    print('Date format error, please check date format')

        if args.init_dict:
            try:
                create_dict(config)
            except Exception as e:
                logging.error('Fail to create the date_index_dict ' + str(e))
                print('Please check input or get support')

        if args.update:
            download_newest_file(config)

        if args.support:
            support()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()

