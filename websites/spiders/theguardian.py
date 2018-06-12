# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from websites.items import ArticleItem
from scrapy_splash import SplashRequest

SPLASH_SCRIPT = """
function main(splash)
    assert(splash:go(splash.args.url))
    assert(splash:wait(1))
    return {html=splash:html()}
end
"""


class TheguardianSpider(scrapy.Spider):
    name = 'theguardian'
    allowed_domains = ['theguardian.com']
    start_urls = ['https://www.theguardian.com/inequality',
                  'https://www.theguardian.com/lifeandstyle/women']

    urlb = "https://www.theguardian.com/global-development/series/womens-rights-and-gender-equality-in-focus+world/middleeast?page="
    urlm = "https://www.theguardian.com/world/middleeast?page="

    for i in range(1, 5):
        start_urls.append(urlb + str(i))
    for i in range(1, 200):
        start_urls.append(urlm + str(i))

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        hrefs = response.xpath("//div[@class='fc-item__container']/a/@href").extract()
        for href in hrefs:
            yield SplashRequest(url=href, callback=self.parse_links, endpoint='render.html')
            # yield Request(response.urljoin(href), callback=self.parse_links, meta={
            #     'splash': {
            #         'endpoint': 'render.html',
            #         'args': {
            #             'lua_source': SPLASH_SCRIPT,
            #             'timeout': 90
            #         }
            #     }
            # })

    def parse_links(self, response):
        item = ArticleItem()
        title = ""
        try:
            title = self.cleanhtml(response.xpath("//*[@class='u-cf']/h1").extract_first()).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        item["title"] = title
        ############################################################
        author = ""
        try:
            author = self.cleanhtml(response.xpath("//*[@rel='author']").extract_first()).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        try:
            author = self.cleanhtml(response.xpath("//*[@class='byline']").extract_first()).strip()
        except (RuntimeError, TypeError, NameError):
            pass
        item["author"] = author
        ############################################################
        item["link"] = response.urljoin('')
        ##############################################################
        try:
            item["description"] = [self.cleanhtml(d) for d in
                                   response.xpath("//*[@id='article']/div[2]/div/div[1]/div/p").extract()]
        except (RuntimeError, TypeError, NameError):
            pass
        ##############################################################
        comment = list()
        names = list()
        try:
            comment.extend([self.cleanhtml(d).strip() for d in response.xpath("//*[@class='d-comment__body']").extract()])
            names.extend([self.cleanhtml(d) for d in response.xpath("//*[@itemprop='givenName']/text()").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        links = response.xpath("//*[@class='pagination__list']/a/@href").extract()
        if len(links) == 0:
            item["comments"] = comment
            item["names"] = names
            item["feedbacks"] = []
            yield item
        else:
            for href in links:
                request = SplashRequest(response.urljoin(href), callback=self.parse_comment, endpoint='render.html')
                request.meta['item'] = item
                request.meta['comment'] = comment
                request.meta['names'] = names
                yield request

    def parse_comment(self, response):
        item = response.meta['item']
        comment = response.meta['comment']
        names = response.meta['names']
        try:
            comment.extend([self.cleanhtml(d) for d in response.xpath("//*[@class='d-comment__body']").extract()])
            names.extend([self.cleanhtml(d) for d in response.xpath("//*[@itemprop='givenName']/text()").extract()])
        except (RuntimeError, TypeError, NameError):
            pass
        item["comments"] = comment
        item["names"] = names
        item["feedbacks"] = []
        yield item
