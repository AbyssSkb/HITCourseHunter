import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Cookie": os.getenv("COOKIE"),
}


def get_time_info():
    print("正在获取时间信息...")
    url = "http://jw.hitsz.edu.cn/Xsxk/queryXkdqXnxq"
    data = {"mxpylx": "1"}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        if "application/json" in response.headers["Content-Type"]:
            response_json: dict = response.json()
            try:
                current_academic_year = response_json["p_dqxn"]
                current_term = response_json["p_dqxq"]
                academic_year = response_json["p_xn"]
                term = response_json["p_xq"]
                # print(
                #     f"Current academic year: {current_academic_year}, term: {current_term}"
                # )
                # print(f"Academic year: {academic_year}, term: {term}")
                print("时间信息已获取。")
                return {
                    "current_academic_year": current_academic_year,
                    "current_term": current_term,
                    "academic_year": academic_year,
                    "term": term,
                }
            except KeyError:
                print(response_json)
        elif "text/html" in response.headers["Content-Type"]:
            print("Cookie过期，请重新登录")
        else:
            print("响应内容不是有效的JSON格式")
    else:
        print(f"请求失败，状态码：{response.status_code}")


def get_course_categories(time_info: dict[str, str]):
    print("正在获取课程类别...")
    url = "http://jw.hitsz.edu.cn/Xsxk/queryYxkc"
    data = {
        "p_xn": time_info["academic_year"],
        "p_xq": time_info["term"],
    }
    response = requests.post(url=url, headers=headers, data=data)
    if response.status_code == 200:
        if "application/json" in response.headers["Content-Type"]:
            response_json: dict = response.json()
            categories = []
            elements = response_json["xkgzszList"]
            for element in elements:
                code = element["xkfsdm"]
                name = element["xkfsmc"]
                categories.append({"code": code, "name": name})

            print("课程类别已获取。")
            return categories
        elif "text/html" in response.headers["Content-Type"]:
            print("Cookie过期，请重新登录")
        else:
            print("响应内容不是有效的JSON格式")
    else:
        print(f"请求失败，状态码：{response.status_code}")


def get_coueses(category: dict[str, str], time_info: dict[str, str], keyword: str = ""):
    if keyword == "":
        print(f"正在获取`{category['name']}`类别下所有课程...")
    else:
        print(f"正在获取`{category['name']}`类别下关键词为`{keyword}`的课程...")
    url = "http://jw.hitsz.edu.cn/Xsxk/queryKxrw"
    data = {
        "p_pylx": "1",
        "p_gjz": keyword,
        "p_xn": time_info["academic_year"],
        "p_xq": time_info["term"],
        "p_dqxn": time_info["current_academic_year"],
        "p_dqxq": time_info["current_term"],
        "p_xkfsdm": category["code"],
    }

    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        try:
            response_json: dict = response.json()
            try:
                elements = response_json["kxrwList"]["list"]
                # print(elements[0])
                courses = [
                    {
                        "id": course["id"],
                        "name": course["kcmc"] + course["tyxmmc"].strip(),
                        "teacher": course["dgjsmc"],
                        "code": category["code"],
                        "academic_year": time_info["academic_year"],
                        "term": time_info["term"],
                    }
                    for course in elements
                ]
                return courses
            except KeyError:
                print(response_json["message"])
                return []
        except ValueError:
            print("响应内容不是有效的JSON格式")
            return []
    else:
        print(f"请求失败，状态码：{response.status_code}")
        return []


def main():
    if os.path.exists("courses.json"):
        with open("courses.json", "r") as f:
            selected_courses = json.load(f)
    else:
        selected_courses = []

    try:
        time_info = get_time_info()
        if time_info is None:
            print("获取时间信息失败。")
            return
        categories = get_course_categories(time_info)
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
                        selected_category, time_info=time_info, keyword=keyword
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


if __name__ == "__main__":
    main()
