"""AI 解析模块 - 使用 DeepSeek API 提取结构化信息"""
import os
import json
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AIParser:
    """AI 内容解析器"""
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
    
    async def extract_promotion(self, content: str) -> Optional[dict]:
        """从文本内容提取活动信息"""
        if not self.api_key:
            logger.error("DeepSeek API Key 未设置")
            return None
        
        prompt = self._build_prompt(content)
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "你是一个专业的银行活动信息提取助手。"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    return self._parse_response(content)
                else:
                    logger.error(f"DeepSeek API 调用失败: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"AI 解析异常: {e}")
            return None
    
    def _build_prompt(self, content: str) -> str:
        """构建提示词"""
        return f"""请从以下内容中提取银行/平台活动信息，返回 JSON 格式。

返回格式要求：
{{
    "title": "活动标题（必填）",
    "bank": "银行/平台名称（必填）",
    "promo_type": "活动类型：返现/折扣/积分/礼品/其他",
    "start_date": "开始日期，格式 YYYY-MM-DD（如有）",
    "end_date": "结束日期，格式 YYYY-MM-DD（如有）",
    "content": "活动内容摘要（100字以内）",
    "url": "活动参与链接（如有）",
    "qrcode_url": "二维码图片URL（如有）"
}}

注意：
1. 如果某个字段信息不存在，设为 null
2. 日期格式统一为 YYYY-MM-DD
3. 银行名称使用标准名称（如：中国农业银行、中国银行、中国工商银行、广发银行、中国建设银行、中信银行）

需要提取的内容：
{content}
"""
    
    def _parse_response(self, content: str) -> Optional[dict]:
        """解析 AI 返回的 JSON"""
        try:
            # 尝试直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            # 尝试提取 JSON 部分
            import re
            json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            logger.error(f"JSON 解析失败: {content}")
            return None


# 全局实例
parser = AIParser()
