# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re
import arabic_reshaper
from bidi.algorithm import get_display
from scrapy import Spider, Request
from websites.items import ArticleItem
from operator import add
from scrapy_splash import SplashRequest


class BaljazeeraSpider(Spider):
    name = 'baljazeera'
    # allowed_domains = ['http://blogs.aljazeera.net/amalalharithi']
    start_urls = ['http://blogs.aljazeera.net/amalalharithi']

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def parse(self, response):
        hrefs = response.xpath("//*[@class='single_article_block']/h2/a/@href").extract()
        for href in hrefs:
            yield Request(url=response.urljoin(href), callback=self.parse_links)

    def parse_links(self, response):
        print(response.urljoin(''))
        item = ArticleItem()

        title = ""
        try:
            title = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='detail-blog-body']/h1/text()").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["title"] = title

        author = ""
        try:
            author = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='blogger-info-detail']/ul/li/strong/a").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author

        item["link"] = response.url

        description = list()
        try:
            description.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='body-content']/div/p/text()").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            description.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//p[@dir='rtl']").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            description.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='body-content']/div/div/div/text()").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            description.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='detail-blog-body']/div/div/div/p/text()").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            description.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='body-content']/div/div/div/div").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["description"] = description

        item["comments"] = list()
        item["names"] = list()
        item["feedbacks"] = list()

        yield item
