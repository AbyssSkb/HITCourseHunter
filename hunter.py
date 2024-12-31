import json
import time
from dotenv import dotenv_values
from tools import get_cookies, add_course

try:
    with open("courses.json", "r") as f:
        courses = json.load(f)
except FileNotFoundError:
    print("找不到文件courses.json。请先运行prepare.py。")
    exit(1)

config = dotenv_values(".env")
cookies = config.get("COOKIES")
if cookies is None or cookies == "":
    cookies = get_cookies()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Cookie": cookies,
}

unsucessful_courses = []


def main():
    try:
        for course in courses:
            status = add_course(course, headers)
            if not status:
                unsucessful_courses.append(course)
            print("等待3秒后继续...")
            print()
            time.sleep(3)
    except KeyboardInterrupt:
        print("\n正在退出...")
    finally:
        config["COOKIES"] = headers["Cookie"]
        with open(".env", mode="w") as f:
            for key, value in config.items():
                f.write(f'{key}="{value}"\n')

        with open("courses.json", "w") as f:
            json.dump(unsucessful_courses, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
