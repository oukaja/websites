# -*- coding: utf-8 -*-
import scrapy


class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    link = scrapy.Field()
    description = scrapy.Field()
    comments = scrapy.Field()
    names = scrapy.Field()
    feedbacks = scrapy.Field()
