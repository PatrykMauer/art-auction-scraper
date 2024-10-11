# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags


class AuctionsscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def remove_newline(value):
    return value.replace('\n', '').strip()


class SpecItem(scrapy.Item):
    name = scrapy.Field(input_processor=MapCompose(
        remove_tags, remove_newline), output_processor=TakeFirst())
    value = scrapy.Field(input_processor=MapCompose(
        remove_tags, remove_newline), output_processor=TakeFirst())
    pass


class DescriptionItem(scrapy.Item):
    Description = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=Join(' \n')
    )
    pass
