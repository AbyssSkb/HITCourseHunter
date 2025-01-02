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
重命名 `.env.example` 为 `.env`，填入你的统一身份认证用户名和密码。
> 注意是从深圳校区页面登录的密码而不是从本部页面登录的密码
```ini
USERNAME="你的统一身份认证用户名"
PASSWORD="你的统一身份认证密码"
```

## 🛠️ 实现原理
- `prepare.exe`
  - 获取课程信息
  - 询问用户是否添加课程
  - 将最终结果保存到 `courses.json`
- `hunter.exe`
  - 读取 `courses.json` 中的课程信息
  - 按照3秒间隔持续发送选课请求
- 接口说明:
  - 获取学期信息: `/Xsxk/queryXkdqXnxq`
  - 获取课程类别: `/Xsxk/queryYxkc`
  - 查询可选课程: `/Xsxk/queryKxrw`
  - 选课: `/Xsxk/addGouwuche`