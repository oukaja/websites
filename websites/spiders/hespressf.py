# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import arabic_reshaper
from bidi.algorithm import get_display
from scrapy import Spider
from websites.items import ArticleItem


class HespressfSpider(Spider):
    name = 'hespressf'
    allowed_domains = ['hespress.com']
    start_urls = ['https://www.hespress.com/femme/383932.html']

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext.strip().rstrip().lstrip().replace("\n", " ")

    def parse(self, response):
        item = ArticleItem()
        item["title"] = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id='article_holder']/h1/text()").extract_first())))
        item["author"] = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@id='article_body']/div[1]/span/text()").extract_first())))
        item["link"] = response.urljoin('')
        item["description"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@id='article_body']/p/text()").extract()]
        item["comments"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(c))) for c in response.xpath("//div[@id='comment_list']/div/div/div/div/div[@class='comment_text']").extract()]
        item["names"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(n))) for n in response.xpath("//div[@id = 'comment_list']/div/div/div/div/div[@class='comment_header']").extract()]
        item["feedbacks"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(f))) for f in response.xpath("//div[@class='result']/text()").extract()]
        yield item
