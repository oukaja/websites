# -*- coding: utf-8 -*-
import scrapy
from bidi.algorithm import get_display
import arabic_reshaper
import re
from websites.items import ArticleItem
from scrapy_splash import SplashRequest
from operator import add
from scrapy.http import Request


class QatarlivingSpider(scrapy.Spider):
    name = 'qatarliving'
    allowed_domains = ['qatarliving.com']
    start_urls = ['http://qatarliving.com/']

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def parse(self, response):
        for href in response.xpath("//*[@class='cpcl b-news-n-posts']/div/div/div/a/@href").extract():
            yield Request(url=response.urljoin(href), callback=self.parse_link)

    def parse_link(self, response):
        item = ArticleItem()

        title = ""
        try:
            title = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='b-post-header--el-title']/text()").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["title"] = title

        author = ""
        try:
            author = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='username']/text()").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author

        item["link"] = response.url

        description = list()
        try:
            description.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='b-post-detail--el-text']").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["description"] = description

        comment = list()
        names = list()
        feeds = list()
        try:
            comment.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='b-comments-list--el-text']/div").extract()])
            names.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='b-comments-list--el-info']/a/text()").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["comments"] = comment
        item["names"] = names
        item["feedbacks"] = feeds

        yield item
