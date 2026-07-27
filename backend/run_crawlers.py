"""爬虫运行脚本"""
import asyncio
import sys
import os
import logging

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from app.database import init_db, SessionLocal
from app.crud import create_promotion, is_duplicate
from app.spiders.spider_manager import spider_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_crawlers():
    """运行所有爬虫"""
    logger.info("开始运行爬虫...")
    
    # 初始化数据库
    init_db()
    db = SessionLocal()
    
    try:
        # 爬取所有银行活动
        activities = await spider_manager.crawl_all()
        
        saved_count = 0
        duplicate_count = 0
        
        for activity in activities:
            # 检查是否重复
            if is_duplicate(db, activity):
                duplicate_count += 1
                continue
            
            # 保存到数据库
            create_promotion(db, activity)
            saved_count += 1
            logger.info(f"保存活动: {activity.get('title')}")
        
        logger.info(f"爬取完成: 总计 {len(activities)} 条, 新增 {saved_count} 条, 重复 {duplicate_count} 条")
        
    finally:
        db.close()


def main():
    """主函数"""
    asyncio.run(run_crawlers())


if __name__ == "__main__":
    main()
