# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GreenptScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    item_category = scrapy.Field()
    item_name = scrapy.Field()
    item_point = scrapy.Field()
    company = scrapy.Field()
    item_tag = scrapy.Field()
