# -*- coding: utf-8 -*-

# Scrapy settings for project project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'project'

SPIDER_MODULES = ['project.spiders']
NEWSPIDER_MODULE = 'project.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False


DOWNLOAD_TIMEOUT = 10
RETRY_TIMES = 5

# LOG_FILE = 'log'
# LOG_LEVEL = 'INFO'


# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   'project.middlewares.CodeErrorMiddleware': 543,
}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'project.middlewares.ProxyMiddleware': 300,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'project.middlewares.MyRetryMiddleware': 550,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'project.extensions.RedisSpiderSmartIdleClosedExtensions': 0,
    'project.extensions.ErrorClosedExtensions': 0,
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'project.pipelines.SqlPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

DNSCACHE_ENABLED = True
DNSCACHE_SIZE = 1000
DNS_TIMEOUT = 60

IDLE_NUMBER = 360         # 允许的空闲时长，每5秒会增加一次IDLE_NUMBER，直到增加到360，程序close

ERROR_CHECK_INTERVAL = 60     # error次数检测间隔
CLOSESPIDER_INTERVAL_ERRORCOUNT = 30    # 在检测间隔内，error次数大于该值，程序close

# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
DUPEFILTER_CLASS = "project.my_dupefilter.MyRFPDupeFilter"
DUPEFILTER_DEBUG = True

SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'
DEPTH_PRIORITY = -1    # 深度优先

SCHEDULER_PERSIST = True    # 是否在关闭时保留原来的调度器和去重记录
SCHEDULER_FLUSH_ON_START = False    # 是否在开始之前清空调度器和去重记录

REDIS_HOST = '101.132.71.2'
REDIS_PORT = 6379
REDIS_PARAMS = {
    'password': '',
}
REDIS_PROXY_KEY = 'proxy'

MYSQL_HOST = '101.132.71.2'
MYSQL_PORT = 3306
MYSQL_USER = ''
MYSQL_PASSWD = ''
MYSQL_DB = 'test'

MAIL_FROM = '805071841@qq.com'
MAIL_HOST = 'smtp.qq.com'
MAIL_PORT = 465
MAIL_USER = '805071841@qq.com'
MAIL_PASS = ''
MAIL_TO = ['805071841@qq.com']
MAIL_TLS = True
MAIL_SSL = True

BLOOMFILTER_BIT = 30
BLOOMFILTER_HASH_NUMBER = 6
