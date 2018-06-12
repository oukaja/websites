# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import arabic_reshaper
from bidi.algorithm import get_display
from scrapy import Spider, Request
from websites.items import ArticleItem


class TunisiaSpider(Spider):
    name = 'tunisia'
    allowed_domains = ['tunisia-sat.com']
    start_urls = ['https://www.tunisia-sat.com/forums/forums/91/']

    urlb = "https://www.tunisia-sat.com/forums/forums/91/page-"
    for i in range(2, 242):
        start_urls.append(urlb + str(i))

    @staticmethod
    def cleanhtml(raw_html, tag=False):
        if tag is False:
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', raw_html)
        else:
            cleanr = re.compile('<span class="LikeText">')
            cleanc = re.compile('</span>')
            clean = re.sub(cleanr, '', raw_html)
            cleantext = re.sub(cleanc, '', clean)
        return cleantext.replace("\n", "")

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        hrefs = response.xpath("//h3[@class='title']/a/@href").extract()
        for href in hrefs:
            yield Request(url=response.urljoin(href), callback=self.parse_links)

    def parse_links(self, response):
        item = ArticleItem()
        title = ""
        try:
            title = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//h1[@itemprop='headline']/text()").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["title"] = title
        ############################################################
        author = ""
        try:
            author = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("//a[@class='username']/text()").extract_first()).strip()))
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author
        # ############################################################
        item["link"] = response.url
        # ##############################################################
        description = list()
        try:
            description.extend([self.cleanhtml(d) for d in get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(response.xpath("null").extract())))])
        except (RuntimeError, TypeError, NameError):
            pass
        item["description"] = description
        # ##############################################################
        comment = list()
        names = list()
        feed = list()
        try:
            comment.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d).strip())) for d in response.xpath("//article/blockquote").extract()])
            names.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//a[@class='username author']/text()").extract()])
            for d in response.xpath("//span[@class='LikeText']").extract():
                c = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d, True))).count("</a>")
                if c == 4:
                    feed.append(3 + int(re.findall(r'\d+', self.cleanhtml(get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d, True))).split("</a>")[3]))[0]))
                else:
                    feed.append(c)
        except (RuntimeError, TypeError, NameError):
            pass

        links = response.xpath("//div[@class='PageNav']/nav/a[position()>1]/@href").extract()
        if len(links) == 0:
            item["comments"] = comment
            item["names"] = names
            item["feedbacks"] = feed
            yield item
        else:
            for href in links:
                request = Request(response.urljoin(href), callback=self.parse_comment)
                request.meta['item'] = item
                request.meta['comment'] = comment
                request.meta['names'] = names
                request.meta['feedbacks'] = feed
                yield request

    def parse_comment(self, response):
        item = response.meta['item']
        comment = response.meta['comment']
        feed = response.meta['feedbacks']
        names = response.meta['names']
        try:
            comment.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d).strip())) for d in response.xpath("//article/blockquote").extract()])
            names.extend([get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d))) for d in response.xpath("//a[@class='username author']/text()").extract()])
            for d in response.xpath("//span[@class='LikeText']").extract():
                c = get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d, True))).count("</a>")
                if c == 4:
                    feed.append(3 + int(re.findall(r'\d+', self.cleanhtml(get_display(arabic_reshaper.reshape(u'' + self.cleanhtml(d, True))).split("</a>")[3]))[0]))
                else:
                    feed.append(c)
        except (RuntimeError, TypeError, NameError):
            pass
        item["comments"] = comment
        item["names"] = names
        item["feedbacks"] = feed
        yield item

