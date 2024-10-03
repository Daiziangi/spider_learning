from typing import Iterable
import scrapy
from scrapy import Request
from scrapy.http import HtmlResponse

from spider02.items import MovieItem

class DouobanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['movie.douban.com']
    # start_urls = ['http://movie.douban.com/top250']
    def start_requests(self):
        for i in range(10): #这里range()多少也是看你自己要爬多少页,这里是爬取10页
            url = f'https://www.douban.com/doulist/3936288/?start={i*25}&sort=time&playable=0&sub_type='
            #这里让 i * 25 是因为每一页的url中的start参数的值是每一页的电影条目的起始索引,每一页的电影条目数是25.
            yield Request(url=url)
            # yield Request(url=url,meta={'proxy':'http://...'})
            #  #如果需要使用代理,可以在这里设置,也可以在中间键的Spider02DownloaderMiddleware类的process_request方法中设置,
            # 也是写个meta参数,里面是代理的地址.
            #除了加代理,还可以在这里或者中间键中加headers,cookies等信息
        '''
        如果是要在url里加上搜索关键字进行搜索的话:
        keywords = ['关键字1','关键字2','关键字3']
        for keyword in keywords:
            for page in range(5): #这里range()多少也是看你自己要爬多少页
                url = f'https://xxxx.com/search?q={keyword}&s={page*48}'  #这里page*48的原因是页码从0开始,每一页间隔的数值为48
                yield Request(url=url)
        '''

    #response:HtmlResponse 表示 response 参数应该是 HtmlResponse 类型的对象。冒号 : 后面跟着的是类型注解。
    '''def parse(self, response:HtmlResponse, **kwargs) -> Iterable[MovieItem]：里面
    -> Iterable[MovieItem] 中的 Iterable[MovieItem] 是一个类型注解，它指定了函数返回值的预期类型。
    Iterable 是一个泛型类型，表示可以迭代的对象，比如列表、元组、字典等。MovieItem 应该是一个类，表示一个电影条目的数据结构。
    所以，Iterable[MovieItem] 表示函数返回一个可以迭代的对象，其中的每个元素都是 MovieItem 类型。'''
    def parse(self, response:HtmlResponse, **kwargs):
            # 检查响应编码是否为UTF-8，如果不是则进行转换
        # if response.encoding != 'utf-8':    
        # # 使用replace方法创建一个新的HtmlResponse对象，并指定编码为utf-8
        #     response = HtmlResponse(url=response.url, body=response.body, encoding='utf-8', request=response.request)
        sel = scrapy.Selector(response)
        list_items = sel.css('.doulist-item')
        for item in list_items:
            detail_url = item.css('.title a::attr(href)').extract_first()
            movie_item = MovieItem()
            # movie_item['title'] = item.css('.title a::text').extract_first()
            movie_item['rank'] = item.css('.rating_nums::text').extract_first()
            subject_all = item.css('.doulist-subject > div.abstract::text').getall()
            if len(subject_all) > 2:
                subject_str = subject_all[2].strip()
                movie_item['subject'] = subject_str
            yield Request(
                #这里yield的Request方法是为了将电影的详情页的url传递给parse_detail方法,使得parse_detail方法可以获取到电影的详情页的url
                #让parse_detail方法去解析电影详情页
                url = detail_url,callback=self.parse_detail,
                cb_kwargs={'item':movie_item} 
                #这里的'item'是键,movie_item是值,这里的键是为了在parse_detail方法中接收这个值,这个值就是movie_item实例对象
            )   #这里的cb_kwargs是为了传递movie_item实例对象给parse_detail方法 

    '''
    当需要解析/获取更深层次页面的数据并打包封装在一起时,就需要让较为浅层次的页面将已经获取到的数据先进行部分打包封装
    (打包封装到对应item的实例化对象的属性中(这里的item可以在items.py文件中自定义这个类)),
    并且将更加深层次的url作为Request的参数进行yield. 同时其中Request中的callback函数要是用于解析/处理更加深层的页面的函数.
    在这个解析/处理更加深层的页面的函数中,需要继续解析页面,获取数据,并将获取到的数据和上一层传过来打包好的数据封装在一起
    (封装到同一个item对象的属性中),
    再yield这个最终封装好的数据(内容)对象.
    '''
    def parse_detail(self,response,**kwargs):
        #      # 检查响应编码是否为UTF-8，如果不是则进行转换
        # if response.encoding != 'utf-8':    
        # # 使用replace方法创建一个新的HtmlResponse对象，并指定编码为utf-8
        #     response = HtmlResponse(url=response.url, body=response.body, encoding='utf-8', request=response.request)
        #这里的**kwargs是为了接收parse方法中的cb_kwargs参数传递过来的movie_item实例对象
        movie_item = kwargs['item']  
        #这里的item是parse方法中的cb_kwargs参数的键,也就意为从cb_kwargs参数中获取键为item的值,也就是movie_item实例对象
        sel = scrapy.Selector(response)
        movie_item['title'] = sel.css('h1 span::text').extract_first()
        movie_item['duration'] = sel.css('span[property="v:runtime"]::attr(content)').extract_first()
        movie_item['intro'] = sel.css("span[property='v:summary']::text").extract_first()
        yield movie_item

    '''
    # 后面跟着的是元素的 ID 名称，用于选择具有特定 ID 属性的元素。ID 在一个页面中应该是唯一的。    #uniqueId 会选择 ID 为 uniqueId 的元素。
    . 后面跟着的是元素的类名，用于选择所有具有特定类名的元素。        .className 会选择所有具有 class="className" 属性的元素。
    [] 用于选择具有特定属性的元素。你可以进一步指定属性的值来缩小选择范围。           [type="text"] 会选择所有 type 属性为 text 的元素。

    在 Scrapy 框架中，::text 是一个特殊的选择器，用于选择元素的文本内容。
    所以，如果你在 Scrapy 框架中看到 span.inq::text，这意味着你想要选择所有类名为 inq 的 span 元素的文本内容。
    这是一个特定于 Scrapy 的用法，而不是标准的 CSS 语法。

    在 CSS 中，用于选择文本内容的正确伪元素是 ::selection，它用于选择用户选中的文本部分。
    但是，它不能与 span 或任何其他标签一起使用来选择文本内容。
    '''