"""Module for scraping ids and closing time of specified auction categories from Catawiki.com"""
import scrapy
# Line too long
# pylint: disable=C0301


class AuctionsSpider(scrapy.Spider):
    """Scrapy spider that scrapes specified auction categories from Catawiki.com"""
    name = "auctions"
    allowed_domains = ["catawiki.com"]

    graphics_ids = ['1563']
    books_ids = ['1239', '141']

    start_urls = [
        f'https://www.catawiki.com/buyer/api/v1/categories/{cat_id}/auctions?locale=en&page=1&status=open&per_page=100'
        for cat_id in graphics_ids + books_ids]

    def parse(self, response, **kwargs):
        auction_list = response.json()

        # Determine the type based on category ID in the request URL
        if any(cat_id in response.url for cat_id in self.graphics_ids):
            auction_type = "graphics"
        elif any(cat_id in response.url for cat_id in self.books_ids):
            auction_type = "books"
        else:
            auction_type = "unknown"

        auctions = [
            {
                'id': auction['id'],
                'close_at': auction['close_at'][:-10],
                'expert': auction['auctioneers'][0]['name'],
                'type': auction_type
            }
            for auction in auction_list['auctions']
        ]

        yield from auctions
