# -*- coding: utf-8 -*-
import re
import arabic_reshaper
from bidi.algorithm import get_display
from scrapy import Spider
from websites.items import ArticleItem


class Kol7srySpider(Spider):
    name = 'kol7sry'
    # allowed_domains = ['https://kol7sry.net/?p=104102']
    start_urls = ['https://kol7sry.net/?p=104102']

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext.strip().rstrip().lstrip().replace("\n", " ")

    def parse(self, response):
        item = ArticleItem()
        item["title"] = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//h1[@class='name post-title entry-title']").extract_first())))
        item["author"] = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='post-meta-author']").extract_first())))
        item["link"] = response.urljoin('')
        item["description"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='td-post-text-content']/p/text()").extract()]
        item["comments"] = list()
        item["names"] = list()
        item["feedbacks"] = list()
        yield item
