# 🎯 HITSZ 自动化选课脚本

[![CI](https://github.com/AbyssSkb/HITCourseHunter/actions/workflows/ci.yml/badge.svg)](https://github.com/AbyssSkb/HITCourseHunter/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

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

   重命名 `.env.example` 为 `.env`，修改其中的配置信息

3. 运行程序

   ```bash
   # 先运行 prepare.py 选择课程
   uv run prepare.py
   
   # 再运行 hunter.py 开始抢课
   uv run hunter.py
   ```

### 🔍 如何获取浏览器可执行文件路径

见[获取浏览器路径的方法](https://drissionpage.cn/get_start/before_start/#2%EF%B8%8F%E2%83%A3-%E8%AE%BE%E7%BD%AE%E8%B7%AF%E5%BE%84)
