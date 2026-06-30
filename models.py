from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active_user = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    # 关联行程
    schedules = db.relationship('Schedule', backref='creator', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256:600000')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Schedule(db.Model):
    __tablename__ = 'schedules'
    __table_args__ = (
        db.Index('idx_schedule_type', 'group_type'),
        db.Index('idx_schedule_date', 'event_date'),
        db.Index('idx_schedule_creator', 'creator_id'),
    )

    id = db.Column(db.Integer, primary_key=True)

    # 行程信息
    star_name = db.Column(db.String(200), nullable=False, index=True)  # 艺人名称
    event_name = db.Column(db.String(500), nullable=False)  # 活动名称
    event_date = db.Column(db.Date, nullable=True)  # 活动日期
    event_time = db.Column(db.String(50), nullable=True)  # 活动时间（可选，灵活格式）
    event_location = db.Column(db.String(500), nullable=True)  # 活动地点
    event_image = db.Column(db.String(500), nullable=True)  # 活动图片路径
    description = db.Column(db.Text, nullable=True)  # 补充描述

    # 分类：solo 单人 / duo 双人 / group 多人
    group_type = db.Column(db.String(20), nullable=False, index=True)

    # 元信息
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 多语言支持字段
    star_name_en = db.Column(db.String(200), nullable=True)
    star_name_th = db.Column(db.String(200), nullable=True)
    event_name_en = db.Column(db.String(500), nullable=True)
    event_name_th = db.Column(db.String(500), nullable=True)
    event_location_en = db.Column(db.String(500), nullable=True)
    event_location_th = db.Column(db.String(500), nullable=True)

    def to_dict(self, lang='en'):
        """根据语言返回对应数据"""
        data = {
            'id': self.id,
            'star_name': self._get_localized('star_name', lang),
            'event_name': self._get_localized('event_name', lang),
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'event_time': self.event_time,
            'event_location': self._get_localized('event_location', lang),
            'event_image': self.event_image,
            'description': self.description,
            'group_type': self.group_type,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        return data

    def _get_localized(self, field, lang):
        """获取本地化字段值"""
        if lang == 'en':
            en_val = getattr(self, f'{field}_en', None)
            return en_val if en_val else getattr(self, field)
        elif lang == 'th':
            th_val = getattr(self, f'{field}_th', None)
            return th_val if th_val else getattr(self, field)
        return getattr(self, field)


class ScheduleImage(db.Model):
    __tablename__ = 'schedule_images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(500), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id', ondelete='CASCADE'), nullable=False)

    schedule = db.relationship('Schedule', backref=db.backref('images', lazy='dynamic', cascade='all, delete-orphan', order_by='ScheduleImage.sort_order'))
