import time
import colorama
from colorama import Fore
from tools import (
    add_course,
    wait_until_start,
    load_courses,
    load_config,
    get_headers,
    save_results,
)

colorama.init()  # 初始化 colorama


def run_course_hunter(
    courses: list[dict[str, str]], headers: dict[str, str]
) -> list[dict[str, str]]:
    """执行选课流程

    Args:
        courses (list[dict[str, str]]): 要选择的课程列表
        headers (dict[str, str]): HTTP 请求头

    Returns:
        list[dict[str, str]]: 选课失败的课程列表
    """
    unsuccessful_courses = []
    for course in courses:
        status = add_course(course, headers)
        if not status:
            unsuccessful_courses.append(course)
        for i in range(2, 0, -1):
            print(f"\r{Fore.CYAN}等待 {i} 秒后继续...{Fore.RESET}", end="")
            time.sleep(1)
        print("\r" + " " * 50 + "\r", end="")  # 清除倒计时行
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
        if config and headers:
            save_results(config, headers, unsuccessful_courses)


if __name__ == "__main__":
    main()
