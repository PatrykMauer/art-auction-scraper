"""
Module for scraping auction object data ('id', 'highest_bid', 'expert', 'close_at')
and uploading highlight_image_url to Google Drive.
"""
# pylint: disable=W0718
from datetime import date
import scrapy
from auctionsscraper.utils import handle_error, get_object_id, load_json_data


class ObjectsSpider(scrapy.Spider):
    """ Scrapy spider that collects auction data from catawiki website. """
    name = "objects"
    allowed_domains = ["www.catawiki.com"]

    def start_requests(self):
        data = load_json_data('auctions.json')
        if not data:
            return

        today = str(date.today())
        for item in data:
            try:
                # Ensure all necessary keys are present
                if item.get('close_at') == today:
                    url = f"https://www.catawiki.com/en/a/{item['id']}"
                    meta = {
                        'expert': item['expert'],
                        'close_at': item['close_at'].replace('-', '/'),
                        'type': item['type']
                    }
                    yield scrapy.Request(url=url, callback=self.parse, meta=meta)
            except KeyError as e:
                handle_error(f"Missing key in item: {e}")
            except AttributeError as e:
                handle_error(
                    f"Data format error with 'close_at' in item: {e}")
            except Exception as e:
                # General exception handling for unexpected errors
                handle_error(f"Unexpected error in start_requests: {e}")

    def parse(self, response, **kwargs):
        try:
            container = response.css('div.LotList_list__t1AL2.gallery')
            object_links = container.css('a::attr(href)').getall()
            object_ids = [get_object_id(link) for link in object_links]
            print(object_links)
            if not object_links:
                handle_error("Object_links are empty")

            if object_ids:
                base_url = 'https://www.catawiki.com/buyer/api/v3/bidding/lots?ids='
                ids_string = '%2C'.join(object_ids)
                url = base_url + ids_string
                yield scrapy.Request(
                    url=url,
                    callback=self.get_object_details,
                    meta=response.meta
                )
        except Exception as e:
            handle_error(str(e))

    def get_object_details(self, response):
        """Scrape auction object data"""
        try:
            scraped_objects = response.json()
            for scraped_object in scraped_objects['lots']:
                url = f"https://www.catawiki.com/buyer/api/v3/lots/{scraped_object['id']}/gallery"
                yield scrapy.Request(
                    url=url,
                    callback=self.extract_image_url,
                    meta={
                        'id': scraped_object['id'],
                        'highest_bid': scraped_object['current_bid_amount']['EUR'],
                        'expert': response.meta['expert'],
                        'close_at': response.meta['close_at'],
                        'type': response.meta['type']
                    }
                )
        except Exception as e:
            handle_error(str(e))

    def extract_image_url(self, response):
        """Scrape first image of a listing and append its url to reponse.meta"""
        try:
            images = response.json()
            highlight_image_url = images['gallery'][0]['images'][0]['l']['url']
            yield {
                'id': response.meta['id'],
                'highest_bid': response.meta['highest_bid'],
                'highlight_image_url': highlight_image_url,
                'expert': response.meta['expert'],
                'close_at': response.meta['close_at'],
                'type': response.meta['type']
            }
        except Exception as e:
            handle_error(str(e))
