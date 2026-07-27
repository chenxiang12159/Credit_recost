"""爬虫基类"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseSpider(ABC):
    """银行爬虫基类"""
    
    def __init__(self):
        self.name: str = ""
        self.base_url: str = ""
        self.headers: Dict = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    @abstractmethod
    async def crawl(self) -> List[Dict]:
        """爬取活动列表"""
        pass
    
    @abstractmethod
    def parse_activity(self, html_content: str) -> List[Dict]:
        """解析活动内容"""
        pass
    
    def normalize_activity(self, activity: Dict) -> Dict:
        """标准化活动数据格式"""
        return {
            'title': activity.get('title', ''),
            'bank': self.name,
            'promo_type': activity.get('promo_type', '其他'),
            'start_date': self.parse_date(activity.get('start_date')),
            'end_date': self.parse_date(activity.get('end_date')),
            'content': activity.get('content', ''),
            'images': activity.get('images', []),
            'author': activity.get('author', ''),
            'rating': activity.get('rating', 0),
            'url': activity.get('url', ''),
            'qrcode_url': activity.get('qrcode_url', ''),
            'source': f'{self.name}_official'
        }
    
    def parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y年%m月%d日',
            '%Y.%m.%d',
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return date_str
