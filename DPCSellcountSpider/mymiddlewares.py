# -*- coding: UTF-8 -*-
# Created by dev on 16-5-20.

import random
import redis
import json
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.utils.project import get_project_settings
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError


class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    # the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape
    # for more user agent strings,you can find it in http://www.useragentstring.com/pages/useragentstring.php
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 UBrowser/5.6.13381.207 Safari/537.36"
    ]

    def process_request(self, request, spider):
        try:
            ua = random.choice(self.user_agent_list)
            if ua:
                request.headers.setdefault('User-Agent', ua)
        except:
            pass


class ProxyMiddleware(object):
    settings = get_project_settings()
    REDIS_HOST = settings.get('REDIS_HOST')
    REDIS_PORT = settings.get('REDIS_PORT')
    proxykey = settings.get('PROXY_KEY')
    redisclient = redis.Redis(REDIS_HOST, REDIS_PORT)
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError)

    def process_request(self, request, spider):
        """
        将request设置为使用代理
        """
        try:
            self.redisclient = redis.Redis(self.REDIS_HOST, self.REDIS_PORT)
            proxy = self.redisclient.srandmember(self.proxykey)
            proxyjson = json.loads(proxy)
            ip = proxyjson["ip"]
            # print ip
            request.meta['proxy'] = "http://%s" % ip
        except Exception, ee:
            # print '------------------------------', ee
            pass

    def process_exception(self, request, exception, spider):
        """
        处理由于使用代理导致的连接异常 则重新换个代理继续请求
        """
        # print '错误类型', exception.message
        # if isinstance(exception, self.DONT_RETRY_ERRORS):
        print '代理报错   ------------------', exception
        try:
            new_request = request.copy()
            if len(request.meta['sellcountUrl']) > 15:
                self.redisclient = redis.Redis(self.REDIS_HOST, self.REDIS_PORT)
                proxy = self.redisclient.srandmember(self.proxykey)
                proxyjson = json.loads(proxy)
                ip = proxyjson["ip"]
                new_request.meta['proxy'] = "http://%s" % ip
                return new_request
            else:
                print request.meta['sellcountUrl'], '异常URL'
        except:
            pass
