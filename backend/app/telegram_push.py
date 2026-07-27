"""Telegram 推送模块"""
import os
from telegram import Bot
from telegram.constants import PARSEMODE_MARKDOWN
import logging

logger = logging.getLogger(__name__)


class TelegramPusher:
    """Telegram 消息推送器"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = None
        
        if self.token and self.chat_id:
            self.bot = Bot(token=self.token)
        else:
            logger.warning("Telegram 配置未设置，推送功能不可用")
    
    async def send_promotion(self, promo: dict) -> bool:
        """发送活动信息"""
        if not self.bot:
            logger.error("Telegram Bot 未初始化")
            return False
        
        try:
            # 构建消息内容
            message = self._build_message(promo)
            
            # 如果有二维码，发送图片+文字
            if promo.get('qrcode_url'):
                await self.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=promo['qrcode_url'],
                    caption=message,
                    parse_mode=PARSEMODE_MARKDOWN
                )
            else:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=PARSEMODE_MARKDOWN
                )
            
            logger.info(f"活动推送成功: {promo.get('title')}")
            return True
            
        except Exception as e:
            logger.error(f"活动推送失败: {e}")
            return False
    
    def _build_message(self, promo: dict) -> str:
        """构建消息内容"""
        lines = []
        
        # 标题
        lines.append(f"🏦 *{promo.get('title', '未知活动')}*")
        lines.append("")
        
        # 银行/平台
        if promo.get('bank'):
            lines.append(f"📍 {promo['bank']}")
        
        # 活动类型
        if promo.get('promo_type'):
            lines.append(f"🎯 类型: {promo['promo_type']}")
        
        # 活动时间
        start = promo.get('start_date', '')
        end = promo.get('end_date', '')
        if start or end:
            lines.append(f"📅 时间: {start} ~ {end}")
        
        lines.append("")
        
        # 活动内容
        if promo.get('content'):
            content = promo['content']
            if len(content) > 500:
                content = content[:500] + "..."
            lines.append(content)
            lines.append("")
        
        # 参与链接
        if promo.get('url'):
            lines.append(f"🔗 [点击参与]({promo['url']})")
        
        return "\n".join(lines)
    
    async def send_text(self, text: str) -> bool:
        """发送纯文本消息"""
        if not self.bot:
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text
            )
            return True
        except Exception as e:
            logger.error(f"文本消息发送失败: {e}")
            return False


# 全局实例
pusher = TelegramPusher()
