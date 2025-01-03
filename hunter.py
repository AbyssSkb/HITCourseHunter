"""HITSZ课程自动选课程序

从courses.json中读取预选课程列表，在指定时间自动进行选课。
支持定时选课功能，如未在.env中设置START_TIME则立即开始选课。

功能特点：
- 支持定时开始选课
- 自动处理Cookie过期问题
- 选课失败自动重试
- 可随时中断，未选上的课程会重新保存
- 精确的定时功能，支持毫秒级等待

配置要求：
- courses.json：包含要选的课程信息
- .env：包含登录凭证和可选的开始时间

使用方法：
1. 先运行prepare.py准备课程列表
2. 在.env中可选设置START_TIME（格式：HH:MM:SS）
3. 运行本程序等待自动选课
"""

import time
from colorama import init, Fore
from tools import (
    add_course,
    wait_until_start,
    load_courses,
    load_config,
    get_headers,
    save_results,
)

init()  # 初始化colorama

def run_course_hunter(courses, headers):
    """执行选课流程

    按顺序尝试选择courses中的每门课程，
    每次选课之间有3秒的等待时间。

    Args:
        courses (list[dict]): 要选择的课程列表
        headers (dict): 包含Cookie的HTTP请求头

    Returns:
        list[dict]: 选课失败的课程列表
    """
    unsuccessful_courses = []
    for course in courses:
        status = add_course(course, headers)
        if not status:
            unsuccessful_courses.append(course)
        print(Fore.CYAN + "等待3秒后继续..." + Fore.RESET)
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
            print(Fore.CYAN + f"计划开始时间: {start_time}" + Fore.RESET)
            wait_until_start(start_time)
        else:
            print(Fore.GREEN + "未设置开始时间，直接开始抢课！" + Fore.RESET)

        unsuccessful_courses = run_course_hunter(courses, headers)

    except (FileNotFoundError, ValueError) as e:
        print(Fore.RED + f"错误: {str(e)}" + Fore.RESET)
        return
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n正在退出..." + Fore.RESET)
        if courses:
            unsuccessful_courses = courses
    finally:
        if config is not None and headers is not None:
            save_results(config, headers, unsuccessful_courses)


if __name__ == "__main__":
    main()
