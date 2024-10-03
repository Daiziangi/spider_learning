# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import openpyxl
from scrapy.crawler import Crawler

import pymysql

class Spider02Pipeline:
    #这里写的方法都是钩子方法(函数)--->回调函数(方法),自己不会主动去调用它们,
    # 而是当爬虫爬到数据,将数据放入管道中的时候,这些方法会自动被框架所调用

#这里这个管道目的是让爬取到的数据保存到Excel中.

#这里四个是scrapy中最常用的钩子函数,且这四个方法的名字命名必须如此,不能写错.
    #这个函数是在创建管道(?)时会自动调用  ????
    def __init__(self):
        self.wb = openpyxl.Workbook() #创建一个Excel文件(工作簿->workbook)
        self.ws = self.wb.active #表示在当前工作簿中创建一个sheet表(worksheet)
        self.ws.title = 'Top250' #这里是当前sheet表的名称
        self.ws.append(('标题','评分','主题','时长','简介')) #这里是在设置当前表的表头有哪些列/项
        
    #在爬虫开始运行时会执行一次
    def open_spider(self,spider):
        pass

    #在爬虫结束运行时会执行一次
    def close_spider(self,spider):
        self.wb.save('电影数据.xlsx') #这里是这个Excel文件的文件名

    #在爬虫每次拿到一条数据时都会执行一次
    def process_item(self, item, spider):
        title = item.get('title','')
        rank = item.get('rank') or '' #这里的写法和上下两个的意思是一致的
        subject = item.get('subject','')
        duration = item.get('duration')
        intro = item.get('intro')
        self.ws.append((title,rank,subject,duration,intro)) 
        #这里是将所爬取到的每一条的标题,评分和主题信息以一行的形式插入到这个sheet表中
        return item

class DB_Pipeline:
    def __init__(self):
        self.conn = pymysql.connect(
            host ='localhost',
            port =3306,
            user ='root',
            password ='181814',
            database ='spider',
            charset ='utf8mb4'
            )
        self.cursor = self.conn.cursor()
        self.data = [] #写一个空列表用来装数据,使得数据可以一次性插入数据库
    def close_spider(self,spider):
        #如果关闭连接前,data列表中仍有数据,就写入数据库
        if len(self.data) > 0:
            self._write_to_db()
        # self.cursor.close() #这里是关闭游标,但是下面关闭连接时会自动关闭游标
        self.conn.close()


    def process_item(self,item,spider):
        title = item.get('title','')
        rank = item.get('rank') or 0
        subject = item.get('subject','')
        self.data.append((title,rank,subject))
        #如果数据量大于10条,就写入数据库,并清空data列表,以便下次继续将新数据写入data列表中
        #也就是每爬取到10条数据就写入一次数据库
        if len(self.data) >= 10:
            self._write_to_db()
            self.data.clear()
        return item
    
    #以下划线开头是为了表示这个方法是私有的,不希望外部调用
    def _write_to_db(self):
        #sql语句中的三个表头分别是title,rating,subject,因此这里的tb_to_movie的括号中的三个参数分别是这三个表头的值
        self.cursor.execute('insert into tb_to_movie(title,rating,subject) values(%s,%s,%s)',self.data)
        self.conn.commit()
        self.conn.close()
        
#将数据保存至数据库的高级版pipeline
class ToDBPipline:

    @classmethod #因为这里是类方法,因此下面这个from_crawler必须是这个名字
    def from_crawler(cls,crawler:Crawler):
        host = crawler.settings['DB_HOST']
        port = crawler.settings['DB_PORT']
        username = crawler.settings['DB_USER']
        password = crawler.settings['DB_PASS']
        database = crawler.settings['DB_NAME']
        return cls(host,port,username,password,database)
    #这边是用cls加上圆括号,调用这个类的构造器语法,构造这个类的类对象
    
    def __init__(self,host,port,username,password,database) :
        self.conn = pymysql.connect(
            host=host,port=port,
            user=username,password=password,
            database=database,charset='utf8mb4',
            autocommit=True
        )
        self.cursor = self.conn.cursor()

    def open_spider(self,spider):
        pass

    def close_spider(self,spider):
        self.conn.close()

    def process_item(self,item,spider):
        title = item.get('title','')
        price = item.get('price',0.0)
        deal_count = item.get('deal_count','')
        shop = item.get('shop','')
        location = item.get('location','')
        self.cursor.execute(
            "insert into 'tb_taobao_goods'"
            "('g_titile','g_price','g_deal_count','g_shop','g_locaiton')"
            'values (%s,%s,%s,%s,%s)'
            (title,price,deal_count,shop,location)
        )
        '''
        也就是获取item中对应爬取到的数据,若获取不到则给出默认值,
        然后执行SQL语句将对应的数据保存到数据库中.
        '''
        return item
    
#将数据保存至数据库的高级版pipeline---豆瓣电影版
class DouBanToDBPipline:

    @classmethod #因为这里是类方法,因此下面这个from_crawler必须是这个名字
    def from_crawler(cls,crawler:Crawler):
        host = crawler.settings['DB_HOST']
        port = crawler.settings['DB_PORT']
        username = crawler.settings['DB_USER']
        password = crawler.settings['DB_PASS']
        database = crawler.settings['DB_NAME']
        return cls(host,port,username,password,database)
    #这边是用cls加上圆括号,调用这个类的构造器语法,构造这个类的类对象
    
    def __init__(self,host,port,username,password,database) :
        self.conn = pymysql.connect(
            host=host,port=port,
            user=username,password=password,
            database=database,charset='utf8mb4',
            autocommit=True
        )
        self.cursor = self.conn.cursor()

    def open_spider(self,spider):
        pass

    def close_spider(self,spider):
        self.conn.close()

    # def process_item(self,item,spider):
    #     title = item.get('title','')
    #     rank = item.get('rank',0.0)
    #     subject = item.get('subject','')
    #     duration = item.get('duration','')
    #     intro = item.get('intro','')
    #     self.cursor.execute(
    #         "insert into 'douban_movie'"
    #         "('movie_titile','movie_rank','movie_subject','movie_duration','movie_intro')"
    #         'values (%s,%s,%s,%s,%s)'
    #         (title,rank,subject,duration,intro)
    #     )
    #     '''
    #     也就是获取item中对应爬取到的数据,若获取不到则给出默认值,
    #     然后执行SQL语句将对应的数据保存到数据库中.
    #     '''
    #     return item
    
    def process_item(self, item, spider):
        title = item.get('title', '')
        rank = item.get('rank', 0.0)
        subject = item.get('subject', '')
        duration = item.get('duration', '')
        intro = item.get('intro', '')
        self.cursor.execute(
            "INSERT INTO douban_movie (movie_title, movie_rank, movie_subject, movie_duration, movie_intro) "
            "VALUES (%s, %s, %s, %s, %s)",
            (title, rank, subject, duration, intro)
        )
        return item