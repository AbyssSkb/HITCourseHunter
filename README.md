# 🎯 HITSZ 抢课助手

[![Build and Release](https://github.com/AbyssSkb/HITCourseHunter/actions/workflows/release.yml/badge.svg)](https://github.com/AbyssSkb/HITCourseHunter/actions/workflows/release.yml)

## ⚠️ 注意事项
- 自用
- 具有时效性，不保证能用
- 可能没有手抢的快（

## 📚 使用说明

### 🚀 方法一：使用可执行文件

1. 下载程序
   - 前往 [Release页面](https://github.com/AbyssSkb/HITCourseHunter/releases)
   - 下载最新版本的 `hitcoursehunter.zip`
   - 解压到任意目录 (可能需要加入防火墙白名单)

2. 配置环境（见下方配置说明）

3. 运行程序
   - 先运行 `prepare.exe`，按提示选择课程
   - 再运行 `hunter.exe` 开始抢课

### 💻 方法二：使用Python运行

1. 克隆仓库
   ```bash
   git clone https://github.com/AbyssSkb/HITCourseHunter.git
   ```

2. 配置环境
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   
   # 配置.env文件（见下方配置说明）
   ```

3. 运行程序
   ```bash
   # 先运行prepare.py选择课程
   python prepare.py
   
   # 再运行hunter.py开始抢课
   python hunter.py
   ```

### ⚙️ 配置说明
重命名 `.env.example` 为 `.env`，修改以下配置：
> 注意密码填的是从深圳校区页面登录的密码
```ini
USERNAME="你的统一身份认证用户名"
PASSWORD="你的统一身份认证密码"
START_TIME="13:00:00"  # 可选，计划开始时间，格式为 HH:MM:SS
```

## 🛠️ 实现原理
- `prepare.exe`
  - 获取学期信息和课程类别
  - 通过关键词搜索课程
  - 将用户选择的课程保存到 `courses.json`
- `hunter.exe`
  - 读取 `courses.json` 中的课程信息
  - 在指定时间（若配置了START_TIME）开始自动抢课
  - 如果某门课抢课失败，会保留在 `courses.json` 中供下次继续尝试
  - 每次抢课间隔3秒以避免请求过于频繁
- 接口说明:
  - 获取学期信息: `/Xsxk/queryXkdqXnxq`
  - 获取课程类别: `/Xsxk/queryYxkc`
  - 查询可选课程: `/Xsxk/queryKxrw`
  - 选课: `/Xsxk/addGouwuche`