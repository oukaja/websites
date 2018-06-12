# -*- coding: utf-8 -*-
import scrapy
from bidi.algorithm import get_display
import arabic_reshaper
import re
from websites.items import ArticleItem
from scrapy_splash import SplashRequest
from operator import add
from scrapy.http import Request

class AlanbaSpider(scrapy.Spider):
    name = 'alanba'
    allowed_domains = ['alanba.com.kw']
    start_urls = ['http://alanba.com.kw/']

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def parse(self, response):
        for url in response.xpath("//*[@class='page-title CenterTextAlign']/a/@href").extract():
            yield Request(url=response.urljoin(url), callback=self.parse_link)

    def parse_link(self, response):
        item = ArticleItem()

        title = ""
        try:
            title = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(''.join(response.xpath("//*[@class='page-title-art']/text()").extract())).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["title"] = title

        author = ""
        try:
            author = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='post_source']/text()").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author

        item["link"] = response.url

        description = list()
        try:
            description.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@itemprop='articleBody']/div").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["description"] = description

        comment = list()
        names = list()
        feeds = list()
        try:
            comment.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='comment_content']/p/text()").extract()])
            names.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='comment']//*[@class='userName']/text()").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["comments"] = comment
        item["names"] = names
        item["feedbacks"] = feeds

        yield item