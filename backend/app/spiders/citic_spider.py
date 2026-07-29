"""中信银行爬虫"""
import httpx
import logging
from typing import List, Dict

from .base_spider import BaseSpider

logger = logging.getLogger(__name__)


class CITICSpider(BaseSpider):
    """中信银行信用卡活动爬虫"""
    
    def __init__(self):
        super().__init__()
        self.name = "中信银行"
        self.base_url = "https://creditcard.citicbank.cn"
        # 首页 youhui 是导航，真实活动在子列表页
        self.activity_urls = [
            "https://creditcard.citicbank.cn/youhui/",
            "https://creditcard.ecitic.com/youhui/shuakahuodong.shtm",
        ]
    
    async def crawl(self) -> List[Dict]:
        """爬取中信银行活动"""
        all_activities = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                for url in self.activity_urls:
                    response = await client.get(url, headers=self.headers)
                    response.raise_for_status()
                    activities = self.parse_activity(response.text)
                    all_activities.extend(activities)
                    
                logger.info(f"中信银行爬取成功，获取 {len(all_activities)} 条活动")
        except Exception as e:
            logger.error(f"中信银行爬取失败: {e}")
        
        return all_activities
    
    def parse_activity(self, html_content: str, page_url: str = None) -> List[Dict]:
        """解析中信银行活动页面"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        items = self.extract_activities(soup, self.base_url, max_items=20, page_url=page_url or self.activity_urls[0])
        return [self.normalize_activity(a) for a in items]
    
    def _detect_type(self, title: str) -> str:
        """根据标题检测活动类型"""
        title_lower = title.lower()
        if '返现' in title_lower or 'cashback' in title_lower:
            return '返现'
        elif '折扣' in title_lower or '减' in title_lower:
            return '折扣'
        elif '积分' in title_lower:
            return '积分'
        elif '礼' in title_lower or '赠' in title_lower:
            return '礼品'
        return '其他'
