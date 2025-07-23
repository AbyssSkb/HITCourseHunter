# 🎯 HITSZ 自动化选课脚本

[![CI](https://github.com/AbyssSkb/HITCourseHunter/actions/workflows/ci.yml/badge.svg)](https://github.com/AbyssSkb/HITCourseHunter/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## ✨ 新功能

- 🌐 **全新Web界面** - 用户友好的图形化课程选择界面
- 🔍 **智能搜索** - 快速搜索和筛选课程
- 📱 **响应式设计** - 支持移动设备和桌面端
- 🎨 **现代化UI** - 美观易用的Material Design风格界面
- ⚡ **实时交互** - 动态加载和即时反馈

## ⚠️ 注意事项

- 自用
- 具有时效性，不保证能用
- 可能没有手抢的快（

## 📚 使用说明

> [!NOTE]
> 请确保你已安装 [uv](https://docs.astral.sh/uv/getting-started/installation/) 或 Python 3.10+

### 🚀 快速开始

1. 克隆仓库

   ```bash
   git clone https://github.com/AbyssSkb/HITCourseHunter.git
   cd HITCourseHunter
   ```

2. 安装依赖

   ```bash
   # 使用 uv (推荐)
   uv sync
   
   # 或使用 pip
   pip install -r requirements.txt
   # 或直接安装依赖
   pip install colorama flask pycryptodome python-dotenv requests selectolax
   ```

3. 配置环境

   重命名 `.env.example` 为 `.env`，修改其中的配置信息

### 🌐 Web界面 (推荐)

1. 启动课程选择界面

   ```bash
   # 使用 uv
   uv run prepare.py
   
   # 或使用 python
   python3 prepare.py
   ```

2. 选择 "Web界面" 选项

3. 在浏览器中打开 `http://localhost:5000`

4. 在Web界面中：
   - 配置用户名和密码
   - 浏览和选择课程
   - 管理选课列表

5. 开始抢课

   ```bash
   # 使用 uv
   uv run hunter.py
   
   # 或使用 python
   python3 hunter.py
   ```

### 💻 命令行界面 (传统方式)

1. 运行课程选择

   ```bash
   # 使用 uv
   uv run prepare.py
   
   # 或使用 python
   python3 prepare.py
   ```

2. 选择 "命令行界面" 选项

3. 按提示选择课程

4. 开始抢课

   ```bash
   # 使用 uv
   uv run hunter.py
   
   # 或使用 python
   python3 hunter.py
   ```

## 🎨 界面预览

### 主页
干净简洁的主页，提供快速导航和功能介绍。

### 课程选择
![Course Selection](https://github.com/user-attachments/assets/34a585ba-d86c-4f7e-8eb5-120ba10c2335)

智能化的课程浏览和选择界面，支持分类筛选和关键词搜索。

### 系统设置
![Configuration](https://github.com/user-attachments/assets/2a28e7c7-173c-4b33-bd6c-16e25f415c6c)

直观的配置页面，轻松设置登录信息和抢课参数。

### 已选课程
![Selected Courses](https://github.com/user-attachments/assets/970f6c09-9f6c-4523-86bb-eabc601cf67b)

清晰的课程管理界面，方便查看和管理已选课程。

## ⚙️ 功能特性

### Web界面特性
- 🎯 **可视化课程选择** - 图形化界面浏览课程信息
- 🔍 **智能搜索过滤** - 按关键词快速查找课程
- 📊 **实时统计信息** - 显示已选课程数量和状态
- 💾 **自动保存进度** - 实时保存选择结果
- 📱 **移动端适配** - 响应式设计支持手机操作
- 🎨 **现代化界面** - Material Design风格，美观易用

### 核心功能
- ⏰ **定时抢课** - 设置开始时间自动等待
- 🔄 **失败重试** - 自动重试失败的选课请求
- 🍪 **Session管理** - 智能Cookie管理和刷新
- 🔐 **安全认证** - 支持统一身份认证登录
- 📋 **批量处理** - 支持多门课程批量选择

## 🛠️ 技术栈

- **后端**: Python 3.10+, Flask
- **前端**: HTML5, CSS3, JavaScript, Bootstrap 5
- **UI框架**: Material Design, Font Awesome
- **网络请求**: Requests, 加密算法支持
- **数据解析**: Selectolax (快速HTML解析)

## 📁 项目结构

```
HITCourseHunter/
├── app.py              # Flask Web应用
├── prepare.py          # 课程选择入口(支持Web和CLI)
├── hunter.py           # 自动抢课脚本
├── tools.py            # 核心工具函数
├── templates/          # HTML模板
│   ├── base.html      # 基础模板
│   ├── index.html     # 主页
│   ├── course_selection.html  # 课程选择页
│   ├── selected_courses.html  # 已选课程页
│   ├── config.html    # 配置页面
│   └── error.html     # 错误页面
├── static/            # 静态资源
│   ├── css/
│   │   └── style.css  # 自定义样式
│   └── js/
│       └── main.js    # 前端交互逻辑
├── .env.example       # 配置文件模板
└── courses.json       # 选择的课程数据
```
