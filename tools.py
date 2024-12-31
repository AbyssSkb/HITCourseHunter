import requests
from DrissionPage import Chromium, ChromiumOptions
from dotenv import dotenv_values
import sys


def get_cookies():
    config = dotenv_values()
    username = config.get("USERNAME")
    password = config.get("PASSWORD")
    path = config.get("PATH")
    if username is None or password is None:
        print("请在.env文件中填写用户名和密码。")
        sys.exit(1)

    if path is None:
        print("请在.env文件中填写浏览器路径。")
        sys.exit(1)

    co = ChromiumOptions().set_browser_path(path)
    print("正在获取Cookies...")
    tab = Chromium(co).latest_tab
    tab.get(
        "https://ids.hit.edu.cn/authserver/login?service=http%3A%2F%2Fjw.hitsz.edu.cn%2FcasLogin"
    )
    ele = tab.ele("#username")
    ele.focus()
    ele.input(username, by_js=True)

    ele = tab.ele("#password")
    ele.focus()
    ele.input(password, by_js=True)

    ele = tab.ele("#login_submit")
    ele.focus()
    ele.click()
    tab.wait.load_start()
    print("登录成功，Cookies已获取。")
    return tab.cookies().as_str()


def get_time_info(headers: dict[str, str]):
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
            headers["Cookie"] = get_cookies()
            return get_time_info(headers)
        else:
            print("响应内容不是有效的JSON格式")
    else:
        print(f"请求失败，状态码：{response.status_code}")


def get_course_categories(time_info: dict[str, str], headers: dict[str, str]):
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


def get_coueses(
    category: dict[str, str],
    time_info: dict[str, str],
    headers: dict[str, str],
    keyword: str,
) -> list[dict[str, str]]:
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
        except ValueError:
            print("响应内容不是有效的JSON格式")
    else:
        print(f"请求失败，状态码：{response.status_code}")
    return []


def add_course(course: dict[str, str], headers: dict[str, str]) -> bool:
    print(f"正在选择课程：{course['name']} ({course['teacher']}) ...")
    url = "http://jw.hitsz.edu.cn/Xsxk/addGouwuche"
    data = {
        "p_xktjz": "rwtjzyx",
        "p_xn": course["academic_year"],
        "p_xq": course["term"],
        "p_xkfsdm": course["code"],
        "p_id": course["id"],
    }
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        if "application/json" in response.headers["Content-Type"]:
            response_json = response.json()
            message = response_json["message"]
            if message == "操作成功":
                print("选课成功")
                return True
            else:
                print(f"选课失败：{message}")
        elif "text/html" in response.headers["Content-Type"]:
            print("Cookie过期，请重新登录")
            headers["Cookie"] = get_cookies()
            return add_course(course, headers)
        else:
            print("响应内容不是有效的JSON格式")
    else:
        print(f"请求失败，状态码：{response.status_code}")
    return False
