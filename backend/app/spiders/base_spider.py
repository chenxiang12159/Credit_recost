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

    def _detect_type(self, title: str) -> str:
        """根据标题检测活动类型"""
        title_lower = title.lower()
        if any(kw in title_lower for kw in ['返现', 'cashback', '回馈', '刷卡金']):
            return '返现'
        elif any(kw in title_lower for kw in ['折扣', '减', '优惠', '立减', '满减']):
            return '折扣'
        elif any(kw in title_lower for kw in ['积分', '里程', '奖励']):
            return '积分'
        elif any(kw in title_lower for kw in ['礼', '赠', '送', '礼品', '免费', '0元']):
            return '礼品'
        elif any(kw in title_lower for kw in ['薅', '羊毛', '活动', '撸', '水']):
            return '其他'
        return '其他'

    def extract_activities(self, soup, base_url: str, max_items: int = 20, page_url: str = None) -> List[Dict]:
        """通用活动提取：找含优惠正向词、排除公告类的真实活动链接"""
        import re
        from urllib.parse import urljoin
        base = page_url or base_url
        # 正向优惠词（必须含其一才算活动）
        positive = ['满', '减', '返', '礼', '赠', '惠', '折扣', '立减', '羊毛',
                    '话费', '红包', '积分', '抽奖', '0元', '免费', '福利', '刷卡金',
                    '达标', '消费', '分期', '优惠', '活动']
        # 排除词（公告/产品/查询/设置等非活动）
        exclude = ['公告', '关于', '通知', '声明', '章程', '查询', '披露', '报告',
                   '公示', '提示', '说明', '办法', '细则', '额度', '首页',
                   '设置', '登录', '注册', '中心', '广场', '客服', '还款', '账单',
                   '积分商城', '我的', '权益', '介绍', '指南', '攻略']
        found = []
        seen = set()
        for a in soup.find_all('a'):
            text = a.get_text(strip=True)
            href = a.get('href', '')
            if not text or not href:
                continue
            if len(text) < 5 or len(text) > 40:
                continue
            # 排除非活动
            if any(w in text for w in exclude):
                continue
            # 必须含正向优惠词
            if not any(k in text for k in positive):
                continue
            # 补全URL（正确处理 ./ ../ / 等相对路径）
            full = urljoin(base, href)
            if not full.startswith('http'):
                continue
            if full in seen:
                continue
            seen.add(full)
            # 提取附近日期
            parent = a.parent
            date_text = parent.get_text() if parent else text
            dates = re.findall(r'(\d{4}[-/年.]\d{1,2}[-/月.]\d{1,2})', date_text)
            found.append({
                'title': text,
                'url': full,
                'start_date': dates[0] if dates else None,
                'end_date': dates[1] if len(dates) > 1 else None,
                'content': text[:200],
                'promo_type': self._detect_type(text),
            })
            if len(found) >= max_items:
                break
        return found
