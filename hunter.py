"""HITSZ课程自动抢课程序"""

import time
from tools import (
    add_course,
    wait_until_start,
    load_courses,
    load_config,
    get_headers,
    save_results,
)


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
