# 🎯 HITSZ 抢课助手

[![Build and Release](https://github.com/AbyssSkb/HITCourseHunter/actions/workflows/release.yml/badge.svg)](https://github.com/AbyssSkb/HITCourseHunter/actions/workflows/release.yml)

## ⚠️ 注意事项
- 自用
- 具有时效性，不保证能用
- 可能没有手抢的快（

## 📚 使用说明
> 请确保你已安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)
1. 克隆仓库
   ```bash
   git clone https://github.com/AbyssSkb/HITCourseHunter.git
   ```

2. 修改配置文件

   重命名 `.env.example` 为 `.env`，修改以下配置信息：
   ```ini
   USERNAME="你的统一身份认证用户名"
   PASSWORD="你的统一身份认证密码"
   PATH="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"  # 你的 Edge/Chrome 浏览器可执行文件路径
   HEADLESS="True"  # 是否启用无头模式，True 表示不显示浏览器窗口，False 表示显示浏览器窗口
   START_TIME="13:00:00"  # 可选，计划开始时间，格式为 HH:MM:SS
   ```

3. 运行程序
   ```bash
   # 先运行 prepare.py 选择课程
   uv run prepare.py
   
   # 再运行 hunter.py 开始抢课
   uv run hunter.py
   ```

### 🔍 如何获取浏览器可执行文件路径
见[获取浏览器路径的方法](https://drissionpage.cn/get_start/before_start/#2%EF%B8%8F%E2%83%A3-%E8%AE%BE%E7%BD%AE%E8%B7%AF%E5%BE%84)

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