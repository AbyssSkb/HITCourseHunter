import requests
import json
import time
from dotenv import load_dotenv
import os

try:
    with open("courses.json", "r") as f:
        courses = json.load(f)
except FileNotFoundError:
    print("找不到文件：courses.json。请先运行prepare.py。")
    exit(1)

load_dotenv()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Cookie": os.getenv("COOKIE"),
}

for course in courses:
    name = course["name"]
    teacher = course["teacher"]
    print(f"正在课程选择：{name}（{teacher}）")
    url = "http://jw.hitsz.edu.cn/Xsxk/addGouwuche"
    data = {
        "p_xktjz": "rwtjzyx",
        "p_xn": course["academic_year"],
        "p_xq": course["term"],
        "p_xkfsdm": course["code"],
        "p_id": course["id"],
    }
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        if "application/json" in response.headers["Content-Type"]:
            response_json = response.json()
            print("响应内容：", response_json["message"])
        elif "text/html" in response.headers["Content-Type"]:
            print("Cookie过期，请重新登录")
        else:
            print("响应内容不是有效的JSON格式")
    else:
        print(f"请求失败，状态码：{response.status_code}")

    print("等待3秒后继续...")
    print()
    time.sleep(3)
