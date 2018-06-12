# -*- coding: utf-8 -*-
from scrapy import Spider
from websites.items import ArticleItem
from scrapy.http import Request
from bidi.algorithm import get_display
import arabic_reshaper
import re


class BbcSpider(Spider):
    name = 'bbc'
    allowed_domains = ['bbc.com']
    start_urls = ['http://www.bbc.com/arabic/topics/e45cb5f8-3c87-4ebd-ac1c-058e9be22862',
                  'http://www.bbc.com/arabic/middleeast']

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        hrefs = response.xpath("//*[@class='title-link']/@href").extract()
        for href in hrefs:
            yield Request(response.urljoin(href), callback=self.parse_links)

    def parse_links(self, response):
        item = ArticleItem()
        title = ""
        try:
            title += get_display(arabic_reshaper.reshape(u'' + response.xpath("//*[@class='story-body']/h1/text()").extract_first()))
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            title += get_display(arabic_reshaper.reshape(u'' + response.xpath("//*[@id='media-asset-page-text']/h1/text()").extract_first()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["title"] = title.strip()
        item["author"] = ""
        item["link"] = response.urljoin('')
        descrip = list()
        try:
            descrip.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d).strip())) for d in response.xpath("//*[@class='story-body__inner']").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["description"] = descrip
        item["comments"] = []
        item["names"] = []
        item["feedbacks"] = []
        yield item