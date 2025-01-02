"""HIT课程自动抢课程序"""

import json
import time
from datetime import datetime
from dotenv import dotenv_values
from tools import get_cookies, add_course


def load_courses():
    """从courses.json加载待抢课程列表"""
    try:
        with open("courses.json", "r") as f:
            courses = json.load(f)

        if len(courses) == 0:
            raise ValueError("没有要抢的课程")
        return courses
    except FileNotFoundError:
        raise FileNotFoundError("找不到文件courses.json。请先运行prepare.py。")


def load_config():
    """从.env加载配置并验证"""
    config = dotenv_values(".env")
    cookies = config.get("COOKIES")
    start_time = config.get("START_TIME")

    if start_time and not validate_time_format(start_time):
        raise ValueError("时间格式不正确，请检查START_TIME的值（格式：HH:MM:SS）")

    if cookies is None or cookies == "":
        cookies = get_cookies()
        config["COOKIES"] = cookies

    return config


def get_headers(cookies):
    """生成HTTP请求头"""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Cookie": cookies,
    }


def save_results(config, headers, unsuccessful_courses):
    """保存更新后的cookie和未成功的课程"""
    config["COOKIES"] = headers["Cookie"]
    with open(".env", mode="w") as f:
        for key, value in config.items():
            f.write(f'{key}="{value}"\n')

    with open("courses.json", "w") as f:
        json.dump(unsuccessful_courses, f, ensure_ascii=False, indent=4)


def validate_time_format(time_str):
    """验证HH:MM:SS格式时间字符串"""
    try:
        time.strptime(time_str, "%H:%M:%S")
        return True
    except ValueError:
        return False


def wait_until_start(start_time):
    """倒计时等待至指定时间"""
    now = datetime.now()
    time_parts = start_time.strip().split(":")
    target_time = now.replace(
        hour=int(time_parts[0]),
        minute=int(time_parts[1]),
        second=int(time_parts[2]),
        microsecond=0,
    )

    time_delta = (target_time - now).total_seconds()

    if time_delta < 0:
        print("目标时间已过，直接开始抢课！")
        return

    while True:
        remaining = (target_time - datetime.now()).total_seconds()
        if remaining <= 0:
            break
        print(f"\r距离开始还有 {int(remaining)} 秒...", end="", flush=True)
        time.sleep(0.1)

    print("\n开始抢课！")


def run_course_hunter(courses, headers):
    """执行抢课流程"""
    unsuccessful_courses = []
    for course in courses:
        status = add_course(course, headers)
        if not status:
            unsuccessful_courses.append(course)
        print("等待3秒后继续...")
        print()
        time.sleep(3)
    return unsuccessful_courses


def main():
    """主函数：程序入口"""
    config = None
    headers = None
    unsuccessful_courses = []
    courses = None

    try:
        courses = load_courses()
        config = load_config()
        headers = get_headers(config["COOKIES"])

        start_time = config.get("START_TIME")
        if start_time:
            print(f"计划开始时间: {start_time}")
            wait_until_start(start_time)
        else:
            print("未设置开始时间，直接开始抢课！")

        unsuccessful_courses = run_course_hunter(courses, headers)

    except (FileNotFoundError, ValueError) as e:
        print(f"错误: {str(e)}")
        return
    except KeyboardInterrupt:
        print("\n正在退出...")
        if courses:
            unsuccessful_courses = courses
    finally:
        if config is not None and headers is not None:
            save_results(config, headers, unsuccessful_courses)


if __name__ == "__main__":
    main()
