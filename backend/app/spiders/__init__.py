"""银行爬虫模块"""
from .abc_spider import ABCSpider
from .icbc_spider import ICBCSpider
from .cgb_spider import CGBSpider
from .boc_spider import BOCSpider
from .citic_spider import CITICSpider
from .ccb_spider import CCBSpider

__all__ = [
    'ABCSpider',
    'ICBCSpider', 
    'CGBSpider',
    'BOCSpider',
    'CITICSpider',
    'CCBSpider'
]
