# -*- coding: utf-8 -*-
import re
import arabic_reshaper
from bidi.algorithm import get_display
from scrapy import Spider
from websites.items import ArticleItem


class ThmniaSpider(Spider):
    name = 'thmnia'
    # allowed_domains = ['https://thmnia.com']
    start_urls = ['https://thmnia.com/126974/مباحث-حلوان-تضبط-متهما-عذب-زوجة-أخيه-وق/']

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext.strip().rstrip().lstrip().replace("\n", " ")

    def parse(self, response):
        item = ArticleItem()
        item["title"] = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='post-title']").extract_first())))
        item["author"] = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='post-author-name']/b/text()").extract_first())))
        item["link"] = response.urljoin('')
        item["description"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='entry-content clearfix single-post-content']/p/text()").extract()]
        item["comments"] = list()
        item["names"] = list()
        item["feedbacks"] = list()
        yield item