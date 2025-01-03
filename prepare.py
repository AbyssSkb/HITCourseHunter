"""HITSZ课程选课准备程序

用于在正式选课前准备要选的课程列表。
支持按类别浏览和关键词搜索课程，选中的课程会保存到courses.json文件中。
程序会自动处理登录认证，支持Cookie过期自动重新获取。

功能特点：
- 支持按课程类别浏览
- 支持关键词搜索课程
- 交互式选课界面
- 自动保存选课结果
- 可中断后继续选课

用法：
直接运行该程序，按提示进行操作即可。选择的课程将保存到courses.json文件中，
供hunter.py程序在选课时使用。
"""

from tools import (
    display_categories,
    get_headers,
    get_time_info,
    get_course_categories,
    get_coueses,
    handle_course_selection,
    load_config,
    load_existing_courses,
    save_results,
)
from colorama import init, Fore

init()  # 初始化colorama

def run_course_preparation(categories, time_info, headers, selected_courses):
    """执行课程准备流程"""
    while True:
        display_categories(categories)
        try:
            opt = int(input(Fore.GREEN + "选择一个类别 (0 退出) : " + Fore.RESET))
            if opt == 0:
                break

            selected_category = categories[opt - 1]
            while True:
                keyword = input(
                    Fore.GREEN + "输入你想查找的课程的关键词 (q 退出，直接回车查找全部) : " + Fore.RESET
                )
                if keyword == "q":
                    break

                courses = get_coueses(
                    category=selected_category,
                    time_info=time_info,
                    headers=headers,
                    keyword=keyword,
                )

                if handle_course_selection(courses, selected_courses):
                    break

        except (ValueError, IndexError):
            print(Fore.RED + "无效输入，请重试。" + Fore.RESET)
            continue


def main():
    """主函数：程序入口"""
    config = None
    headers = None
    selected_courses = []

    try:
        selected_courses = load_existing_courses()
        config = load_config()
        headers = get_headers(config["COOKIES"])

        time_info = get_time_info(headers)
        if time_info is None:
            print(Fore.RED + "获取时间信息失败。" + Fore.RESET)
            return

        categories = get_course_categories(time_info, headers)
        if not categories:
            print(Fore.RED + "获取课程类别失败。" + Fore.RESET)
            return

        run_course_preparation(categories, time_info, headers, selected_courses)

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n正在退出..." + Fore.RESET)
    finally:
        if config is not None and headers is not None:
            save_results(config, headers, selected_courses)


if __name__ == "__main__":
    main()
