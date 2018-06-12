# -*- coding: utf-8 -*-
import scrapy
from bidi.algorithm import get_display
import arabic_reshaper
import re
from websites.items import ArticleItem
from scrapy.http import Request
from scrapy_splash import SplashRequest


class AlarabiyaSpider(scrapy.Spider):
    name = 'alarabiya'
    allowed_domains = ['alarabiya.net']
    start_urls = ['http://alarabiya.net/']

    LUA_SCRIPT = """
                function main(splash)
                  assert(splash:go(splash.args.url))
                  assert(splash:wait(1.5))
                  return {
                    html = splash:html()
                  }
                end
                """

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def start_requests(self):
        yield Request(url='http://alarabiya.net/', callback=self.parse, meta={
            'splash': {
                'endpoint': 'render.html',
                'args': {
                    'lua_source': self.LUA_SCRIPT,
                    'timeout': 90
                }
            }
        })

    def parse(self, response):
        print(response.body)
        # urls = response.xpath("//*[@class='news_list']/li/a/@href").extract()
        # for url in urls:
        #     yield Request(url=response.urljoin(url), callback=self.parse_link)

    # def parse_link(self, response):
    #     print(response.urljoin(''))
