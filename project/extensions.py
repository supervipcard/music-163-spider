# -*- coding: utf-8 -*-

# Define here the models for your scraped Extensions

from twisted.internet import task
from scrapy import signals
from scrapy.exceptions import NotConfigured


class RedisSpiderSmartIdleClosedExtensions(object):
    def __init__(self, idle_number, crawler, mail_to):
        self.crawler = crawler
        self.idle_number = idle_number
        self.mail_to = mail_to
        self.idle_list = []
        self.idle_count = 0

    @classmethod
    def from_crawler(cls, crawler):
        # first check if the extension should be enabled and raise

        # NotConfigured otherwise

        if 'redis_key' not in crawler.spidercls.__dict__.keys():
            raise NotConfigured('Only supports RedisSpider')

        idle_number = crawler.settings.getint('IDLE_NUMBER', 360)
        mail_to = crawler.settings.get('MAIL_TO', ['805071841@qq.com'])
        ext = cls(idle_number, crawler, mail_to)

        crawler.signals.connect(ext.spider_idle, signal=signals.spider_idle)
        crawler.signals.connect(ext.spider_error, signal=signals.spider_error)

        return ext

    def spider_idle(self, spider):
        # 当spider进入空闲状态时会调用这个方法一次，之后每隔5秒再调用一次
        # 当持续半个小时都没有spider.redis_key，就关闭爬虫
        # 判断是否存在 redis_key
        if not spider.server.exists(spider.redis_key):
            self.idle_count += 1
        else:
            self.idle_count = 0

        if self.idle_count > self.idle_number:
            self.crawler.engine.close_spider(spider, 'Waiting time exceeded')

    def spider_error(self, failure, response, spider):
        spider.error_count += 1
        spider.mailer.send(to=self.mail_to, subject='Spider Error：' + str(response), body=str(failure))


class ErrorClosedExtensions(object):
    def __init__(self, crawler, interval, closespider_error_count):
        self.crawler = crawler
        self.interval = interval
        self.closespider_error_count = closespider_error_count
        self.task = None
        self.last_error_count = 0

    @classmethod
    def from_crawler(cls, crawler):
        interval = crawler.settings.getint('ERROR_CHECK_INTERVAL', 60)
        closespider_error_count = crawler.settings.getint('CLOSESPIDER_INTERVAL_ERRORCOUNT', 30)
        o = cls(crawler, interval, closespider_error_count)

        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)

        return o

    def spider_opened(self, spider):
        self.task = task.LoopingCall(self.check_error_count, spider)
        self.task.start(self.interval)

    def check_error_count(self, spider):
        if spider.error_count - self.last_error_count > self.closespider_error_count:
            self.crawler.engine.close_spider(spider, 'Error too many')
        else:
            self.last_error_count = spider.error_count

    def spider_closed(self, spider, reason):
        if self.task and self.task.running:
            self.task.stop()
