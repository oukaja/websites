# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from scrapy import Spider
from websites.items import ArticleItem
from scrapy.http import Request
from bidi.algorithm import get_display
import arabic_reshaper
import re


class HibapressSpider(Spider):
    name = 'hibapress'
    allowed_domains = ['hibapress.com']
    start_urls = []
    urlb = "https://ar.hibapress.com/section-2.html/page/"
    for i in range(1, 63):
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
        hrefs = response.xpath(
            "//article/div/a[position()<25]/@href").extract()
        for href in hrefs:
            yield Request(response.urljoin(href), callback=self.parse_links)

    def parse_links(self, response):
        item = ArticleItem()
        item["title"] = get_display(arabic_reshaper.reshape(
            u'' + self.cleanhtml(response.xpath("//div[@class='bdaia-post-title']/h1/span/text()").extract_first())))
        ##############################################################
        author = ""
        try:
            author += "*" + get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id='hibapressarticles']/p[2]/span/b/span/text()").extract_first()))).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            author += "*" + get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id='hibapressarticles']/p[2]/span/text()").extract_first()))).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            author += get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id='hibapressarticles']/p[1]/text()").extract_first()))).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            author += get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id='hibapressarticles']/p[2]/span/strong/text()").extract_first()))).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            author += "*" + get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id='hibapressarticles']/div/span/strong/text()").extract_first()))).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            author += "*" + get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id=':ld']/div[1]/span/text()").extract_first()))).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            author += "*" + get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id='hibapressarticles']/p/span/strong/text()").extract_first()))).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            author += "*" + get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id='hibapressarticles']/p[2]/span/strong/text()").extract_first()))).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            author += "*" + get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id='hibapressarticles']/div/div/div/div/div/span/text()").extract_first()))).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author
        ##############################################################
        item["link"] = response.urljoin('')
        ############################################################## 
        descrip = list()
        try:
            descrip.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in
                            response.xpath("//*[@id='hibapressarticles']/p[position()>1]").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            descrip.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in
                            response.xpath("//*[@id='hibapressarticles']/div/text()").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["description"] = descrip
        ##############################################################
        item["comments"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(c))) for c in
                            response.xpath("//*[@class='comment-body']/p[2]/text()").extract()]
        ##############################################################
        item["names"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(n))) for n in
                         response.xpath("//*[@class='comment-header']/h3/text()").extract()]
        ##############################################################
        item["feedbacks"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(f))) for f in
                             response.xpath("null").extract()]
        yield item
