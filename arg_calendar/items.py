# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArgCalendarItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    term = scrapy.Field()
    link = scrapy.Field()
    cases = scrapy.Field()

class CaseItem(scrapy.Item):
	name = scrapy.Field()
	date = scrapy.Field()
	docket = scrapy.Field()
	consolidated_with = scrapy.Field()
	link = scrapy.Field()

