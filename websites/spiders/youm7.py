# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from scrapy import Spider
from websites.items import ArticleItem
from scrapy.http import Request
from bidi.algorithm import get_display
import arabic_reshaper
import re


class Youm7Spider(Spider):
    name = 'youm7'
    allowed_domains = ['youm7.com']
    start_urls = ['https://www.youm7.com/المرأة']

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def parse(self, response):
        hrefs = response.xpath("//h3/a/@href").extract()
        for href in hrefs:
            yield Request(response.urljoin(href), callback=self.parse_links)

    def parse_links(self, response):
        item = ArticleItem()
        title = ""
        title = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='articleHeader']/h1/text()").extract_first())))
        item["title"] = title.replace('\n', '').replace('\r', '').strip()
        ##############################################################
        author = ""
        try:
            author += "*" + get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='writeBy']/text()").extract_first()))).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author
        # ##############################################################
        item["link"] = response.urljoin('')
        # ##############################################################
        descrip = list()
        try:
            descrip.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d.replace('\t', '').replace('\n', '').replace('\r', '').strip()))) for d in response.xpath("//*[@class='articleCont']/p/text()").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["description"] = descrip
        # ##############################################################
        item["comments"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(c))) for c in response.xpath("//*[@class='article__comment-content-text selectionShareable']/text()").extract()]
        # ##############################################################
        item["names"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(n))) for n in response.xpath("//*[@class='article__comment-by-text selectionShareable']/text()").extract()]
        # ##############################################################
        item["feedbacks"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(f))) for f in response.xpath("null").extract()]
        yield item
