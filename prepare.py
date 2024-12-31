import json
import os
from dotenv import dotenv_values
from tools import get_cookies, get_time_info, get_course_categories, get_coueses

config = dotenv_values(".env")
cookies = config.get("COOKIES")
if cookies is None or cookies == "":
    cookies = get_cookies()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Cookie": cookies,
}


def main():
    if os.path.exists("courses.json"):
        with open("courses.json", "r") as f:
            selected_courses = json.load(f)
    else:
        selected_courses = []

    try:
        time_info = get_time_info(headers)
        if time_info is None:
            print("获取时间信息失败。")
            return
        categories = get_course_categories(time_info, headers)
        if categories is None:
            print("获取课程类别失败。")
            return
        elif len(categories) == 0:
            print("未找到课程类别。")
            return
        # print(categories)
        while True:
            for i, category in enumerate(categories):
                print(f"{i+1}. {category['name']}")
            try:
                opt = int(input("选择一个类别 (0 退出) : "))
                if opt == 0:
                    break
                selected_category = categories[opt - 1]
                while True:
                    keyword = input(
                        "输入你想查找的课程的关键词 (q 退出，直接回车查找全部) : "
                    )
                    if keyword == "q":
                        break
                    courses = get_coueses(
                        category=selected_category,
                        time_info=time_info,
                        headers=headers,
                        keyword=keyword,
                    )
                    if len(courses) == 0:
                        print("未找到课程。")
                        continue
                    else:
                        print(f"共找到{len(courses)}门课程。")

                    for course in courses:
                        name = course["name"]
                        teacher = course["teacher"]
                        opt = input(f"是否添加课程 {name} ({teacher})? (y/n/q): ")
                        if opt == "y":
                            selected_courses.append(course)
                        elif opt == "q":
                            break
            except ValueError:
                print("无效输入。")
    except KeyboardInterrupt:
        print("\n正在退出...")
    finally:
        with open("courses.json", "w") as f:
            json.dump(selected_courses, f, ensure_ascii=False, indent=4)

        config["COOKIES"] = headers["Cookie"]
        with open(".env", mode="w") as f:
            for key, value in config.items():
                f.write(f'{key}="{value}"\n')


if __name__ == "__main__":
    main()
