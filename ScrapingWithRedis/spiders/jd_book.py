# -*- coding: utf-8 -*-
import scrapy
import copy
import json
from urllib import parse


class JdBookSpider(scrapy.Spider):
    name = 'jd_book'
    allowed_domains = ['jd.com', 'p.3.cn']
    start_urls = ['https://book.jd.com/booksort.html']

    def parse(self, response):
        dt_list = response.xpath("//div[@class='mc']//dt")
        for each_dt in dt_list:
            item = {}
            item['first_cate'] = each_dt.xpath("./a/text()").extract_first()
            dd_list = each_dt.xpath("./following-sibling::dd[1]/em/a")
            for each_dd in dd_list:
                item['second_cate'] = each_dd.xpath("./text()").extract_first()
                item['second_cate_url'] = "https:" + each_dd.xpath("./@href").extract_first()
                yield scrapy.Request(
                    item['second_cate_url'],
                    callback=self.parse_cate,
                    meta={'item': copy.deepcopy(item)}
                )

    def parse_cate(self, response):
        item = response.meta['item']
        book_list = response.xpath("//li[@class='gl-item']")
        for each_book in book_list:
            item['book_name'] = each_book.xpath(".//div[@class='p-name']//em/text()").extract_first().strip()
            item['book_detail_url'] = "https:" + each_book.xpath(".//div[@class='p-img']/a/@href").extract_first()
            item['img'] = each_book.xpath(".//img/@src").extract()
            item['author'] = each_book.xpath(".//span[@class='author_type_1']/a/@title").extract_first()
            item['press'] = each_book.xpath(".//span[@class='p-bi-store']/a/@title").extract()
            item['publish_date'] = each_book.xpath(".//span[@class='p-bi-date']/text()").extract_first().strip()
            item['data-sku'] = each_book.xpath("./div/@data-sku").extract_first()
            if item['data-sku'] is not None:
                yield scrapy.Request(
                    "https://p.3.cn/prices/mgets?skuIds=J_{}".format(item['data-sku']),
                    callback=self.parse_book_price,
                    meta={'item': copy.deepcopy(item)}
                )
        next_url = response.xpath("//a[@class='pn-next']/@href").extract_first()
        if next_url is not None:
            next_url = parse.urljoin(response.url, next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_cate,
                meta={'item': item}
            )

    def parse_book_price(self, response):
        item = response.meta['item']
        item['book_price'] = json.loads(response.body.decode())[0]["op"]
        yield item
