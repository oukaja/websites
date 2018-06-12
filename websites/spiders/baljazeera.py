# -*- coding: utf-8 -*-
import scrapy


class BaljazeeraSpider(scrapy.Spider):
    name = 'baljazeera'
    # allowed_domains = ['http://blogs.aljazeera.net/amalalharithi']
    start_urls = ['http://blogs.aljazeera.net/amalalharithi']

    def parse(self, response):
        pass
