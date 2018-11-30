# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImagecrawlerItem(scrapy.Item):
    # define the fields for your item here like:
	source_url = scrapy.Field()
	alternate_text = scrapy.Field()
	img_height = scrapy.Field()
	img_width = scrapy.Field()
	img_url = scrapy.Field()
	img_name = scrapy.Field()
	img_type = scrapy.Field()
	img_aspect_ratio = scrapy.Field()
