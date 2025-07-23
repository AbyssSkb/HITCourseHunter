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
import sys

colorama.init()  # 初始化 colorama


def show_interface_choice():
    """显示界面选择"""
    print(Fore.GREEN + "🎯 HITCourseHunter - 课程选择" + Fore.RESET)
    print()
    print("请选择使用方式：")
    print(Fore.CYAN + "1. Web界面 (推荐) - 图形化选课界面" + Fore.RESET)
    print(Fore.YELLOW + "2. 命令行界面 - 传统文本界面" + Fore.RESET)
    print()
    
    while True:
        try:
            choice = input(Fore.WHITE + "请输入选择 (1 或 2): " + Fore.RESET).strip()
            if choice == "1":
                return "web"
            elif choice == "2":
                return "cli"
            else:
                print(Fore.RED + "无效选择，请输入 1 或 2" + Fore.RESET)
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n已取消" + Fore.RESET)
            sys.exit(0)


def start_web_interface():
    """启动Web界面"""
    try:
        print(Fore.GREEN + "正在启动Web界面..." + Fore.RESET)
        print(Fore.CYAN + "请在浏览器中打开: http://localhost:5000" + Fore.RESET)
        print(Fore.YELLOW + "按 Ctrl+C 停止服务器" + Fore.RESET)
        print()
        
        # Import and run Flask app
        from app import main as run_web_app
        run_web_app()
        
    except ImportError:
        print(Fore.RED + "Web界面依赖缺失，请安装 Flask:" + Fore.RESET)
        print(Fore.YELLOW + "pip install flask" + Fore.RESET)
        print()
        print(Fore.CYAN + "正在启动命令行界面..." + Fore.RESET)
        start_cli_interface()
    except Exception as e:
        print(Fore.RED + f"启动Web界面失败: {str(e)}" + Fore.RESET)
        print(Fore.CYAN + "正在启动命令行界面..." + Fore.RESET)
        start_cli_interface()


def start_cli_interface():
    """启动命令行界面"""
    print(Fore.CYAN + "使用命令行界面进行课程选择" + Fore.RESET)
    run_course_preparation_cli()


def run_course_preparation_cli():
    """执行命令行课程准备流程"""
    config = None
    headers = None
    selected_courses = []

    try:
        selected_courses = load_existing_courses()
        config = load_config()
        headers = get_headers(config["COOKIES"])

        time_info = get_time_info(headers)
        if not time_info:
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
            opt = int(input(Fore.WHITE + "选择一个类别 (0 退出程序) : " + Fore.RESET))
            if opt == 0:
                break

            selected_category = categories[opt - 1]
            while True:
                keyword = input(
                    Fore.WHITE
                    + "输入你想查找的课程的关键词 (q 返回上一级，直接回车查找全部) : "
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
    # 显示界面选择
    interface_choice = show_interface_choice()
    
    if interface_choice == "web":
        start_web_interface()
    else:
        start_cli_interface()


if __name__ == "__main__":
    main()
