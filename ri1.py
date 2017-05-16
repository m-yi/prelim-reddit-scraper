# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from reddit.items import RiItem
import re
from scrapy import Spider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor


class Ri1Spider(scrapy.Spider):
    name = "ri1"
    allowed_domains = ["www.reddit.com"]
    start_urls = ['http://www.reddit.com/']

    rules = [Rule(LinkExtractor(allow = ['/top/\?count=\d*&after=\w*']))]


    def parse(self, response):
        page_urls = [response.url + "?count=" + str(page_num*25) + "&after=t3_67" + r'....'
                    for page_num in range(1,9)]
        for page_url in page_urls:
            yield scrapy.Request(page_url, callback = self.parse_comments)
        # print(response.url)


    def parse_comments(self, response):

        for href in response.xpath('//a[@class="bylink comments may-blank"]/@href').extract():
            url = response.urljoin(href)
            yield scrapy.Request(url, callback=self.parse_comments_contents)


    def parse_comments_contents(self, response):
        item = RiItem()

        loader = ItemLoader(item=RiItem(), response = response)
        comments_bodies = response.xpath('//div[contains(@data-type, "comment")]')

        for comment in comments_bodies:
            comment_text = comment.xpath('.//div[contains(@class, "usertext-body may-blank-within md-container ")]/div').extract()
            comment_author = comment.xpath('./@data-author').extract()
            comment_id = comment.xpath('./@id').extract()
            comment_child_ids = comment.xpath('./div[contains(@class, "child")]/div[contains(@class, "sitetable listing")]/div[contains(@data-type, "comment")]/@id').extract()

            loader.replace_value('comment_text', comment_text)
            loader.replace_value('comment_author', comment_author)
            loader.replace_value('comment_id', comment_id)
            loader.replace_value('comment_child_ids', comment_child_ids)

            yield loader.load_item()

        more_comments = response.xpath('//span[contains(@class, "morecomments")]/a/@href').extract()
        for moreC in more_comments:
            yield scrapy.Request(self.allowed_domains + moreC, callback = self.parse)
