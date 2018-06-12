# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import arabic_reshaper
from bidi.algorithm import get_display
from scrapy import Spider, Request
from websites.items import ArticleItem


class KapitalisSpider(Spider):
    name = 'kapitalis'
    allowed_domains = ['kapitalis.com']
    start_urls = ['http://kapitalis.com/tunisie/category/a-la-une/',
                  'http://kapitalis.com/tunisie/category/societe/']

    # urlb = "http://kapitalis.com/tunisie/category/a-la-une/page/"
    urlm = "http://kapitalis.com/tunisie/category/societe/page/"
    # for i in range(2, 565):
    #     start_urls.append(urlb + str(i) + "/")
    for i in range(2, 1420):
        start_urls.append(urlm + str(i) + "/")

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        hrefs = response.xpath("//div[@class='sidebar_content']//*[@class='title']/@href").extract()
        for href in hrefs:
            yield Request(url=response.urljoin(href), callback=self.parse_links)

    def parse_links(self, response):
        item = ArticleItem()
        title = ""
        try:
            title = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//h1[@itemprop='name']/text()").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["title"] = title
        ############################################################
        author = ""
        try:
            author = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//div[@class='sidebar_content']//p/strong/text()").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author
        #############################################################
        item["link"] = response.url
        #############################################################
        description = list()
        try:
            description.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//div[@class='sidebar_content']//div[@itemtype='http://schema.org/Review']/p[position()>2]").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["description"] = description
        # ##############################################################
        comment = list()
        names = list()
        try:
            comment.extend([self.cleanhtml(d).strip() for d in response.xpath("//*[@class='commentlist']//*[@class='comment-content comment']").extract()])
            names.extend([self.cleanhtml(d) for d in response.xpath("//*[@class='commentlist']//cite/text()").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["comments"] = comment
        item["names"] = names
        item["feedbacks"] = []
        yield item
