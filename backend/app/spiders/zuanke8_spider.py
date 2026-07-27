"""赚客吧爬虫 - 深度爬取帖子内容+图片"""
import httpx
from bs4 import BeautifulSoup
import re
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

from .base_spider import BaseSpider

logger = logging.getLogger(__name__)


class Zuanke8Spider(BaseSpider):
    """赚客吧爬虫 - 含帖子内容+图片"""
    
    def __init__(self):
        super().__init__()
        self.name = "赚客吧"
        self.base_url = "https://www.zuanke8.com"
        self.cookie_file = Path(__file__).parent.parent.parent / "cookies" / "zuanke8_cookies.txt"
        self.cookies = self._load_cookies()
        
        # 赚客吧版块
        self.board_urls = [
            f"{self.base_url}/forum-2-1.html",   # 免费赠品
            f"{self.base_url}/forum-13-1.html",  # 有奖活动
            f"{self.base_url}/forum-15-1.html",  # 赚客大家谈
        ]
    
    def _load_cookies(self) -> Dict[str, str]:
        """从 Netscape 格式文件加载 cookies"""
        cookies = {}
        if not self.cookie_file.exists():
            logger.warning(f"Cookie 文件不存在: {self.cookie_file}")
            return cookies
        
        try:
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split('\t')
                    if len(parts) >= 7:
                        cookies[parts[5]] = parts[6]
            logger.info(f"加载了 {len(cookies)} 个 cookies")
        except Exception as e:
            logger.error(f"加载 cookie 文件失败: {e}")
        
        return cookies
    
    async def crawl(self) -> List[Dict]:
        """爬取赚客吧活动（含帖子内容）"""
        all_activities = []
        
        if not self.cookies:
            logger.error("没有可用的 cookies，无法访问赚客吧")
            return []
        
        try:
            async with httpx.AsyncClient(
                timeout=30.0, 
                follow_redirects=True,
                cookies=self.cookies,
                verify=False
            ) as client:
                # 检查登录状态
                if not await self._check_login(client):
                    logger.error("Cookie 已过期，请重新导出")
                    return []
                
                # 爬取各个版块
                for board_url in self.board_urls:
                    activities = await self._crawl_board(client, board_url)
                    all_activities.extend(activities)
                
                logger.info(f"赚客吧爬取完成，获取 {len(all_activities)} 条活动")
                
        except Exception as e:
            logger.error(f"赚客吧爬取失败: {e}")
        
        return all_activities
    
    async def _check_login(self, client: httpx.AsyncClient) -> bool:
        """检查登录状态"""
        try:
            response = await client.get(f"{self.base_url}/home.php?mod=spacecp")
            return 'spacecp' in response.text or '我的' in response.text
        except:
            return False
    
    async def _crawl_board(self, client: httpx.AsyncClient, board_url: str) -> List[Dict]:
        """爬取单个版块"""
        activities = []
        
        try:
            response = await client.get(board_url)
            response.raise_for_status()
            
            # 获取帖子列表
            threads = self._parse_thread_list(response.text)
            
            # 逐个获取帖子内容（限制每版块前15个）
            for thread in threads[:15]:
                try:
                    content_data = await self._fetch_thread_content(client, thread['url'])
                    if content_data:
                        thread.update(content_data)
                    activities.append(self.normalize_activity(thread))
                except Exception as e:
                    logger.warning(f"获取帖子内容失败: {thread.get('title', '')[:30]} - {e}")
                    # 即使获取内容失败，也保存标题
                    activities.append(self.normalize_activity(thread))
            
            logger.info(f"版块 {board_url} 爬取完成，获取 {len(activities)} 条")
            
        except Exception as e:
            logger.warning(f"版块 {board_url} 爬取失败: {e}")
        
        return activities
    
    def _parse_thread_list(self, html_content: str) -> List[Dict]:
        """解析帖子列表"""
        threads = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        thread_rows = soup.find_all('tbody', id=re.compile(r'normalthread_'))
        
        for row in thread_rows:
            try:
                thread = self._parse_thread_row(row)
                if thread:
                    threads.append(thread)
            except Exception as e:
                logger.warning(f"解析帖子行失败: {e}")
        
        return threads
    
    def _parse_thread_row(self, row) -> Optional[Dict]:
        """解析单个帖子行"""
        title_link = row.find('a', class_=re.compile(r'(s xst|title)', re.I))
        if not title_link:
            th = row.find('th')
            title_link = th.find('a') if th else None
        
        if not title_link:
            return None
        
        title = title_link.get_text(strip=True)
        if not title or len(title) < 3:
            return None
        
        link = title_link.get('href', '')
        if link and not link.startswith('http'):
            link = self.base_url + '/' + link.lstrip('/')
        
        # 获取发帖时间
        time_elem = row.find('td', class_=re.compile(r'(by|time|date)', re.I))
        post_time = ''
        if time_elem:
            time_text = time_elem.get_text(strip=True)
            dates = re.findall(r'(\d{4}[-/年.]\d{1,2}[-/月.]\d{1,2})', time_text)
            if dates:
                post_time = dates[0]
        
        # 获取作者
        author_elem = row.find('a', class_=re.compile(r'(author|user)', re.I))
        author = author_elem.get_text(strip=True) if author_elem else ''

        # 获取评分
        rating = 0
        num_td = row.find('td', class_='num')
        if num_td:
            rating_a = num_td.find('a')
            if rating_a:
                try:
                    rating = int(rating_a.get_text(strip=True))
                except (ValueError, TypeError):
                    rating = 0

        return {
            'title': title,
            'url': link,
            'start_date': post_time if post_time else None,
            'author': author,
            'rating': rating,
            'promo_type': self._detect_type(title),
            'source': 'zuanke8',
            'content': '',
            'images': []
        }
    
    async def _fetch_thread_content(self, client: httpx.AsyncClient, url: str) -> Optional[Dict]:
        """获取帖子详情页内容"""
        try:
            response = await client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取楼主帖子内容
            post_content = soup.find('td', class_='t_f')
            if not post_content:
                return None
            
            # 提取文字内容（去除附件信息）
            content_text = self._extract_text_content(post_content)
            
            # 提取图片
            images = self._extract_images(post_content)
            
            # 获取作者
            author_elem = soup.find('a', class_='xw1')
            author = author_elem.get_text(strip=True) if author_elem else None
            
            return {
                'content': content_text,
                'images': images,
                'author': author
            }
            
        except Exception as e:
            logger.warning(f"获取帖子内容失败: {url} - {e}")
            return None
    
    def _extract_text_content(self, post_element) -> str:
        """提取帖子文字内容"""
        # 克隆节点以便修改
        clone = post_element.__copy__()
        
        # 移除附件信息、图片描述等干扰内容
        for elem in clone.find_all(['div', 'p'], class_=re.compile(r'(attach|image|notice)', re.I)):
            elem.decompose()
        
        # 获取文本
        text = clone.get_text(separator='\n', strip=True)
        
        # 清理多余空行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 过滤掉纯附件信息行
        filtered = []
        for line in lines:
            # 跳过类似 "image.jpg(19.95 KB, 下载次数: 274)下载附件" 的行
            if re.match(r'^.*\(\d+[\.\d]* [KMG]B,.*下载次数.*\)', line):
                continue
            if '下载附件' in line and '上传' in line:
                continue
            # 跳过纯附件文件名（如 "1785128098352.jpg"）
            if re.match(r'^[\w\-]+\.(jpg|jpeg|png|gif|bmp|webp)$', line, re.I):
                continue
            # 跳过单独的 "下载附件"
            if line.strip() == '下载附件':
                continue
            # 跳过纯时间戳上传行（如 "2026-7-27 12:54 上传"）
            if re.match(r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}\s+上传$', line):
                continue
            filtered.append(line)
        
        return '\n'.join(filtered)
    
    def _extract_images(self, post_element) -> List[str]:
        """提取帖子图片 URL"""
        images = []
        
        for img in post_element.find_all('img'):
            # 优先使用 file 属性（完整图片URL）
            src = img.get('file') or img.get('src', '')
            
            if src and not src.startswith('data:'):
                # 确保是完整 URL
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = self.base_url + src
                
                # 过滤掉表情、图标等小图片
                if 'smiley' not in src and 'icon' not in src and len(src) > 20:
                    images.append(src)
        
        return images
    
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
    
    def parse_activity(self, html_content: str) -> List[Dict]:
        """解析活动内容（基类抽象方法实现）"""
        # 赚客吧使用自定义解析逻辑，此方法不使用
        return []


# 全局实例
zuanke8_spider = Zuanke8Spider()
