# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from scrapy import Spider
from websites.items import ArticleItem
from scrapy.http import Request
from bidi.algorithm import get_display
import arabic_reshaper
import re


class WorldbankSpider(Spider):
    name = 'worldbank'
    allowed_domains = ['blogs.worldbank.org']
    start_urls = ['http://blogs.worldbank.org/arabvoices/']
    urlb = "http://blogs.worldbank.org/arabvoices/frontpage?page="
    for i in range(1, 65):
        start_urls.append(urlb + str(i))

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        hrefs = response.xpath("//*[@class='node-title node-title']/a/@href").extract()
        for href in hrefs:
            yield Request(response.urljoin(href), callback=self.parse_links)

    def parse_links(self, response):
        item = ArticleItem()
        item["title"] = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id='page-title']/text()").extract_first())))
        ##############################################################
        author = ""
        try:
            author += "*" + get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='submittedby']").extract_first()))).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author
        ##############################################################
        item["link"] = response.urljoin('')
        ##############################################################
        descrip = list()
        try:
            descrip.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='field-items']").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["description"] = descrip
        ##############################################################
        i = len([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(c))) for c in response.xpath("//*[@id='comments']//*[@class='field-item even']").extract()])
        item["comments"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(c))) for c in response.xpath("//*[@id='comments']//*[@class='field-item even']").extract()]
        ##############################################################
        item["names"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(n))) for n in response.xpath("//*[@class='comment-submitted']").extract()]
        ##############################################################
        item["feedbacks"] = ['0' for i in range(i)]
        yield item
