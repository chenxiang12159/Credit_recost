"""数据库模块 - SQLite + SQLAlchemy"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'promotions.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 创建数据库引擎
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Promotion(Base):
    """活动表"""
    __tablename__ = 'promotions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    bank = Column(String(100))
    promo_type = Column(String(50))  # 返现/折扣/积分/礼品
    start_date = Column(Date)
    end_date = Column(Date)
    content = Column(Text)
    images = Column(Text)  # JSON 格式的图片 URL 列表
    author = Column(String(100))  # 发帖人/来源作者
    rating = Column(Integer, default=0)  # 评分（赚客吧）
    url = Column(String(2000))
    qrcode_url = Column(String(2000))
    source = Column(String(50))  # manual/zuanke8/bank_official
    status = Column(String(20), default='active')  # active/expired
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PushLog(Base):
    """推送记录表"""
    __tablename__ = 'push_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    promotion_id = Column(Integer, nullable=False)
    channel = Column(String(20))  # telegram
    status = Column(String(20))  # success/failed
    error_msg = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
