"""爬虫管理器"""
import asyncio
import logging
from typing import List, Dict

from .cgb_spider import CGBSpider
from .citic_spider import CITICSpider
from .cmbc_spider import CMBCSpider
from .psbc_spider import PSBCSpider
from .zuanke8_spider import Zuanke8Spider

logger = logging.getLogger(__name__)


class SpiderManager:
    """爬虫管理器 - 协调所有爬虫"""
    
    def __init__(self):
        # 启用官网可爬的银行（含追进列表页的中信/民生/邮储）
        self.bank_spiders = [
            CGBSpider(),    # 广发 ✅ 一层活动页，链接真实可用
            CITICSpider(),  # 中信：追进 shuakahuodong 子列表页
            CMBCSpider(),   # 民生：直连优惠活动列表页
            PSBCSpider(),   # 邮储：优惠活动列表页
        ]
        # 农行/建行/浦发/中行/招行：官网JS渲染/404/跳首页，完全爬不到，待定
        # 各银行羊毛活动建议统一用赚客吧按银行名搜索补充
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
