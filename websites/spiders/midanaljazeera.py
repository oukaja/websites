# -*- coding: utf-8 -*-
import scrapy
from bidi.algorithm import get_display
import arabic_reshaper
import re
from websites.items import ArticleItem
from scrapy_splash import SplashRequest
from operator import add


class MidanaljazeeraSpider(scrapy.Spider):
    name = 'midanaljazeera'
    allowed_domains = ['midan.aljazeera.net']
    start_urls = ['http://midan.aljazeera.net/intellect/sociology/']

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def parse(self, response):
        for url in response.xpath("//*[@class='link_all']/@href").extract():
            yield SplashRequest(url=response.urljoin(url), callback=self.parse_link, endpoint='render.html')

    def parse_link(self, response):
        item = ArticleItem()

        title = ""
        try:
            title = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='background_title']/h1/text()").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["title"] = title

        author = ""
        try:
            author = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//h4[@class='gold']/text()").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author

        item["link"] = response.url

        description = list()
        try:
            description.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='fontstyleDivBody detailedBody']/div/div/div").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["description"] = description

        comment = list()
        names = list()
        feeds = list()
        try:
            comment.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='comment-text']/text()").extract()])
            names.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='commenter']/text()").extract()])
            feeds.extend(map(add,
                             [int(self.cleanhtml(d)) for d in response.xpath("//*[@class='comments-like clsLike clicked']/text()").extract()],
                             [int(self.cleanhtml(d)) for d in response.xpath("//*[@class='comments-unlike clsLike clicked']/text()").extract()]))
        except (RuntimeError, TypeError, NameError):
            pass
        item["comments"] = comment
        item["names"] = names
        item["feedbacks"] = feeds

        yield item
