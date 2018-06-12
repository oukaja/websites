# -*- coding: utf-8 -*-
import scrapy
from bidi.algorithm import get_display
import arabic_reshaper
import re
from websites.items import ArticleItem
from scrapy.http import Request


class ArabicpostSpider(scrapy.Spider):
    name = 'arabicpost'
    allowed_domains = ['arabicpost.net']
    start_urls = ['http://arabicpost.net/eve',
                  'https://arabicpost.net/newmedia/']


    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        hrefs = list()
        hrefs.extend(list(response.xpath("//*[@class='archive__home__wrap']/div/a/@href").extract()))
        hrefs.extend(list(response.xpath("//article/a/@href").extract()))
        print(len(hrefs))
        for href in hrefs:
            yield Request(response.urljoin(href), callback=self.parse_links, dont_filter=True)

    def parse_links(self, response):
        item = ArticleItem()
        title = ""
        try:
            title += get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='single__content__wrap']/section/div/h1/text()").extract_first())))
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            title += get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//body/div/section/section/div/h1/text()").extract_first())))
        except (RuntimeError, TypeError, NameError):
            pass
        item["title"] = title.strip()
        ################################################
        author = ""
        try:
            author += get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='post-source']/text()").extract_first())))
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            author += get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//*[@class='post-source']/strong/text()").extract_first())))
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author.strip()
        ##############################################################
        item["link"] = response.urljoin('')
        ##############################################################
        descrip = list()
        try:
            descrip.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//div[@class='single__content__wrap']//*[@class='content__rules js__single-content js_post-content']//*[@style='direction: rtl;']").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            descrip.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='content__rules js__single-content js_post-content']//*[@style='direction: rtl;']").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            descrip.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//div[@class='single__content__wrap blog__page article__page__styles']//*[@style='text-align: right;']").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            descrip.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@class='single__content js_post-container']//p/text()").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["description"] = descrip
        ################################################
        link = response.xpath("//*[@class='fb_rtl']/@src").extract_first()
        ##############################################################
        request = Request(response.urljoin(link), callback=self.parse_comment, dont_filter=True)
        request.meta['item'] = item
        yield request

    def parse_comment(self, response):
        item = response.meta['item']
        try:
            item["comments"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//*[@id='facebook']/body/div/div/div/div/div/div/div/div/div/div/div/div/div/span/span/span/text()").extract()]
            item["names"] = [get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//a[@class=' UFICommentActorName']/text()").extract()]
            item["feedbacks"] = []
        except (RuntimeError, TypeError, NameError):
            pass
        yield item


