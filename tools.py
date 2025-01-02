import requests
from dotenv import dotenv_values
import sys
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os


def load_existing_courses():
    """加载已选择的课程列表

    从courses.json文件中读取之前已选择的课程信息。
    如果文件不存在，则返回空列表。

    Returns:
        list[dict]: 包含课程信息的列表，每个课程为一个字典
    """
    if os.path.exists("courses.json"):
        with open("courses.json", "r") as f:
            return json.load(f)
    return []


def display_categories(categories):
    """显示可选课程类别列表

    将课程类别以编号+名称的形式打印到控制台。

    Args:
        categories (list[dict]): 课程类别列表，每个类别包含name字段
    """
    for i, category in enumerate(categories):
        print(f"{i+1}. {category['name']}")


def handle_course_selection(courses: list[dict[str, str]], selected_courses: list[dict[str, str]]):
    """处理用户的课程选择过程

    遍历课程列表，让用户对每门课程进行选择：
    - y: 添加到选课列表
    - n: 跳过当前课程
    - q: 退出选课过程

    Args:
        courses (list[dict]): 可选课程列表
        selected_courses (list[dict]): 已选课程列表

    Returns:
        bool: 如果用户选择退出返回True，否则返回False
    """
    if len(courses) == 0:
        print("未找到课程。")
        return False

    print(f"共找到{len(courses)}门课程。")
    for course in courses:
        name = course["name"]
        teacher = course["teacher"]
        opt = input(f"是否添加课程 {name} ({teacher})? (y/n/q): ")
        if opt == "y":
            selected_courses.append(course)
        elif opt == "q":
            return True
    return False


def validate_time_format(time_str):
    """验证时间字符串格式

    检查时间字符串是否符合HH:MM:SS格式。

    Args:
        time_str (str): 要验证的时间字符串

    Returns:
        bool: 时间格式正确返回True，否则返回False
    """
    try:
        time.strptime(time_str, "%H:%M:%S")
        return True
    except ValueError:
        return False


def load_config():
    """加载和验证配置信息

    从.env文件中加载配置信息，包括Cookie和开始时间等关键参数。
    如果Cookie不存在或为空，会自动调用get_cookies()获取新的Cookie。
    会对START_TIME的格式进行验证，确保其符合HH:MM:SS格式。

    Returns:
        dict: 包含以下配置项的字典:
            - COOKIES: 用于身份验证的Cookie字符串
            - START_TIME: 开始抢课的时间（格式：HH:MM:SS）
            - 其他在.env文件中定义的配置项

    Raises:
        ValueError: 当START_TIME的格式不符合HH:MM:SS规范时抛出
    """
    config = dotenv_values(".env")
    cookies = config.get("COOKIES")
    start_time = config.get("START_TIME")

    if start_time and not validate_time_format(start_time):
        raise ValueError("时间格式不正确，请检查START_TIME的值（格式：HH:MM:SS）")

    if cookies is None or cookies == "":
        cookies = get_cookies()
        config["COOKIES"] = cookies

    return config


def load_courses():
    """加载待选课程列表

    从courses.json文件加载待选课程信息。

    Returns:
        list[dict]: 待选课程列表

    Raises:
        FileNotFoundError: 当courses.json文件不存在时抛出
        ValueError: 当没有待选课程时抛出
    """
    try:
        with open("courses.json", "r") as f:
            courses = json.load(f)

        if len(courses) == 0:
            raise ValueError("没有要抢的课程")
        return courses
    except FileNotFoundError:
        raise FileNotFoundError("找不到文件courses.json。请先运行prepare.py。")


def get_headers(cookies):
    """生成HTTP请求头

    根据提供的Cookie构造用于HTTP请求的headers字典。
    使用预设的User-Agent确保请求行为与浏览器一致。

    Args:
        cookies (str): 用于身份验证的Cookie字符串

    Returns:
        dict: 包含以下键值的请求头字典:
            - User-Agent: 浏览器标识字符串
            - Cookie: 身份验证Cookie
    """
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Cookie": cookies,
    }


def save_results(config, headers, courses):
    """保存更新后的配置和课程信息

    将最新的Cookie保存回配置文件，并将课程信息更新到JSON文件中。
    这样可以在程序重启后保持登录状态和课程选择状态。

    Args:
        config (dict): 配置信息字典
        headers (dict): 包含Cookie的请求头字典
        courses (list): 课程信息列表
    """
    config["COOKIES"] = headers["Cookie"]
    with open(".env", mode="w") as f:
        for key, value in config.items():
            f.write(f'{key}="{value}"\n')

    with open("courses.json", "w") as f:
        json.dump(courses, f, ensure_ascii=False, indent=4)


def wait_until_start(start_time):
    """倒计时等待至指定时间

    实现精确的定时等待功能，直到达到指定的开始时间。
    会显示倒计时信息，每0.1秒更新一次。
    如果当前时间已经超过目标时间，则立即开始执行。

    Args:
        start_time (str): 目标开始时间，格式为"HH:MM:SS"
    """
    now = datetime.now()
    time_parts = start_time.strip().split(":")
    target_time = now.replace(
        hour=int(time_parts[0]),
        minute=int(time_parts[1]),
        second=int(time_parts[2]),
        microsecond=0,
    )

    time_delta = (target_time - now).total_seconds()

    if time_delta < 0:
        print("目标时间已过，直接开始抢课！")
        return

    while True:
        remaining = (target_time - datetime.now()).total_seconds()
        if remaining <= 0:
            break
        print(f"\r距离开始还有 {int(remaining)} 秒...", end="", flush=True)
        time.sleep(0.1)

    print("\n开始抢课！")


def get_cookies():
    """获取新的登录Cookie

    通过模拟登录过程获取有效的Cookie。
    使用.env文件中配置的用户名和密码进行统一身份认证。

    Returns:
        str: 包含所有必要认证信息的Cookie字符串

    Raises:
        SystemExit: 当.env中未配置用户名或密码时退出程序
    """
    config = dotenv_values(".env")
    username = config.get("USERNAME")
    password = config.get("PASSWORD")
    if username is None or password is None:
        print("请在.env文件中填写用户名和密码。")
        sys.exit(1)

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        }
    )

    params = {
        "type": "IDSUnion",
        "appId": "ff2dfca3a2a2448e9026a8c6e38fa52b",
        "success": "http://jw.hitsz.edu.cn/casLogin",
    }
    response = session.get(
        "https://ids.hit.edu.cn/authserver/combinedLogin.do", params=params
    )
    soup = BeautifulSoup(response.text, "html.parser")

    form = soup.select_one("#authZForm")
    url = "https://sso.hitsz.edu.cn:7002" + form["action"]
    client_id = soup.select_one("input[name=client_id]")["value"]
    scope = soup.select_one("input[name=scope]")["value"]
    state = soup.select_one("input[name=state]")["value"]
    data = {
        "action": "authorize",
        "response_type": "code",
        "redirect_uri": "https://ids.hit.edu.cn/authserver/callback",
        "client_id": client_id,
        "scope": scope,
        "state": state,
        "username": username,
        "password": password,
    }

    response = session.post(url, data=data)
    cookies = "; ".join(
        [
            f"{cookie.name}={cookie.value}"
            for cookie in session.cookies
            if "jw.hitsz.edu.cn" in cookie.domain
        ]
    )
    return cookies


def get_time_info(headers: dict[str, str]):
    """获取当前学年学期信息

    Args:
        headers: HTTP请求头字典

    Returns:
        dict: 包含以下键值的字典:
            - current_academic_year: 当前学年
            - current_term: 当前学期
            - academic_year: 选课学年
            - term: 选课学期
    """
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
    """获取课程类别列表

    Args:
        time_info: 学年学期信息字典
        headers: HTTP请求头字典

    Returns:
        list: 课程类别列表，每个类别是包含code和name的字典
    """
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
    """根据类别和关键词获取课程列表

    Args:
        category: 课程类别字典
        time_info: 学年学期信息字典
        headers: HTTP请求头字典
        keyword: 搜索关键词

    Returns:
        list: 课程列表，每个课程是包含id、name、teacher等信息的字典
    """
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
                elements: list[dict[str, str]] = response_json["kxrwList"]["list"]
                courses = [
                    {
                        "id": course["id"],
                        "name": course["kcmc"].strip() + course["tyxmmc"].strip(),
                        "teacher": course["dgjsmc"].strip(),
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
    """添加课程到购物车

    Args:
        course: 课程信息字典
        headers: HTTP请求头字典

    Returns:
        bool: 是否添加成功
    """
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
