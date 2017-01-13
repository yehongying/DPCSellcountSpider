# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field


# 天猫月销量
class SellCountItem(scrapy.Item):
    spurl = Field()
    urlweb = Field()
    pc = Field()
    spname = Field()
    spleibie = Field()
    sppinpai = Field()
    spxinghao = Field()
    webprice = Field()
    shopname = Field()
    cxprice = Field()
    spcuxiao = Field()
    skuid = Field()
    spplriqi = Field()
    quantity = Field()  # 库存
    sellcount = Field()  # 月销量
    xiaoshoutype = Field()  # 销售类型
    collectiontime = Field()
