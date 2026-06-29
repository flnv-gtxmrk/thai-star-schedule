# 🌟 Thai Star Schedule

泰国明星行程追踪平台 - 支持中/英/泰三语

## ✨ 功能特性

- 📅 行程管理：添加、编辑、删除行程
- 🖼️ 图片上传：支持拖拽上传，自动压缩
- 🔍 搜索筛选：按艺人名称、活动名称搜索
- 🏷️ 分类系统：单人/双人 × 男生/女生
- 🌐 多语言：中文、English、ภาษาไทย
- 👤 用户系统：注册、登录、权限管理
- 🔒 权限控制：只能编辑/删除自己的行程
- 📱 响应式：适配手机和桌面端

## 🚀 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装步骤

1. **克隆或下载项目**
   ```bash
   cd thai-star-schedule
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动应用**
   ```bash
   # Windows
   run.bat

   # 或者手动启动
   python app.py
   ```

4. **访问网站**
   打开浏览器访问: http://localhost:5000

## 📁 项目结构

```
thai-star-schedule/
├── app.py              # 主应用
├── models.py           # 数据库模型
├── requirements.txt    # 依赖包
├── wsgi.py             # WSGI入口（生产部署）
├── run.bat             # Windows启动脚本
├── static/
│   ├── css/
│   │   └── style.css   # 样式文件
│   ├── js/
│   │   └── main.js     # 前端逻辑
│   └── uploads/        # 上传的图片
└── templates/
    ├── base.html       # 基础模板
    ├── index.html      # 首页
    ├── login.html      # 登录页
    ├── register.html   # 注册页
    ├── add_schedule.html
    ├── edit_schedule.html
    └── error.html
```

## 🎨 设计风格

- **高饱和度色彩**：活力粉、电光紫、热力橙
- **美式风格**：简约、现代、视觉冲击力强
- **深色主题**：护眼、时尚
- **流畅动画**：悬停效果、过渡动画

## 🔧 配置说明

### 环境变量（可选）

创建 `.env` 文件：

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///thaistar.db
```

### 生产部署

使用 Gunicorn：

```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## 📝 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/schedule/<id>` | GET | 获取行程详情 |
| `/api/schedule/stats` | GET | 获取统计数据 |

## 🛡️ 安全特性

- CSRF 保护
- 密码哈希存储（PBKDF2）
- 登录限流（防暴力破解）
- 文件上传验证
- 权限控制

## 📄 许可证

MIT License
