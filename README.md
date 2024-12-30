# 🎯 HITSZ 选课助手

## ⚠️ 注意事项
- 自用
- 具有时效性，不保证能用
- 极端情况下可能没有手抢的快（

## 📚 使用说明

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置环境变量
- 重命名 `.env.example` 为 `.env`
- 填入你的教务系统 Cookie（获取方式请自行 Google）

3. 使用步骤
```bash
# 1. 提前运行 prepare.py 选择要抢的课程
python prepare.py

# 2. 运行 hunter.py 开始抢课
python hunter.py
```

## ⚙️ 实现原理
- `prepare.py` 负责课程信息获取与存储
- `hunter.py` 负责模拟选课操作
- 使用教务系统的以下接口:
  - 获取学期信息: `/Xsxk/queryXkdqXnxq`
  - 获取课程类别: `/Xsxk/queryYxkc`
  - 查询可选课程: `/Xsxk/queryKxrw`
  - 加入购物车（选课）: `/Xsxk/addGouwuche`