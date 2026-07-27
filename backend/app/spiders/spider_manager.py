"""爬虫管理器"""
import asyncio
import logging
from typing import List, Dict

from .abc_spider import ABCSpider
from .cgb_spider import CGBSpider
from .citic_spider import CITICSpider
from .ccb_spider import CCBSpider
from .zuanke8_spider import Zuanke8Spider

logger = logging.getLogger(__name__)


class SpiderManager:
    """爬虫管理器 - 协调所有爬虫"""
    
    def __init__(self):
        self.bank_spiders = [
            ABCSpider(),
            CGBSpider(),
            CITICSpider(),
            CCBSpider()
        ]
        self.zuanke8_spider = Zuanke8Spider()
    
    async def crawl_all(self) -> List[Dict]:
        """爬取所有来源活动"""
        all_activities = []
        
        # 爬取银行官方活动
        for spider in self.bank_spiders:
            try:
                activities = await spider.crawl()
                all_activities.extend(activities)
                logger.info(f"{spider.name} 爬取完成，获取 {len(activities)} 条活动")
            except Exception as e:
                logger.error(f"{spider.name} 爬取失败: {e}")
        
        # 爬取赚客吧
        try:
            activities = await self.zuanke8_spider.crawl()
            all_activities.extend(activities)
            logger.info(f"赚客吧 爬取完成，获取 {len(activities)} 条活动")
        except Exception as e:
            logger.error(f"赚客吧 爬取失败: {e}")
        
        logger.info(f"总计爬取 {len(all_activities)} 条活动")
        return all_activities
    
    async def crawl_zuanke8(self) -> List[Dict]:
        """爬取赚客吧活动"""
        return await self.zuanke8_spider.crawl()


# 全局实例
spider_manager = SpiderManager()
