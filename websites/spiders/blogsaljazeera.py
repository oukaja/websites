# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import arabic_reshaper
from bidi.algorithm import get_display
from scrapy import Spider
from websites.items import ArticleItem
from operator import add
from scrapy_splash import SplashRequest


class BlogsaljazeeraSpider(Spider):
    name = 'blogsaljazeera'
    allowed_domains = ['blogs.aljazeera.net']
    start_urls = ['http://blogs.aljazeera.net/']

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def parse(self, response):
        hrefs = response.xpath("//*[@class='first_main_article']/article/a/@href").extract()
        for href in hrefs:
            yield SplashRequest(url=response.urljoin(href), callback=self.parse_links, endpoint='render.html')

    def parse_links(self, response):
        item = ArticleItem()

        title = ""
        try:
            title = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='detail-blog-body']/h1/text()").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["title"] = title

        author = ""
        try:
            author = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id='detail-longblog-page']/div/div/ul/li[1]/strong/a/text()").extract()[1]).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author

        item["link"] = response.url

        description = list()
        try:
            description.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='body-content']/div[3]").extract()])
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
                             [int(self.cleanhtml(d)) for d in response.xpath("//*[@class='comments-like clsLike']/text()").extract()],
                             [int(self.cleanhtml(d)) for d in response.xpath("//*[@class='comments-unlike clsLike']/text()").extract()]))
        except (RuntimeError, TypeError, NameError):
            pass
        item["comments"] = comment
        item["names"] = names
        item["feedbacks"] = feeds

        yield item
