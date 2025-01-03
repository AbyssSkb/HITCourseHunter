"""HITSZ课程选择准备程序"""

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
