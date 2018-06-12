# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import arabic_reshaper
from scrapy import Spider, Request
from bidi.algorithm import get_display
from websites.items import ArticleItem
from operator import add
from scrapy_splash import SplashRequest


class Blogsaljazeera2Spider(Spider):
    name = 'blogsaljazeera2'
    allowed_domains = ['blogs.aljazeera.net']
    start_urls = ['http://blogs.aljazeera.net/topics/short']


    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    @staticmethod
    def lua_script(n):
        LUA_SCRIPT = """
                function main(splash)
                local url = splash.args.url
                assert(splash:go(url))
                assert(splash:wait(1))
                for i=1,{},1 do
                assert(splash:runjs('document.getElementsByTagName("button")[0].click()'))
                assert(splash:wait(1))
                end
                return {}
                end
                """.format(n, "{html=splash:html()}")
        return LUA_SCRIPT

    def parse(self, response):
        for url in self.start_urls:
            yield Request(response.urljoin(url), self.parse_result, meta={
                'splash': {
                    'args': {'lua_source': self.lua_script(2)},
                    'endpoint': 'execute',
                }
            })

    def parse_result(self, response):
        for link in response.xpath("//*[@id='topics_Artilce_container']/div/a/@href").extract():
            yield Request(response.urljoin(link), self.parse_links, dont_filter=False)

    def parse_links(self, response):
        rep = int(int(response.xpath("//input[@id='intTotal']/@value").extract_first())/6)+1
        yield SplashRequest(url=response.urljoin(''), callback=self.parse_comment, endpoint='execute', args={'lua_source': self.lua_script(rep)})

    def parse_comment(self, response):
        item = ArticleItem()

        title = ""
        try:
            title = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//h1[@class='tweet_strip_text']/text()").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["title"] = title

        author = ""
        try:
            author = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("null").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author

        item["link"] = response.url

        description = list()
        try:
            description.extend([self.cleanhtml(d) for d in get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("null").extract())))])
        except (RuntimeError, TypeError, NameError):
            pass
        item["description"] = description

        comment = list()
        names = list()
        feeds = list()
        try:
            comment.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//article/p/text()").extract()])
            names.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//article/div/div/h2/text()").extract()])
            feeds.extend([self.cleanhtml(d) for d in response.xpath("//*[@class='number_likes']/text()").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["comments"] = comment
        item["names"] = names
        item["feedbacks"] = feeds

        return item
