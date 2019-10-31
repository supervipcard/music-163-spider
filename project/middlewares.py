# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from scrapy.utils.python import global_object_name
from scrapy.exceptions import IgnoreRequest
from scrapy import signals
import random
import logging
import json
import time
import base64

logger = logging.getLogger(__name__)


class CodeError(IgnoreRequest):
    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(CodeError, self).__init__(*args, **kwargs)


class ABYProxyMiddleware(object):
    def __init__(self, proxyUser, proxyPass):
        self.proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")

    @classmethod
    def from_crawler(cls, crawler):
        proxyUser = crawler.settings.get('PROXY_USER')
        proxyPass = crawler.settings.get('PROXY_PASS')
        return cls(proxyUser, proxyPass)

    def process_request(self, request, spider):
        request.meta['proxy'] = "http://http-dyn.abuyun.com:9020"
        request.headers.setdefault('Proxy-Authorization', self.proxyAuth)


class ADSLProxyMiddleware(object):
    def __init__(self, key):
        self.key = key

    @classmethod
    def from_crawler(cls, crawler):
        key = crawler.settings.get('REDIS_PROXY_KEY')
        return cls(key)

    def process_request(self, request, spider):
        count = 0
        while True:
            keys = spider.server.keys('%s*' % self.key)    # redis连接
            if keys:
                proxy_channel = random.choice(keys).decode('utf-8')
                proxy = spider.server.get(proxy_channel)
                if proxy:
                    request.meta['proxy_channel'] = proxy_channel
                    request.meta['proxy'] = 'https://' + proxy.decode('utf-8')
                    break
            count += 1
            logger.warning("Waiting %(request)s (%(count)d times): Proxy Absence", {'request': request, 'count': count})
            time.sleep(3)


class MyRetryMiddleware(RetryMiddleware):
    def __init__(self, settings):
        super(MyRetryMiddleware, self).__init__(settings)
        self.ip_blacklist_key = settings.get('IP_BLACKLIST_KEY')

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status != 200:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        elif request.callback.__name__ in ['api_album', 'api_song_url', 'api_song_lyric', 'song_parse'] and json.loads(response.text).get('code') != 200:
            proxy_channel = request.meta.get('proxy_channel')
            if proxy_channel:
                spider.server.sadd(self.ip_blacklist_key, request.meta.get('proxy').replace('https://', ''))
                spider.server.delete(proxy_channel)
            reason = 'code {}'.format(json.loads(response.text).get('code'))
            return self._retry(request, reason, spider) or response
        return response

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        retry_times = self.max_retry_times

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            logger.warning("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            stats.inc_value('retry/max_reached')
            logger.warning("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})


class CodeErrorMiddleware(object):
    def process_spider_input(self, response, spider):
        if response.request.callback.__name__ in ['api_album', 'api_song_url', 'api_song_lyric', 'song_parse'] and json.loads(response.text).get('code') != 200:
            raise CodeError(response, 'Ignoring non-200 response')


class ProjectSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProjectDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
