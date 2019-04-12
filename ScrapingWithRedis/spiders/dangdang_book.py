# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from scrapy_redis.spiders import RedisSpider
from urllib.parse import urljoin


class DangdangBookSpider(RedisSpider):
    name = 'dangdang_book'
    allowed_domains = ['dangdang.com']
    # start_urls = ['http://dangdang.com/']
    redis_key = "dangdang"

    def parse(self, response):
        div_list = response.xpath("//div[@class='con flq_body']/div")
        for each_div in div_list:
            item = {}
            item['first_cate'] = each_div.xpath("./dl/dt//text()").extract()
            item['first_cate'] = [i.strip() for i in item['first_cate'] if len(i.strip()) > 0]
            left_list = each_div.xpath(".//div[@class='col eject_left']/dl")
            for each_left in left_list:
                item['second_cate'] = each_left.xpath("./dt//text()").extract()
                item['second_cate'] = [i.strip() for i in item['second_cate'] if len(i.strip()) > 0]
                left_detail_list = each_left.xpath("./dd/a")
                for each_left_detail in left_detail_list:
                    item['third_cate'] = each_left_detail.xpath("./@title").extract_first()
                    item['book_list_url'] = each_left_detail.xpath("./@href").extract_first()
                    if item['book_list_url'] is not None:
                        yield scrapy.Request(
                            item['book_list_url'],
                            callback=self.parse_book_list,
                            meta={"item": deepcopy(item)}
                        )

    def parse_book_list(self, response):
        item = response.meta['item']
        book_list = response.xpath("//ul[@class='bigimg']/li")
        for each_book in book_list:
            item['book_name'] = each_book.xpath("./a/@title").extract_first()
            print(item)
        next_url = response.xpath("//a[@class='arrow_r arrow_r_on']/@href").extract_first()
        if next_url is not None:
            next_url = urljoin(response.url, next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={'item': item}
            )
