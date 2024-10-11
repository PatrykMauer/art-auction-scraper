"""
Module for scraping auction object specifications ('id', 'highest_bid', 'expert', 'close_at')
and uploading highlight_image_url to Google Drive.
"""
# Catching too general exception
# pylint: disable=W0718

# Argument order with *args
# pylint: disable=W1113

import json
import pandas as pd

import scrapy

from auctionsscraper.utils import (
    handle_error, get_total_dimensions, save_data_to_json,
    upload_to_google_sheets, initialize_google_sheets, merge_data,
    load_json_data, prepare_data_for_sheet,
    merge_details_with_description, extract_id_from_url,
    extract_specifications, append_specifications_to_details,
    load_description, send_data_to_flask_app)


class SpecsSpider(scrapy.Spider):
    """
    A Scrapy Spider for scraping specifications of auction objects from Catawiki.
    """
    name = "specs"
    allowed_domains = ["www.catawiki.com"]
    custom_settings = {
        'ITEM_CLASS': 'auctionsscraper.items.SpecItem'
    }

    def __init__(
            self, columns=None, sheet_url=None, sheet_name=None,
            auction_type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columns = json.loads(columns) if columns else []
        self.sheet_url = sheet_url
        self.sheet_name = sheet_name
        self.auction_type = auction_type

    def start_requests(self):
        data = load_json_data('objects.json')

        for d in data:
            try:
                url = f'https://www.catawiki.com/en/l/{d["id"]}'
                yield scrapy.Request(url=url, callback=self.parse, meta={'type': d.get('type')})
            except Exception as e:
                handle_error(f"Error creating request in start_requests: {e}")

    def parse(self, response, **kwargs):
        try:
            auction_type = response.meta['type']

            if auction_type == self.auction_type:
                print("TUTAJ")
                object_details = [
                    {'name': 'id', 'value': extract_id_from_url(response)}]

                specifications = extract_specifications(response)
                object_details.extend(
                    append_specifications_to_details(
                        specifications))

                description = load_description(response)
                object_dict = merge_details_with_description(
                    object_details, description)

                if auction_type == "graphics":
                    get_total_dimensions(object_dict)

                yield {'object': object_dict}
        except Exception as e:
            handle_error(f"Unexpected error in parse: {e}")

    def closed(self, reason):
        """
        Merge object and specification data.
        Append data to google sheets.
        """
        if reason != 'finished':
            return

        specs_data = load_json_data('specs.json')
        objects_data = load_json_data('objects.json')

        if not specs_data or not objects_data:
            return

        try:
            merged_data = merge_data(objects_data, specs_data)

            client = initialize_google_sheets()
            data_for_sheet = prepare_data_for_sheet(merged_data, self.columns)

            df = pd.DataFrame(data_for_sheet, columns=self.columns)

            flask_url = 'http://localhost:5000/webhook'
            filename = 'results_2024_05_11.xlsx'  # Replace with your desired filename

            # Send the DataFrame and filename to the Flask app
            send_data_to_flask_app(flask_url, df, filename)

            upload_to_google_sheets(
                client, df, self.sheet_url, self.sheet_name)

            save_data_to_json(merged_data, 'merged.json')
        except Exception as e:
            handle_error(f"Unexpected error in closed: {e}")
