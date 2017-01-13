# -*- coding: utf-8 -*-

# Scrapy settings for DPCSellcountSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'DPCSellcountSpider'

SPIDER_MODULES = ['DPCSellcountSpider.spiders']
NEWSPIDER_MODULE = 'DPCSellcountSpider.spiders'

SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True

CONCURRENT_REQUESTS = 8


# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html  ProxyMiddleware
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'DPCSellcountSpider.mymiddlewares.RotateUserAgentMiddleware': 401,
    'DPCSellcountSpider.mymiddlewares.ProxyMiddleware': 700,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
}

COOKIES_ENABLED = False

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 400
}

# REDIS_HOST = '192.168.1.17'
# REDIS_PORT = 6379

REDIS_HOST = '117.122.192.50'
REDIS_PORT = 6479
#
# REDIS_HOST = '192.168.100.200'
# REDIS_PORT = 6379

PROXY_KEY = 'proxy:iplist3'

LOG_LEVEL = 'ERROR'
LOG_FILE = 'spider.log'

# 超时时间
DOWNLOAD_TIMEOUT = 15
