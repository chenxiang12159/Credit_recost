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
                             keyword: str = None, bank: str = None, promo_type: str = None,
                             sort: str = "comprehensive") -> dict:
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

    if sort == "rating":
        items = query.order_by(Promotion.rating.desc(), Promotion.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
    elif sort == "time":
        items = query.order_by(Promotion.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
    else:
        # comprehensive: 评分×70% + 时间新鲜度×30%
        # SQLite 用 julianday 算天数差
        from sqlalchemy import literal_column
        days_diff = func.julianday(func.datetime('now')) - func.julianday(Promotion.created_at)
        score = Promotion.rating * 0.7 + (100.0 / (days_diff + 1)) * 0.3
        items = query.order_by(score.desc()) \
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


def get_xhs_candidates(db: Session, limit: int = 20) -> list:
    """小红书草稿候选：按用户规则筛选

    规则：
    - 时效 <=1天：无需看评分
    - 时效 >1天：评分 >= 5
    - 优先带图
    """
    from sqlalchemy import func
    from datetime import datetime

    now = datetime.utcnow()
    all_items = db.query(Promotion).filter(Promotion.status == 'active').all()

    candidates = []
    for p in all_items:
        # 时效计算（用 start_date 或 created_at）
        ref_date = p.start_date or (p.created_at.date() if p.created_at else None)
        if ref_date:
            from .database import Promotion as _P
            try:
                from datetime import date
                if isinstance(ref_date, date) and not isinstance(ref_date, datetime):
                    d0 = ref_date
                else:
                    d0 = ref_date.date() if isinstance(ref_date, datetime) else ref_date
                age_days = (now.date() - d0).days
            except Exception:
                age_days = 999
        else:
            age_days = 999

        has_img = bool(p.images and p.images not in ('[]', '', None))

        # 规则判断
        if age_days <= 1:
            pass  # 时效内，不看评分
        else:
            if (p.rating or 0) < 5:
                continue  # 超1天且评分不足，淘汰

        candidates.append({
            "promo": p,
            "age_days": age_days,
            "has_img": has_img,
        })

    # 排序：带图优先，其次时效新，其次评分高
    candidates.sort(key=lambda c: (not c["has_img"], c["age_days"], -(c["promo"].rating or 0)))
    return candidates[:limit]


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
