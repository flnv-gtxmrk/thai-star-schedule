import os
import uuid
import calendar
from datetime import datetime, date, timezone
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   flash, jsonify, session, g, abort)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from PIL import Image

from models import db, User, Schedule, ScheduleImage

# ─────────────────────────────────────────────
# 配置
# ─────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "thaistar.db")}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')

# ─── Session Security ───
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# ─── Upload Security ───
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_GROUP_TYPES = {'solo', 'duo', 'group'}
MAX_IMAGE_DIMENSION = 2400

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ─────────────────────────────────────────────
# 初始化扩展
# ─────────────────────────────────────────────
db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# 启动时自动初始化数据库（兼容 gunicorn / 生产环境）
with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin = User(username='admin', email='admin@startrack.com', is_admin=True)
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()


# ─────────────────────────────────────────────
# 安全响应头
# ─────────────────────────────────────────────
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    # CSP 允许本地资源、Google Fonts、Font Awesome
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data: blob:; "
        "connect-src 'self';"
    )
    return response


# ─────────────────────────────────────────────
# 输入验证
# ─────────────────────────────────────────────
import re as _re

EMAIL_REGEX = _re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
USERNAME_REGEX = _re.compile(r'^[a-zA-Z0-9_一-龥]{3,32}$')


def validate_email(email):
    return bool(email) and bool(EMAIL_REGEX.match(email))


def validate_username(username):
    return bool(username) and bool(USERNAME_REGEX.match(username))


def validate_group_type(value):
    return value in ALLOWED_GROUP_TYPES


def sanitize_text(text, max_length=500):
    """清理文本输入：去除首尾空白并截断长度"""
    if text is None:
        return ''
    return text.strip()[:max_length]


# ─────────────────────────────────────────────
# 多语言文本
# ─────────────────────────────────────────────
TRANSLATIONS = {
    'zh': {
        'site_title': 'StarTrack',
        'home': '首页',
        'add_schedule': '添加行程',
        'login': '登录',
        'register': '注册',
        'logout': '退出',
        'my_schedules': '个人主页',
        'calendar': '日历',
        'all_schedules': '全部行程',
        'star_name': '艺人名称',
        'event_name': '活动名称',
        'event_date': '活动日期',
        'event_time': '活动时间',
        'event_location': '活动地点',
        'event_image': '活动图片',
        'description': '补充说明',
        'group_type': '活动类型',
        'solo': '单人',
        'duo': '双人',
        'group': '多人',
        'submit': '提交',
        'save': '保存',
        'cancel': '取消',
        'edit': '编辑',
        'delete': '删除',
        'confirm_delete': '确认删除此行程？',
        'no_schedules': '暂无行程数据',
        'username': '用户名',
        'email': '邮箱',
        'password': '密码',
        'confirm_password': '确认密码',
        'welcome': 'StarTrack',
        'subtitle': '明星行程追踪平台',
        'search': '搜索',
        'filter': '筛选',
        'all': '全部',
        'optional': '选填',
        'upload_image': '上传图片',
        'drag_drop': '拖拽或点击上传',
        'max_size': '最大 16MB',
        'login_required': '请先登录',
        'unauthorized': '无权操作',
        'success_add': '行程添加成功',
        'success_edit': '行程更新成功',
        'success_delete': '行程已删除',
        'error_occurred': '发生错误',
        'password_mismatch': '两次密码不一致',
        'username_exists': '用户名已存在',
        'email_exists': '邮箱已注册',
        'invalid_credentials': '用户名或密码错误',
        'invalid_username': '用户名格式无效（3-32位，仅限字母、数字、下划线、中文）',
        'invalid_email': '邮箱格式无效',
        'password_too_short': '密码至少需要6位',
        'invalid_group_type': '活动类型无效',
        'invalid_date': '日期格式无效',
        'invalid_image': '图片上传失败，请检查文件格式',
        'required_fields_missing': '请填写必填项',
        'page': '页',
        'prev': '上一页',
        'next': '下一页',
        'footer_text': '© 2026 StarTrack. All rights reserved.',
        'filter_all': '全部',
        'filter_solo': '单人',
        'filter_duo': '双人',
        'filter_group': '多人',
        'refresh': '刷新',
        'multi_image': '支持多张图片',
        'year': '年',
        'month': '月',
        'day': '日',
        'all_dates': '全部日期',
    },
    'en': {
        'site_title': 'StarTrack',
        'home': 'Home',
        'add_schedule': 'Add Schedule',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'my_schedules': 'Profile',
        'calendar': 'Calendar',
        'all_schedules': 'All Schedules',
        'star_name': 'Star Name',
        'event_name': 'Event Name',
        'event_date': 'Event Date',
        'event_time': 'Event Time',
        'event_location': 'Location',
        'event_image': 'Event Image',
        'description': 'Description',
        'group_type': 'Type',
        'solo': 'Solo',
        'duo': 'Duo',
        'group': 'Group',
        'submit': 'Submit',
        'save': 'Save',
        'cancel': 'Cancel',
        'edit': 'Edit',
        'delete': 'Delete',
        'confirm_delete': 'Delete this schedule?',
        'no_schedules': 'No schedules yet',
        'username': 'Username',
        'email': 'Email',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'welcome': 'StarTrack',
        'subtitle': 'Celebrity Schedule Tracker',
        'search': 'Search',
        'filter': 'Filter',
        'all': 'All',
        'optional': 'Optional',
        'upload_image': 'Upload Image',
        'drag_drop': 'Drag & drop or click to upload',
        'max_size': 'Max 16MB',
        'login_required': 'Please login first',
        'unauthorized': 'Unauthorized',
        'success_add': 'Schedule added successfully',
        'success_edit': 'Schedule updated',
        'success_delete': 'Schedule deleted',
        'error_occurred': 'An error occurred',
        'password_mismatch': 'Passwords do not match',
        'username_exists': 'Username already taken',
        'email_exists': 'Email already registered',
        'invalid_credentials': 'Invalid credentials',
        'invalid_username': 'Invalid username (3-32 chars, letters/numbers/underscore/Chinese)',
        'invalid_email': 'Invalid email format',
        'password_too_short': 'Password must be at least 6 characters',
        'invalid_group_type': 'Invalid event type',
        'invalid_date': 'Invalid date format',
        'invalid_image': 'Image upload failed, please check the file format',
        'required_fields_missing': 'Please fill in all required fields',
        'page': 'Page',
        'prev': 'Previous',
        'next': 'Next',
        'footer_text': '© 2026 StarTrack. All rights reserved.',
        'filter_all': 'All',
        'filter_solo': 'Solo',
        'filter_duo': 'Duo',
        'filter_group': 'Group',
        'refresh': 'Refresh',
        'multi_image': 'Multiple images supported',
        'year': 'Year',
        'month': 'Month',
        'day': 'Day',
        'all_dates': 'All Dates',
    },
    'th': {
        'site_title': 'StarTrack',
        'home': 'หน้าแรก',
        'add_schedule': 'เพิ่มกำหนดการ',
        'login': 'เข้าสู่ระบบ',
        'register': 'สมัครสมาชิก',
        'logout': 'ออกจากระบบ',
        'my_schedules': 'โปรไฟล์',
        'calendar': 'ปฏิทิน',
        'all_schedules': 'กำหนดการทั้งหมด',
        'star_name': 'ชื่อศิลปิน',
        'event_name': 'ชื่อกิจกรรม',
        'event_date': 'วันที่',
        'event_time': 'เวลา',
        'event_location': 'สถานที่',
        'event_image': 'รูปภาพ',
        'description': 'คำอธิบาย',
        'group_type': 'ประเภท',
        'solo': 'เดี่ยว',
        'duo': 'คู่',
        'group': 'กลุ่ม',
        'submit': 'ส่ง',
        'save': 'บันทึก',
        'cancel': 'ยกเลิก',
        'edit': 'แก้ไข',
        'delete': 'ลบ',
        'confirm_delete': 'ยืนยันการลบ?',
        'no_schedules': 'ยังไม่มีกำหนดการ',
        'username': 'ชื่อผู้ใช้',
        'email': 'อีเมล',
        'password': 'รหัสผ่าน',
        'confirm_password': 'ยืนยันรหัสผ่าน',
        'welcome': 'StarTrack',
        'subtitle': 'แพลตฟอร์มติดตามกำหนดการดารา',
        'search': 'ค้นหา',
        'filter': 'กรอง',
        'all': 'ทั้งหมด',
        'optional': 'ไม่บังคับ',
        'upload_image': 'อัปโหลดรูป',
        'drag_drop': 'ลากและวางหรือคลิกเพื่ออัปโหลด',
        'max_size': 'สูงสุด 16MB',
        'login_required': 'กรุณาเข้าสู่ระบบ',
        'unauthorized': 'ไม่มีสิทธิ์',
        'success_add': 'เพิ่มกำหนดการสำเร็จ',
        'success_edit': 'อัปเดตกำหนดการแล้ว',
        'success_delete': 'ลบกำหนดการแล้ว',
        'error_occurred': 'เกิดข้อผิดพลาด',
        'password_mismatch': 'รหัสผ่านไม่ตรงกัน',
        'username_exists': 'ชื่อผู้ใช้นี้มีอยู่แล้ว',
        'email_exists': 'อีเมลนี้ลงทะเบียนแล้ว',
        'invalid_credentials': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง',
        'invalid_username': 'ชื่อผู้ใช้ไม่ถูกต้อง (3-32 ตัวอักษร ตัวเลข ขีดล่าง หรือภาษาจีน)',
        'invalid_email': 'รูปแบบอีเมลไม่ถูกต้อง',
        'password_too_short': 'รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร',
        'invalid_group_type': 'ประเภทกิจกรรมไม่ถูกต้อง',
        'invalid_date': 'รูปแบบวันที่ไม่ถูกต้อง',
        'invalid_image': 'อัปโหลดรูปภาพล้มเหลว กรุณาตรวจสอบรูปแบบไฟล์',
        'required_fields_missing': 'กรุณากรอกข้อมูลที่จำเป็น',
        'page': 'หน้า',
        'prev': 'ก่อนหน้า',
        'next': 'ถัดไป',
        'footer_text': '© 2026 StarTrack. All rights reserved.',
        'filter_all': 'ทั้งหมด',
        'filter_solo': 'เดี่ยว',
        'filter_duo': 'คู่',
        'filter_group': 'กลุ่ม',
        'refresh': 'รีเฟรช',
        'multi_image': 'รองรับหลายภาพ',
        'year': 'ปี',
        'month': 'เดือน',
        'day': 'วัน',
        'all_dates': 'ทุกวัน',
    }
}


def get_lang():
    """获取当前语言"""
    return session.get('lang', 'en')


def t(key):
    """翻译快捷方式"""
    lang = get_lang()
    return TRANSLATIONS.get(lang, TRANSLATIONS['zh']).get(key, key)


@app.before_request
def before_request():
    g.lang = get_lang()
    g.t = t


# ─────────────────────────────────────────────
# 用户加载
# ─────────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ─────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file):
    """保存并压缩图片，返回文件名；包含内容验证"""
    if not (file and file.filename and allowed_file(file.filename)):
        return None

    try:
        ext = file.filename.rsplit('.', 1)[1].lower()
        # 只允许 Web 安全格式
        if ext == 'jpg':
            ext = 'jpeg'

        img = Image.open(file)

        # 验证是否为真实图片
        img.verify()
        file.seek(0)
        img = Image.open(file)

        # 限制最大尺寸
        if max(img.size) > MAX_IMAGE_DIMENSION:
            img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)

        # 统一转换为 RGB 并压缩
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(filepath, quality=85, optimize=True)
        return filename
    except Exception:
        return None


def delete_image(filename):
    """删除图片文件"""
    if filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)


def save_localized_field(schedule, field, value):
    """根据当前语言保存字段：同时写入基础字段和对应语言字段"""
    value = value.strip() if value else ''
    setattr(schedule, field, value)
    lang = get_lang()
    if lang in ('en', 'th'):
        setattr(schedule, f'{field}_{lang}', value)


def create_default_admin():
    """默认创建管理员账号，密码可通过环境变量 ADMIN_PASSWORD 设置"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin = User(username='admin', email='admin@startrack.com', is_admin=True)
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print('Default admin created: admin / (see env ADMIN_PASSWORD or default admin123)')


# ─────────────────────────────────────────────
# 路由：语言切换
# ─────────────────────────────────────────────
@app.route('/lang/<lang_code>')
def switch_language(lang_code):
    if lang_code in ('zh', 'en', 'th'):
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('index'))


# ─────────────────────────────────────────────
# 路由：首页
# ─────────────────────────────────────────────
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    group_type = request.args.get('group_type', '')
    year = request.args.get('year', '', type=int)
    month = request.args.get('month', '', type=int)
    day = request.args.get('day', '', type=int)
    search = request.args.get('search', '')

    # 年份下拉框范围：当前年份前后共 10 年
    current_year = datetime.now().year
    year_range = range(current_year - 1, current_year + 9)

    query = Schedule.query

    if group_type:
        query = query.filter_by(group_type=group_type)
    if year:
        query = query.filter(db.extract('year', Schedule.event_date) == year)
    if month:
        query = query.filter(db.extract('month', Schedule.event_date) == month)
    if day:
        query = query.filter(db.extract('day', Schedule.event_date) == day)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            db.or_(
                Schedule.star_name.ilike(search_filter),
                Schedule.star_name_en.ilike(search_filter),
                Schedule.star_name_th.ilike(search_filter),
                Schedule.event_name.ilike(search_filter),
                Schedule.event_name_en.ilike(search_filter),
                Schedule.event_name_th.ilike(search_filter),
                Schedule.event_location.ilike(search_filter),
            )
        )

    # 按活动日期升序排列，无日期的放最后
    pagination = query.order_by(
        Schedule.event_date.is_(None).asc(),
        Schedule.event_date.asc(),
        Schedule.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('index.html',
                         schedules=pagination.items,
                         pagination=pagination,
                         group_type=group_type,
                         year_range=year_range,
                         year=year,
                         month=month,
                         day=day,
                         search=search)


# ─────────────────────────────────────────────
# 路由：注册
# ─────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not validate_username(username):
            flash(t('invalid_username'), 'error')
            return render_template('register.html')

        if not validate_email(email):
            flash(t('invalid_email'), 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash(t('password_too_short'), 'error')
            return render_template('register.html')

        if password != confirm:
            flash(t('password_mismatch'), 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash(t('username_exists'), 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash(t('email_exists'), 'error')
            return render_template('register.html')

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(t('success_add'), 'success')
        return redirect(url_for('index'))

    return render_template('register.html')


# ─────────────────────────────────────────────
# 路由：登录
# ─────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))

        flash(t('invalid_credentials'), 'error')

    return render_template('login.html')


# ─────────────────────────────────────────────
# 路由：退出
# ─────────────────────────────────────────────
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ─────────────────────────────────────────────
# 路由：添加行程
# ─────────────────────────────────────────────
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_schedule():
    if request.method == 'POST':
        star_name = sanitize_text(request.form.get('star_name', ''), 200)
        event_name = sanitize_text(request.form.get('event_name', ''), 500)
        event_date_str = request.form.get('event_date', '')
        group_type = request.form.get('group_type', 'solo')
        event_location = request.form.get('event_location', '')
        description = request.form.get('description', '')

        if not star_name or not event_name:
            flash(t('required_fields_missing'), 'error')
            return render_template('add_schedule.html')

        if not validate_group_type(group_type):
            flash(t('invalid_group_type'), 'error')
            return render_template('add_schedule.html')

        event_date = None
        if event_date_str:
            try:
                event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash(t('invalid_date'), 'error')
                return render_template('add_schedule.html')

        # 创建行程
        schedule = Schedule(
            event_date=event_date,
            group_type=group_type,
            creator_id=current_user.id,
        )
        save_localized_field(schedule, 'star_name', star_name)
        save_localized_field(schedule, 'event_name', event_name)
        save_localized_field(schedule, 'event_location', event_location)
        schedule.description = description

        # 处理多张图片
        image_files = request.files.getlist('event_images')
        saved_images = []
        for idx, f in enumerate(image_files):
            if f and f.filename:
                filename = save_image(f)
                if filename:
                    saved_images.append((filename, idx))
                elif any(f.filename for f in image_files if f.filename):
                    flash(t('invalid_image'), 'error')
                    return render_template('add_schedule.html')

        db.session.add(schedule)
        db.session.flush()  # 获取 schedule.id

        for filename, order in saved_images:
            img = ScheduleImage(filename=filename, sort_order=order, schedule_id=schedule.id)
            db.session.add(img)

        # 向后兼容：设第一张为封面
        if saved_images:
            schedule.event_image = saved_images[0][0]
        else:
            schedule.event_image = None

        db.session.commit()

        flash(t('success_add'), 'success')
        return redirect(url_for('index'))

    return render_template('add_schedule.html')


# ─────────────────────────────────────────────
# 路由：编辑行程
# ─────────────────────────────────────────────
@app.route('/edit/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
def edit_schedule(schedule_id):
    schedule = db.session.get(Schedule, schedule_id)
    if not schedule:
        abort(404)
    if not current_user.is_admin and schedule.creator_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        star_name = sanitize_text(request.form.get('star_name', ''), 200)
        event_name = sanitize_text(request.form.get('event_name', ''), 500)
        event_date_str = request.form.get('event_date', '')
        group_type = request.form.get('group_type', 'solo')
        event_location = request.form.get('event_location', '')
        description = request.form.get('description', '')

        if not star_name or not event_name:
            flash(t('required_fields_missing'), 'error')
            return render_template('edit_schedule.html', schedule=schedule)

        if not validate_group_type(group_type):
            flash(t('invalid_group_type'), 'error')
            return render_template('edit_schedule.html', schedule=schedule)

        save_localized_field(schedule, 'star_name', star_name)
        save_localized_field(schedule, 'event_name', event_name)
        save_localized_field(schedule, 'event_location', event_location)
        schedule.group_type = group_type
        schedule.description = description

        if event_date_str:
            try:
                schedule.event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash(t('invalid_date'), 'error')
                return render_template('edit_schedule.html', schedule=schedule)
        else:
            schedule.event_date = None

        # 处理多张图片
        image_files = request.files.getlist('event_images')
        has_new_images = any(f and f.filename for f in image_files)
        if has_new_images:
            # 删除旧图片
            for img in schedule.images.all():
                delete_image(img.filename)
                db.session.delete(img)
            # 保存新图片
            for idx, f in enumerate(image_files):
                if f and f.filename:
                    filename = save_image(f)
                    if filename:
                        db.session.add(ScheduleImage(filename=filename, sort_order=idx, schedule_id=schedule.id))
                    else:
                        flash(t('invalid_image'), 'error')
                        return render_template('edit_schedule.html', schedule=schedule)
            # 更新封面
            first = schedule.images.order_by(ScheduleImage.sort_order).first()
            schedule.event_image = first.filename if first else None

        db.session.commit()
        flash(t('success_edit'), 'success')
        return redirect(url_for('index'))

    return render_template('edit_schedule.html', schedule=schedule)


# ─────────────────────────────────────────────
# 路由：删除行程
# ─────────────────────────────────────────────
@app.route('/delete/<int:schedule_id>', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    schedule = db.session.get(Schedule, schedule_id)
    if not schedule:
        abort(404)
    if not current_user.is_admin and schedule.creator_id != current_user.id:
        abort(403)

    for img in schedule.images.all():
        delete_image(img.filename)
    delete_image(schedule.event_image)
    db.session.delete(schedule)
    db.session.commit()

    flash(t('success_delete'), 'success')
    return redirect(url_for('index'))


# ─────────────────────────────────────────────
# 路由：我的行程
# ─────────────────────────────────────────────
@app.route('/my')
@login_required
def my_schedules():
    page = request.args.get('page', 1, type=int)
    pagination = Schedule.query.filter_by(creator_id=current_user.id)\
        .order_by(Schedule.created_at.desc())\
        .paginate(page=page, per_page=12, error_out=False)

    return render_template('index.html',
                         schedules=pagination.items,
                         pagination=pagination,
                         is_mine=True)


# ─────────────────────────────────────────────
# 路由：日历视图
# ─────────────────────────────────────────────
@app.route('/calendar')
@login_required
def calendar_view():
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    # 限定有效年月
    year = max(1900, min(2100, year))
    month = max(1, min(12, month))

    # 当月第一天和最后一天
    first_day = date(year, month, 1)
    _, last_day_of_month = calendar.monthrange(year, month)
    last_day = date(year, month, last_day_of_month)

    # 查询当月所有行程
    schedules = Schedule.query.filter(
        Schedule.event_date >= first_day,
        Schedule.event_date <= last_day
    ).order_by(Schedule.event_date.asc(), Schedule.created_at.asc()).all()

    # 按日期分组
    schedules_by_date = {}
    for s in schedules:
        d = s.event_date
        if d not in schedules_by_date:
            schedules_by_date[d] = []
        schedules_by_date[d].append(s)

    # 构建日历网格：从周日开始
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    # 上个月/下个月
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    return render_template('calendar.html',
                         year=year,
                         month=month,
                         month_days=month_days,
                         schedules_by_date=schedules_by_date,
                         prev_year=prev_year,
                         prev_month=prev_month,
                         next_year=next_year,
                         next_month=next_month,
                         date=date)


# ─────────────────────────────────────────────
# 路由：行程详情页
# ─────────────────────────────────────────────
@app.route('/schedule/<int:schedule_id>')
def schedule_detail(schedule_id):
    schedule = db.session.get(Schedule, schedule_id)
    if not schedule:
        abort(404)
    return render_template('schedule_detail.html', schedule=schedule)


# ─────────────────────────────────────────────
# API: 获取行程详情
# ─────────────────────────────────────────────
@app.route('/api/schedule/<int:schedule_id>')
def api_schedule(schedule_id):
    schedule = db.session.get(Schedule, schedule_id)
    if not schedule:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(schedule.to_dict(get_lang()))


# ─────────────────────────────────────────────
# API: 统计数据
# ─────────────────────────────────────────────
@app.route('/api/schedule/stats')
def api_stats():
    total = Schedule.query.count()
    solo = Schedule.query.filter_by(group_type='solo').count()
    duo = Schedule.query.filter_by(group_type='duo').count()
    group = Schedule.query.filter_by(group_type='group').count()

    return jsonify({
        'total': total,
        'solo': solo,
        'duo': duo,
        'group': group
    })


# ─────────────────────────────────────────────
# 错误处理
# ─────────────────────────────────────────────
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message=t('unauthorized')), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Not Found'), 404


@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413


# ─────────────────────────────────────────────
# 启动
# ─────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
