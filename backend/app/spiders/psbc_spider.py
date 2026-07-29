"""邮储银行爬虫"""
import httpx
import logging
from typing import List, Dict

from .base_spider import BaseSpider

logger = logging.getLogger(__name__)


class PSBCSpider(BaseSpider):
    """邮储银行信用卡活动爬虫"""

    def __init__(self):
        super().__init__()
        self.name = "邮储银行"
        self.base_url = "https://www.psbc.com"
        # 优惠活动列表页
        self.activity_urls = [
            "https://www.psbc.com/cn/grfw/yhhd/",
            "https://www.psbc.com/cn/creditcard/",
        ]

    async def crawl(self) -> List[Dict]:
        activities = []
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                for url in self.activity_urls:
                    try:
                        response = await client.get(url, headers=self.headers)
                        response.raise_for_status()
                        activities.extend(self.parse_activity(response.text, url))
                    except Exception as e:
                        logger.warning(f"邮储银行页面 {url} 失败: {e}")
                logger.info(f"邮储银行爬取成功，获取 {len(activities)} 条活动")
        except Exception as e:
            logger.error(f"邮储银行爬取失败: {e}")
        return activities

    def parse_activity(self, html_content: str, url: str) -> List[Dict]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        base = "https://www.psbc.com"
        items = self.extract_activities(soup, base, max_items=20, page_url=url)
        return [self.normalize_activity(a) for a in items]


# 全局实例
psbc_spider = PSBCSpider()
