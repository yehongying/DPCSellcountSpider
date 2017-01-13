# -*- coding: UTF-8 -*-
# Created by dev on 16-5-20.

import re
import sys
import json
import time
import datetime
import logging
import HTMLParser
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from DPCSellcountSpider.items import SellCountItem

reload(sys)
sys.setdefaultencoding('utf-8')


class SellcountSpider(RedisSpider):
    reReplace = re.compile('<.*?>|&.*?;')
    h = HTMLParser.HTMLParser()
    # cookie = '''t=f1d06870685879a126f29aef70568571; thw=cn; _tb_token_=20ShhUwc6Ijc; cookie2=295471f2e024935e8feeb67f9cc11581'''
    cookie = 't=f1d06870685879a126f29aef70568571; cookie2=6f00a95927be6e9e5aea864ba5a014d2;'

    name = "DailySellCountSpider"  # DailySellCountSpider sellCountSpider
    redis_key = '%s:start_urls' % name
    start_urls = {
        # '{"Urls": "https://detail.tmall.com/item.htm?id=525125609473","Urlleibie": "冰柜","Urlweb": "TM","spbjpinpai": "云麦","spbjjixing": "M1501","pc": "2016-07-21"}'
    }

    def make_requests_from_url(self, url):
        try:
            taskInfo = json.loads(url)
            spurl = str(taskInfo['Urls']).replace('http:', 'https:')
            print spurl
            if 'detail.tmall.com' in spurl:
                headers = {
                    "Accept": "*/*",
                    "Referer": "https://www.tmall.com/",
                    "Cookie": self.cookie
                }
                return Request(spurl, callback=self.parseTM, headers=headers, meta={'taskInfo': taskInfo},
                               dont_filter=True)
            elif 'taobao.com' in spurl:
                return Request(spurl, callback=self.parseTB, meta={'taskInfo': taskInfo}, dont_filter=True)
            else:
                self.log("错误URL:" + str(url), level=logging.ERROR)
        except Exception, ex:
            print 'make_requests_from_url error:', ex
            self.log("make_requests_from_url error:" + str(ex), level=logging.ERROR)

    # 天猫商城
    def parseTM(self, response):
        print '1' * 50
        taskInfo = response.meta['taskInfo']
        spurl = taskInfo['Urls']
        urlweb = taskInfo['Urlweb']
        pc = taskInfo.get('pc', '')
        spname = ''
        spleibie = taskInfo['Urlleibie']
        sppinpai = taskInfo['spbjpinpai']
        spxinghao = taskInfo['spbjjixing']
        webprice = ''
        spcuxiao = ''
        shopname = ''
        xiaoshoutype = ''
        item = SellCountItem()
        try:
            html = str(response.body).decode('gbk').encode('utf8')
            if '亲，访问受限了' in html or '小二在紧急处理，稍后再来哦' in html or '<div id="J_Static" class="static">' in html:
                print 'IP被封1-------------------------'
                headers = {
                    "Accept": "*/*",
                    "Referer": "https://www.tmall.com/",
                    # "Cookie": self.cookie
                }
                yield Request(spurl, callback=self.parseTM, headers=headers, meta={'taskInfo': taskInfo},
                              dont_filter=True)
            else:
                spnameReg = re.search('<input type="hidden" name="title" value="(?P<dd>[^<]*?)"', html)
                if spnameReg:
                    spname = spnameReg.group('dd')
                else:
                    spnameReg = re.search('title":"(?P<dd>.*?)"', html)
                    if spnameReg:
                        spname = spnameReg.group('dd')
                    else:
                        spnameReg = re.search('<h\d+ data-spm="\d+">(?P<dd>[\s\S]*?)</h', html)
                        if spnameReg:
                            spname = spnameReg.group('dd')

                spname = spname.replace('\r', '').replace('\n', '').replace('\t', '')
                if spname != '':
                    spname = re.sub(self.reReplace, '', spname)
                    if 'tm-yushou-process-banner' in html:
                        xiaoshoutype = '预售'

                    webPriceReg = re.search('defaultItemPrice":"(?P<dd>.*?)"', html)
                    if webPriceReg:
                        webprice = webPriceReg.group('dd')
                        if '-' in webprice:
                            webprice = webprice[0:webprice.find('-')].rstrip()

                    sppinpaiReg = re.search('brand":"(?P<dd>.*?)"', html)
                    if sppinpaiReg:
                        sppinpai = sppinpaiReg.group('dd')
                    spxinghaoReg = re.search('型号[^"]{0,5}:&nbsp;(?P<dd>.*?)</li>', html)
                    if spxinghaoReg:
                        spxinghao = spxinghaoReg.group('dd')
                    else:
                        spxinghaoReg = re.search('货号[^"]{0,5}:&nbsp;(?P<dd>.*?)</li>', html)
                        if spxinghaoReg:
                            spxinghao = spxinghaoReg.group('dd')

                    spcuxiaoReg = re.findall(
                        '</h.*?>\s+(<h4 class="tb-detail-sellpoint">(?P<cuxiao1>[\w\W]{0,100}?)?</h4>)?\s+<p>\s+(?P<cuxiao2>[\w\W]{0,100}?)?\s+</p>',
                        html)
                    if spcuxiaoReg:
                        for spcuxiaoS in spcuxiaoReg:
                            spcuxiao += re.sub(self.reReplace, '', ' '.join(spcuxiaoS))
                        spcuxiao = spcuxiao.lstrip().rstrip()
                    shopReg = re.search('seller_nickname" value="(?P<dd>.*?)"', html)
                    if shopReg:
                        shopname = shopReg.group('dd')
                    else:
                        shopReg = re.search('<a class="slogo-shopname" href=".*?">(?P<dd>.*?)</a>', html)
                        if shopReg:
                            shopname = shopReg.group('dd')
                        shopname = re.sub(self.reReplace, '', shopname)

                    priceUrl = re.search('"initApi"\s*?:\s*?"(?P<dd>[^"]*?)",', response.body).group('dd')
                    if 'https:' not in priceUrl:
                        priceUrl = 'https:' + priceUrl + '&callback=setMdskip&timestamp=' + str(int(time.time() * 1000))
                    headers = {
                        "Accept": "*/*",
                        "Referer": spurl,
                        # "Cookie": self.cookie
                    }
                    item['spurl'] = spurl
                    item['urlweb'] = urlweb
                    item['pc'] = pc
                    item['spname'] = spname
                    item['spleibie'] = spleibie
                    item['sppinpai'] = self.h.unescape(sppinpai)
                    item['spxinghao'] = self.h.unescape(spxinghao)
                    item['webprice'] = webprice
                    item['spcuxiao'] = spcuxiao
                    item['shopname'] = shopname
                    item['xiaoshoutype'] = xiaoshoutype
                    yield Request(priceUrl, callback=self.parsePriceinfoTM, headers=headers, dont_filter=True,
                                  meta={'spurl': spurl, 'priceUrl': priceUrl, 'item': item})

        except Exception, ex:
            print 'parseTM error:', ex
            self.log("parseTM error:" + str(ex), level=logging.ERROR)

    def parsePriceinfoTM(self, response):
        try:
            print '2' * 50
            spurl = response.meta['spurl']
            priceUrl = response.meta['priceUrl']
            iteminfo = response.meta['item']
            cxprice = ''
            sellcount = '0'
            quantity = '0'
            if 'window.location.href=' in str(response.body):
                # self.log('parsePriceinfoTM:' + str(response.body), level=logging.ERROR)
                print 'IP被封122222------------------------------'
                headers = {
                    "Accept": "*/*",
                    "Referer": spurl,
                    # "Cookie": self.cookie
                }
                yield Request(priceUrl, callback=self.parsePriceinfoTM, headers=headers, dont_filter=True,
                              meta={'spurl': spurl, 'priceUrl': priceUrl, 'item': iteminfo})
            else:
                html = str(response.body).decode('gbk').encode('utf8')
                try:
                    sellcountReg = re.search('sellCount":(?P<dd>\d+)', html)
                    if sellcountReg:
                        sellcount = str(sellcountReg.group('dd'))
                        if sellcount == '' or sellcount.lower() == 'null' or sellcount == 'None':
                            sellcount = '0'
                            # print sellcount, '+++++++++++++++++'
                    spjgMTempReg = re.search('priceInfo":{(?P<dd>.*?)}},', html)
                    if spjgMTempReg:
                        spjgMTemp = spjgMTempReg.group('dd')
                        skuSReg = re.findall('"(?P<dd>[^"]*?)":{', spjgMTemp)
                        if len(skuSReg) > 0:
                            for skuid in skuSReg:
                                item = SellCountItem()
                                try:
                                    if re.match('\d+$', str(skuid)):
                                        quantityReg = re.search('"%s":{"quantity":(?P<dd>\d+)' % str(skuid), html)
                                        if quantityReg:
                                            quantity = quantityReg.group('dd')
                                        regStr = re.compile(
                                            '"%s"[^}]*?promotionList[^}]*?"price":"(?P<dd>\d+\.\d+)"' % str(skuid))
                                        if 'promotionList' not in html:
                                            regStr = re.compile(
                                                '"%s":{"areaSold":true.*?"price":"(?P<dd>\d+\.\d+)"' % str(skuid))
                                        cxPriceReg = re.search(regStr, html)
                                        if cxPriceReg:
                                            cxprice = cxPriceReg.group('dd')
                                    else:
                                        quantity = '0'
                                        priceM = re.search('"priceInfo"[\s\S]*?}}', html).group()
                                        spjgS = re.findall('"price":"(?P<dd>.*?)"', priceM)
                                        if len(spjgS) > 0:
                                            cxprice = str(spjgS[0])
                                            for i in range(len(spjgS)):
                                                try:
                                                    if float(cxprice) > float(str(spjgS[i])) and float(
                                                            str(spjgS[i])) > 0:
                                                        cxprice = str(spjgS[i])
                                                except:
                                                    pass
                                    if cxprice == '':
                                        cxprice = iteminfo['webprice']
                                except:
                                    pass
                                item['spurl'] = spurl
                                item['urlweb'] = iteminfo['urlweb']
                                item['pc'] = iteminfo['pc']
                                item['spname'] = iteminfo['spname']
                                item['spleibie'] = iteminfo['spleibie']
                                item['sppinpai'] = iteminfo['sppinpai']
                                item['spxinghao'] = iteminfo['spxinghao']
                                item['webprice'] = iteminfo['webprice']
                                item['shopname'] = iteminfo['shopname']
                                item['cxprice'] = cxprice
                                item['spcuxiao'] = iteminfo['spcuxiao']
                                item['skuid'] = skuid
                                item['spplriqi'] = time.strftime('%Y-%m-%d %H:00:00', time.localtime())
                                item['quantity'] = quantity
                                item['sellcount'] = sellcount
                                item['xiaoshoutype'] = iteminfo['xiaoshoutype']
                                item['collectiontime'] = str(datetime.datetime.now())
                                print item
                                yield item

                except Exception, ex:
                    self.log("parsePriceinfoTM error:" + str(ex), level=logging.ERROR)
        except Exception, exx:
            print 'parsePriceinfoTM2 error:', exx
            self.log("parsePriceinfoTM2 error:" + str(exx), level=logging.ERROR)

    # 淘宝网
    def parseTB(self, response):
        taskInfo = response.meta['taskInfo']
        spurl = taskInfo['Urls']
        urlweb = taskInfo['Urlweb']
        pc = taskInfo.get('pc', '')
        spname = ''
        spleibie = taskInfo['Urlleibie']
        sppinpai = taskInfo['spbjpinpai']
        spxinghao = taskInfo['spbjjixing']
        webprice = ''
        spcuxiao = ''
        shopname = ''
        xiaoshoutype = ''
        item = SellCountItem()
        try:
            html = str(response.body).decode('gbk').encode('utf8')

            if '亲，访问受限了' in html or '小二在紧急处理，稍后再来哦' in html:
                print 'IP被封1333333333333'
                yield Request(spurl, callback=self.parseTB, meta={'taskInfo': taskInfo}, dont_filter=True)
            else:
                spnameReg = re.search('<h3 class=".*?">(?P<dd>[\s\S]*?)</h3>', html)
                if spnameReg:
                    spname = spnameReg.group('dd')
                if spname != '':
                    spname = spname.replace('\r', '').replace('\n', '')
                    spname = re.sub(self.reReplace, '', spname)
                    spname = spname.lstrip().rstrip()

                    shopReg = re.search('">(?P<dd>.*?)<i id="J_TEnterShop">进入店铺</i></a>', html)
                    if shopReg:
                        shopname = shopReg.group('dd')
                    else:
                        shopReg = re.search('tb-shop-name">[\s\S]*?" title="(?P<dd>.*?)" target=', html)
                        if shopReg:
                            shopname = shopReg.group('dd')
                    shopname = re.sub(self.reReplace, '', shopname)

                    sppinpaiReg = re.search('品牌[^"]{0,5}:(?P<dd>.*?)</li>', html)
                    if sppinpaiReg:
                        sppinpai = sppinpaiReg.group('dd')
                        sppinpai = re.sub(self.reReplace, '', sppinpai)
                    spxinghaoReg = re.search('型号[^"]{0,5}:(?P<dd>.*?)</li>', html)
                    if spxinghaoReg:
                        spxinghao = spxinghaoReg.group('dd')
                        spxinghao = re.sub(self.reReplace, '', spxinghao)

                    webPriceReg = re.search(
                        '<strong id="J_StrPrice.*?><em class="tb-rmb">&yen;</em><em class="tb-rmb-num">(?P<dd>.*?)</em>',
                        html)
                    if webPriceReg:
                        webprice = webPriceReg.group('dd')

                    item['spurl'] = spurl
                    item['urlweb'] = urlweb
                    item['pc'] = pc
                    item['spname'] = spname
                    item['spleibie'] = spleibie
                    item['sppinpai'] = sppinpai
                    item['spxinghao'] = spxinghao
                    item['webprice'] = webprice
                    item['spcuxiao'] = spcuxiao
                    item['shopname'] = shopname
                    item['xiaoshoutype'] = xiaoshoutype

                    sellcountUrlReg = re.search("wholeSibUrl      : '(?P<dd>.*?)'", response.body)
                    sellcountUrl = ''
                    if sellcountUrlReg:
                        sellcountUrl = sellcountUrlReg.group('dd')
                    else:
                        sellcountUrlReg = re.search('wholeSibUrl":"(?P<dd>.*?)"', response.body)
                        if sellcountUrlReg:
                            sellcountUrl = sellcountUrlReg.group('dd')
                    if sellcountUrl != '':
                        if 'https:' not in sellcountUrl:
                            sellcountUrl = 'https:' + sellcountUrl

                        priceUrl = re.search("sibUrl           : '(?P<dd>.*?)'", response.body).group('dd')
                        if len(priceUrl) > 15 and len(sellcountUrl) > 15:
                            if 'https:' not in priceUrl:
                                priceUrl = 'https:' + priceUrl
                            headers = {
                                "Accept": "*/*",
                                "Referer": spurl,
                                "Cookie": self.cookie
                            }
                            yield Request(priceUrl, callback=self.parsePriceinfoTB, headers=headers, dont_filter=True,
                                          meta={'spurl': spurl, 'priceUrl': priceUrl, 'sellcountUrl': sellcountUrl,
                                                'item': item})
        except Exception, ex:
            print 'parseTB error:', ex
            self.log("parseTB error:" + str(ex), level=logging.ERROR)

    def parsePriceinfoTB(self, response):
        try:
            spurl = response.meta['spurl']
            priceUrl = response.meta['priceUrl']
            sellcountUrl = response.meta['sellcountUrl']
            iteminfo = response.meta['item']
            cxprice = ''
            if 'window.location.href=' in str(response.body):
                print 'IP被封1444444444444444'
                headers = {
                    "Accept": "*/*",
                    "Referer": spurl,
                    "Cookie": self.cookie
                }
                yield Request(priceUrl, callback=self.parsePriceinfoTB, headers=headers, dont_filter=True,
                              meta={'spurl': spurl, 'priceUrl': priceUrl, 'item': iteminfo})
            else:
                html = str(response.body).decode('gbk').encode('utf8')
                try:
                    spjgSReg = re.findall(',"price":"(?P<dd>[^"]*?)","start', html)
                    if spjgSReg:
                        cxprice = spjgSReg[0]
                        for ii in range(len(spjgSReg)):
                            try:
                                if float(cxprice) > float(spjgSReg[ii]):
                                    cxprice = spjgSReg[ii]
                            except:
                                pass
                    else:
                        cxprice = iteminfo['webprice']

                except Exception, ex:
                    self.log("parsePriceinfoTB error:" + str(ex), level=logging.ERROR)
                iteminfo['cxprice'] = cxprice

                headers = {
                    "Accept": "*/*",
                    "Referer": spurl,
                    "Cookie": self.cookie
                }
                yield Request(sellcountUrl, callback=self.parseSellcountTB, headers=headers, dont_filter=True,
                              meta={'spurl': spurl, 'sellcountUrl': sellcountUrl, 'item': iteminfo})

        except Exception, exx:
            print 'parsePriceinfoTB2 error:', exx
            self.log("parsePriceinfoTB2 error:" + str(exx), level=logging.ERROR)

    def parseSellcountTB(self, response):
        try:
            spurl = response.meta['spurl']
            sellcountUrl = response.meta['sellcountUrl']
            iteminfo = response.meta['item']
            sellcount = '0'
            if 'window.location.href=' in str(response.body):
                print 'IP被封15555555555555'
                headers = {
                    "Accept": "*/*",
                    "Referer": spurl,
                    "Cookie": self.cookie
                }
                yield Request(sellcountUrl, callback=self.parseSellcountTB, headers=headers, dont_filter=True,
                              meta={'spurl': spurl, 'sellcountUrl': sellcountUrl, 'item': iteminfo})
            else:
                html = str(response.body).decode('gbk').encode('utf8')
                try:
                    sellcountReg = re.search('confirmGoods:(?P<dd>\d+)', html)
                    if sellcountReg:
                        sellcount = str(sellcountReg.group('dd'))
                        if sellcount == '' or sellcount.lower() == 'null' or sellcount == 'None':
                            sellcount = '0'

                    iteminfo['sellcount'] = sellcount
                    iteminfo['spplriqi'] = time.strftime('%Y-%m-%d %H:00:00', time.localtime())
                    iteminfo['skuid'] = ''
                    iteminfo['quantity'] = ''
                    iteminfo['collectiontime'] = str(datetime.datetime.now())
                    print iteminfo
                    yield iteminfo

                except Exception, ex:
                    print 'parseSellcountTB2 error:', ex
                    self.log("parseSellcountTB2 error:" + str(ex), level=logging.ERROR)
        except Exception, exx:
            print 'parseSellcountTB error:', exx
            self.log("parseSellcountTB error:" + str(exx), level=logging.ERROR)
