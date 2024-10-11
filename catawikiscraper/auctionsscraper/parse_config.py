"""
Module that parses config.json file.
It is used by run_crawler.sh to create proper command that scrapes for specific aution."
"""
# pylint: disable = W0621
# Redefining name 'config_file' from outer scope
# pylint: disable=W0718
# Handle too general Exception

import json
import sys


def load_config(config_file, category):
    """
    Load configuration data from a JSON file.

    Args:
        config_file (str): Path to the JSON configuration file.
        category (str): Category key to retrieve data from the configuration file.

    Returns:
        dict: Configuration data for the specified category.

    Raises:
        ValueError: If no data is found for the specified category.
    """
    with open(config_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        category_data = data.get(category)
        if not category_data:
            raise ValueError(f"No data found for category: {category}")
        return category_data


def create_scrapy_command(config):
    """
    Create a Scrapy command string based on the provided configuration.

    Args:
        config (dict): Configuration data including 'columns', 'sheet_url', and 'sheet_name'.

    Returns:
        str: Scrapy command string.

    """
    columns = json.dumps(config["columns"])
    sheet_url = config["sheet_url"]
    sheet_name = config["sheet_name"]
    auction_type = config["auction_type"]
    return f"scrapy crawl specs -a columns='{columns}' -a sheet_url='{sheet_url}' -a sheet_name='{sheet_name}' -a auction_type='{auction_type}' -O specs.json"


if __name__ == "__main__":
    config_file = sys.argv[1]
    category = sys.argv[2]
    try:
        config = load_config(config_file, category)
        command = create_scrapy_command(config)
        print(command)
    except Exception as e:
        print(str(e))
