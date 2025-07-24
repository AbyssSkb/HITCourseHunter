import time

import colorama
import typer
from colorama import Fore
from typing_extensions import Annotated

from tools import (
    MaxRetriesExceededError,
    add_course,
    get_headers,
    load_config,
    load_courses,
    save_results,
    wait_until_start,
)

colorama.init()  # 初始化 colorama
MAX_UNSUCCESSFUL_COURSE_RETRIES = 2


def run_course_hunter(
    courses: list[dict[str, str]], headers: dict[str, str], wait_time: int
) -> list[dict[str, str]]:
    """执行选课流程

    Args:
        courses (list[dict[str, str]]): 要选择的课程列表
        headers (dict[str, str]): HTTP 请求头
        wait_time (int): 每次尝试选课之间的等待时间（秒）

    Returns:
        list[dict[str, str]]: 选课失败的课程列表
    """
    unsuccessful_courses: list[dict[str, str]] = []
    for course in courses:
        status = add_course(course, headers)
        if not status:
            unsuccessful_courses.append(course)
        for i in range(wait_time, 0, -1):
            print(f"\r{Fore.CYAN}等待 {i} 秒后继续...{Fore.RESET}", end="")
            time.sleep(1)
        print("\r" + " " * 50 + "\r", end="")  # 清除倒计时行
    return unsuccessful_courses


def main(
    is_immediate_start: Annotated[
        bool, typer.Option("--now", "-n", help="跳过等待开始时间，立即开始抢课")
    ] = False,
    wait_time: Annotated[
        int,
        typer.Option(
            help="课程抢课间隔时间（秒），优先级高于配置文件", show_default=False
        ),
    ] = -1,
) -> None:
    """选课抢课工具：自动帮助您在选课系统中抢课

    根据配置文件设置运行课程抢课流程。程序将加载您的课程列表，
    并在指定时间（如有设置）开始尝试选课。对于选课失败的课程，
    将自动重试直到达到最大重试次数。
    """
    config = None
    headers = None
    unsuccessful_courses = []
    courses = None
    retry_count = 0

    try:
        courses = load_courses()
        config = load_config()
        headers = get_headers(config["COOKIES"])
        if wait_time == -1:
            wait_time = int(config.get("WAIT_TIME", 3))

        start_time = config.get("START_TIME")
        if start_time and not is_immediate_start:
            print(Fore.CYAN + f"计划开始时间: {start_time}" + Fore.RESET)
            wait_until_start(start_time)
        else:
            print(Fore.GREEN + "直接开始抢课" + Fore.RESET)

        while retry_count <= MAX_UNSUCCESSFUL_COURSE_RETRIES:
            unsuccessful_courses = run_course_hunter(courses, headers, wait_time)

            if not unsuccessful_courses:
                return

            courses = unsuccessful_courses
            retry_count += 1

    except (FileNotFoundError, ValueError) as e:
        print(Fore.RED + f"错误: {str(e)}" + Fore.RESET)
        return
    except MaxRetriesExceededError:
        print(Fore.RED + "重复获取 Cookie 次数超过最大限制" + Fore.RESET)
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n正在退出..." + Fore.RESET)
        if courses:
            unsuccessful_courses = courses
    finally:
        if config and headers:
            save_results(config, headers, unsuccessful_courses)


if __name__ == "__main__":
    typer.run(main)
