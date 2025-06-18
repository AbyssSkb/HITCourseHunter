from tools import (
    MaxRetriesExceededError,
    display_categories,
    get_headers,
    get_time_info,
    get_course_categories,
    get_courses,
    handle_course_selection,
    load_config,
    load_existing_courses,
    save_results,
)
import colorama
from colorama import Fore

colorama.init()  # 初始化 colorama


def run_course_preparation(
    categories: list[dict[str, str]],
    time_info: dict[str, str],
    headers: dict[str, str],
    selected_courses: list[dict[str, str]],
) -> None:
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
                    Fore.GREEN
                    + "输入你想查找的课程的关键词 (q 退出，直接回车查找全部) : "
                    + Fore.RESET
                )
                if keyword == "q":
                    break

                courses = get_courses(
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


def main() -> None:
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
    except MaxRetriesExceededError:
        print(Fore.RED + "重复获取 Cookie 次数超过最大限制" + Fore.RESET)
    finally:
        if config is not None and headers is not None:
            save_results(config, headers, selected_courses)


if __name__ == "__main__":
    main()
