"""数据库 CRUD 操作"""
import uuid
from datetime import datetime, date
from sqlalchemy.orm import Session
from .database import Promotion, PushLog


def parse_date(date_str):
    """将字符串转换为 date 对象"""
    if not date_str:
        return None
    if isinstance(date_str, date):
        return date_str
    if isinstance(date_str, datetime):
        return date_str.date()
    
    # 尝试解析字符串
    date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日', '%Y.%m.%d']
    for fmt in date_formats:
        try:
            return datetime.strptime(str(date_str), fmt).date()
        except ValueError:
            continue
    return None


def create_promotion(db: Session, promo_data: dict) -> Promotion:
    """创建活动记录"""
    import json
    
    images = promo_data.get('images')
    if isinstance(images, list):
        images = json.dumps(images, ensure_ascii=False)
    elif images is None:
        images = '[]'
    
    promotion = Promotion(
        uuid=str(uuid.uuid4()),
        title=promo_data.get('title'),
        bank=promo_data.get('bank'),
        promo_type=promo_data.get('promo_type'),
        start_date=parse_date(promo_data.get('start_date')),
        end_date=parse_date(promo_data.get('end_date')),
        content=promo_data.get('content'),
        images=images,
        author=promo_data.get('author'),
        rating=promo_data.get('rating', 0),
        url=promo_data.get('url'),
        qrcode_url=promo_data.get('qrcode_url'),
        source=promo_data.get('source', 'manual'),
        status='active'
    )
    db.add(promotion)
    db.commit()
    db.refresh(promotion)
    return promotion


def is_duplicate(db: Session, promo_data: dict) -> bool:
    """检查活动是否已存在（去重）"""
    title = promo_data.get('title')
    bank = promo_data.get('bank')
    start_date = promo_data.get('start_date')
    
    if not title or not bank:
        return False
    
    existing = db.query(Promotion).filter(
        Promotion.title == title,
        Promotion.bank == bank,
        Promotion.start_date == start_date
    ).first()
    
    return existing is not None


def get_latest_promotions(db: Session, limit: int = 20) -> list:
    """获取最新活动列表"""
    return db.query(Promotion)\
        .filter(Promotion.status == 'active')\
        .order_by(Promotion.created_at.desc())\
        .limit(limit)\
        .all()


def get_paginated_promotions(db: Session, page: int = 1, page_size: int = 20,
                             keyword: str = None, bank: str = None, promo_type: str = None) -> dict:
    """分页获取活动列表"""
    from sqlalchemy import func

    query = db.query(Promotion).filter(Promotion.status == 'active')

    if keyword:
        query = query.filter(Promotion.title.contains(keyword))
    if bank:
        query = query.filter(Promotion.bank == bank)
    if promo_type:
        query = query.filter(Promotion.promo_type == promo_type)

    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))

    items = query.order_by(Promotion.rating.desc(), Promotion.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def get_promotion_by_uuid(db: Session, promo_uuid: str) -> Promotion:
    """根据 UUID 获取活动"""
    return db.query(Promotion).filter(Promotion.uuid == promo_uuid).first()


def archive_expired(db: Session) -> int:
    """归档过期活动"""
    today = date.today()
    count = db.query(Promotion)\
        .filter(
            Promotion.status == 'active',
            Promotion.end_date < today
        )\
        .update({'status': 'expired'})
    db.commit()
    return count


def create_push_log(db: Session, promotion_id: int, channel: str, status: str, error_msg: str = None):
    """创建推送记录"""
    log = PushLog(
        promotion_id=promotion_id,
        channel=channel,
        status=status,
        error_msg=error_msg
    )
    db.add(log)
    db.commit()


def is_pushed(db: Session, promotion_id: int, channel: str) -> bool:
    """检查是否已推送"""
    return db.query(Promotion).filter(
        PushLog.promotion_id == promotion_id,
        PushLog.channel == channel,
        PushLog.status == 'success'
    ).first() is not None


def get_db_stats(db: Session) -> dict:
    """获取数据库统计信息（用于爬取前后对比）"""
    from sqlalchemy import func
    
    result = db.query(
        func.count(Promotion.id),
        func.max(Promotion.created_at)
    ).filter(Promotion.status == 'active').first()
    
    return {
        "count": result[0] or 0,
        "latest": str(result[1]) if result[1] else ""
    }
