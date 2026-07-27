"""建设银行爬虫"""
import httpx
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Dict

from .base_spider import BaseSpider

logger = logging.getLogger(__name__)


class CCBSpider(BaseSpider):
    """建设银行信用卡活动爬虫"""
    
    def __init__(self):
        super().__init__()
        self.name = "中国建设银行"
        self.base_url = "https://www2.ccb.com"
        self.activity_url = "https://www2.ccb.com/chn/bj/faverable/index.shtml"
    
    async def crawl(self) -> List[Dict]:
        """爬取建设银行活动"""
        activities = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(self.activity_url, headers=self.headers)
                response.raise_for_status()
                activities = self.parse_activity(response.text)
                logger.info(f"建设银行爬取成功，获取 {len(activities)} 条活动")
        except Exception as e:
            logger.error(f"建设银行爬取失败: {e}")
        
        return activities
    
    def parse_activity(self, html_content: str) -> List[Dict]:
        """解析建设银行活动页面"""
        activities = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        activity_items = soup.find_all(['div', 'li', 'a'], class_=re.compile(r'(activity|promo|item)', re.I))
        
        for item in activity_items[:20]:
            try:
                title_elem = item.find(['a', 'span', 'h3', 'h4'])
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                if not title or len(title) < 5:
                    continue
                
                link = ''
                if title_elem.name == 'a' and title_elem.get('href'):
                    link = title_elem['href']
                    if not link.startswith('http'):
                        link = self.base_url + link
                
                date_text = item.get_text()
                dates = re.findall(r'(\d{4}[-/年.]\d{1,2}[-/月.]\d{1,2})', date_text)
                
                activity = {
                    'title': title,
                    'url': link,
                    'start_date': dates[0] if dates else None,
                    'end_date': dates[1] if len(dates) > 1 else None,
                    'content': item.get_text(strip=True)[:200],
                    'promo_type': self._detect_type(title)
                }
                activities.append(self.normalize_activity(activity))
            except Exception as e:
                logger.warning(f"解析建设银行活动项失败: {e}")
        
        return activities
    
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
