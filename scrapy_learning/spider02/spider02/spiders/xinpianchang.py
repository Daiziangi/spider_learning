import scrapy
from scrapy.http import HtmlResponse

from spider02.items import XinpianchangItem

class XinpianchangSpider(scrapy.Spider):
    name = "xinpianchang"
    allowed_domains = ["www.xinpianchang.com"]
    start_urls = ["https://www.xinpianchang.com/"]

    def parse(self, response:HtmlResponse, **kwargs):
        sel = scrapy.Selector(response)
        list_items = sel.xpath('//h2[(@class="truncate block")]')
        for item in list_items:
            movie_item = XinpianchangItem()
            movie_item["title"] = item.extract()
            yield movie_item

