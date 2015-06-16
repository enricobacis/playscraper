# -*- coding: utf-8 -*-

import scrapy

class PlayItem(scrapy.Item):
    pkg = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    stars = scrapy.Field()
    published = scrapy.Field()
    size = scrapy.Field()
    downloads = scrapy.Field()
    version = scrapy.Field()
    os = scrapy.Field()

