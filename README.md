# 🌟 StarTrack

**Thai celebrity schedule tracker** — track, share, and discover celebrity events.  
**泰国明星行程追踪平台** — 追踪、分享、发现明星活动行程。

[![Deploy](https://img.shields.io/badge/Live-thai--star--schedule.onrender.com-blue)](https://thai-star-schedule.onrender.com)

---

## 中文

### 项目简介

StarTrack 是一个面向泰国明星粉丝的行程追踪网站。用户可以浏览、搜索明星活动，按月历查看行程，注册后即可添加/编辑/删除行程，支持多图上传和自定义标签。

### 功能特性

| 功能 | 说明 |
|------|------|
| 📅 行程管理 | 添加、编辑、删除行程（艺人名、活动名、日期时间、地点、描述） |
| 🖼️ 多图上传 | 支持拖拽/多选上传，Pillow 自动压缩至 1200px，上限 16MB |
| 🏷️ 自定义标签 | 每个行程可添加多个键值对标签（如票价、购票链接） |
| 📆 日历视图 | 月历网格展示，按艺人筛选，鼠标悬停预览行程详情 |
| 🔍 搜索筛选 | 按艺人/活动名搜索，按类型（单人/双人/多人）筛选，按年月日筛选 |
| 🌐 三语切换 | English · 中文 · ภาษาไทย（默认英文） |
| 🌓 双主题 | 深色蓝黑主题 / 浅色白黄主题，彩虹渐变强调色 |
| ✨ 星空粒子 | Canvas 满屏闪烁星星背景 |
| 👤 用户系统 | 注册/登录/退出，PBKDF2 密码哈希，管理员可管理全部行程 |
| 🔒 安全防护 | CSRF、CSP、限流、文件内容校验、输入验证 |
| 📱 响应式 | 5 级断点（1200/1024/768/480/360px），适配手机到桌面 |

### 快速开始

**环境要求**：Python 3.10+

```bash
cd thai-star-schedule
pip install -r requirements.txt
python app.py
```

打开 http://localhost:5000

### 部署

本项目已部署于 [Render](https://thai-star-schedule.onrender.com)，每次 `git push` 自动部署。

启动命令：`gunicorn wsgi:app`

### 项目结构

```
thai-star-schedule/
├── app.py                 # Flask 主应用（路由/安全/多语言）
├── models.py              # 数据模型（User/Schedule/ScheduleImage/ScheduleTag）
├── requirements.txt       # 依赖
├── wsgi.py                # 生产环境入口
├── seed.py                # 示例数据
├── run.bat                # Windows 一键启动
├── .github/workflows/     # GitHub Actions
├── static/
│   ├── css/style.css      # 设计系统
│   ├── js/main.js         # 粒子/主题/导航/语言
│   └── uploads/           # 上传图片
└── templates/
    ├── base.html          # 基础模板
    ├── index.html         # 首页
    ├── calendar.html      # 日历页
    ├── schedule_detail.html # 详情页
    ├── add_schedule.html  # 添加行程
    ├── edit_schedule.html # 编辑行程
    ├── login.html         # 登录
    ├── register.html      # 注册
    └── error.html         # 错误页
```

---

## English

### Overview

StarTrack is a celebrity schedule tracking platform for Thai entertainment fans. Browse events, search by artist, view a monthly calendar, and — after signing up — add, edit, or delete schedules with multi-image uploads and custom tags.

### Features

| Feature | Description |
|---------|-------------|
| 📅 Schedule CRUD | Create, edit, delete events (artist, event name, date/time, location, description) |
| 🖼️ Multi-image | Drag & drop multiple images, auto-compressed via Pillow (1200px max, 16MB limit) |
| 🏷️ Custom tags | Key-value label pairs per schedule (e.g. ticket price, link) |
| 📆 Calendar | Monthly grid with hover preview tooltip and artist filter dropdown |
| 🔍 Search & filter | Search by artist/event name, filter by type (Solo/Duo/Group), filter by date |
| 🌐 i18n | English · 中文 · ภาษาไทย (English default), session-based switching |
| 🌓 Dual theme | Dark (blue/black) and Light (white/gold) with rainbow gradient accents |
| ✨ Starfield | Canvas-based twinkling star background |
| 👤 Auth | Register, login, logout with PBKDF2 password hashing; admin manages all content |
| 🔒 Security | CSRF, CSP headers, rate limiting, image content verification, input validation |
| 📱 Responsive | 5 breakpoints (1200/1024/768/480/360px) |

### Quick Start

**Requirements**: Python 3.10+

```bash
cd thai-star-schedule
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5000

### Default Account

| Username | Password | Notes |
|----------|----------|-------|
| admin | admin123 | Admin (customizable via `ADMIN_PASSWORD` env var) |

### Deployment

Deployed on [Render](https://thai-star-schedule.onrender.com) with auto-deploy on `git push`.

Start command: `gunicorn wsgi:app`

### Tech Stack

- **Backend**: Flask 3.x, Flask-Login, Flask-WTF, Flask-SQLAlchemy, Flask-Limiter
- **Database**: SQLite (production-ready with PostgreSQL support via `DATABASE_URL`)
- **Image**: Pillow with LANCZOS resampling
- **Frontend**: Vanilla JS, CSS custom properties, Font Awesome 6, Google Fonts (Inter)
- **Deploy**: Render + Gunicorn

### API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/schedule/<id>` | GET | Schedule detail (JSON) |
| `/api/schedule/stats` | GET | Count by type |

### License

MIT
