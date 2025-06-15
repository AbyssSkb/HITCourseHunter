import requests
from dotenv import dotenv_values
import sys
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os
from colorama import Fore
from DrissionPage import Chromium, ChromiumOptions


def load_existing_courses() -> list[dict[str, str]]:
    """加载已选择的课程列表

    从 courses.json 文件中读取之前已选择的课程信息。
    如果文件不存在，则返回空列表。

    Returns:
        list[dict[str, str]]: 包含课程信息的列表，每个课程为一个字典
    """
    if os.path.exists("courses.json"):
        with open("courses.json", "r") as f:
            return json.load(f)
    return []


def display_categories(categories: list[dict[str, str]]):
    """显示可选课程类别列表

    将课程类别打印到控制台。

    Args:
        categories (list[dict[str, str]]): 课程类别列表
    """
    for i, category in enumerate(categories):
        print(Fore.CYAN + f"{i + 1}. {category['name']}" + Fore.RESET)


def handle_course_selection(
    courses: list[dict[str, str]], selected_courses: list[dict[str, str]]
) -> bool:
    """处理用户的课程选择过程

    遍历课程列表，让用户对每门课程进行选择：
    - y: 添加到选课列表
    - n: 跳过当前课程
    - q: 退出选课过程

    Args:
        courses (list[dict[str, str]]): 可选课程列表
        selected_courses (list[dict[str, str]]): 已选课程列表

    Returns:
        bool: 如果用户选择退出返回 True，否则返回 False
    """
    if len(courses) == 0:
        print(Fore.YELLOW + "未找到课程。" + Fore.RESET)
        return False

    print(Fore.CYAN + f"共找到{len(courses)}门课程。" + Fore.RESET)
    for course in courses:
        name = course["name"]
        information = course["information"]
        print(Fore.CYAN + f"\n课程名称：{name}\n{information}" + Fore.RESET)
        opt = input(Fore.GREEN + "是否选择该课程？(y/n/q) : " + Fore.RESET)
        if opt == "y":
            selected_courses.append(course)
            print(Fore.GREEN + "已添加到选课列表" + Fore.RESET)
        elif opt == "q":
            return True
    return False


def validate_time_format(time_str: str) -> bool:
    """验证时间字符串格式

    检查时间字符串是否符合 HH:MM:SS 格式。

    Args:
        time_str (str): 要验证的时间字符串

    Returns:
        bool: 时间格式正确返回 True，否则返回 False
    """
    try:
        time.strptime(time_str, "%H:%M:%S")
        return True
    except ValueError:
        return False


def load_config() -> dict[str, str]:
    """加载和验证配置信息

    从 .env 文件中加载配置信息，包括 Cookie 和开始时间等关键参数。
    如果 Cookie 不存在或为空，会自动调用 get_cookies() 获取新的 Cookie。
    会对 START_TIME 的格式进行验证，确保其符合 HH:MM:SS 格式。

    Returns:
        dict[str, str]: 包含配置信息的字典

    Raises:
        ValueError: 当 START_TIME 的格式不符合 HH:MM:SS 规范时抛出
    """
    config = dotenv_values(".env")
    cookies = config.get("COOKIES")
    start_time = config.get("START_TIME")

    if start_time and not validate_time_format(start_time):
        raise ValueError("时间格式不正确，请检查 START_TIME 的值（格式：HH:MM:SS）")

    if not cookies:
        cookies = get_cookies()
        config["COOKIES"] = cookies

    return config


def load_courses() -> list[dict[str, str]]:
    """加载待选课程列表

    从 courses.json 文件加载待选课程信息。

    Returns:
        list[dict[str, str]]: 待选课程列表

    Raises:
        FileNotFoundError: 当 courses.json 文件不存在时抛出
        ValueError: 当没有待选课程时抛出
    """
    try:
        with open("courses.json", "r") as f:
            courses = json.load(f)

        if len(courses) == 0:
            raise ValueError("没有要抢的课程")
        return courses
    except FileNotFoundError:
        raise FileNotFoundError("找不到文件 courses.json。请先运行 prepare.py。")


def get_headers(cookies: str) -> dict[str, str]:
    """生成 HTTP 请求头

    根据提供的 Cookie 构造 HTTP 请求头字典。
    使用预设的 User-Agent 确保请求行为与浏览器一致。

    Args:
        cookies (str): 用于身份验证的Cookie字符串

    Returns:
        dict[str, str]: 包含 User-Agent 和 Cookie 的请求头字典:
    """
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Cookie": cookies,
    }


def save_results(
    config: dict[str, str], headers: dict[str, str], courses: list[dict[str, str]]
) -> None:
    """保存更新后的配置和课程信息

    将最新的 Cookie 保存回配置文件，并将课程信息更新到 courses.json 文件中。
    这样可以在程序重启后保持登录状态和课程选择状态。

    Args:
        config (dict[str, str]): 配置信息字典
        headers (dict[str, str]): 包含 Cookie 的请求头字典
        courses (list[dict[str, str]]): 课程信息列表
    """
    config["COOKIES"] = headers["Cookie"]
    with open(".env", mode="w") as f:
        for key, value in config.items():
            f.write(f'{key}="{value}"\n')

    with open("courses.json", "w") as f:
        json.dump(courses, f, ensure_ascii=False, indent=4)


def wait_until_start(start_time: str) -> None:
    """倒计时等待至指定时间

    实现精确的定时等待功能，直到达到指定的开始时间。
    会显示倒计时信息，每 0.1 秒更新一次。
    如果当前时间已经超过目标时间，则立即开始执行。

    Args:
        start_time (str): 目标开始时间，格式为 "HH:MM:SS"
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
        print(Fore.YELLOW + "目标时间已过，直接开始抢课！" + Fore.RESET)
        return

    while True:
        remaining = (target_time - datetime.now()).total_seconds()
        if remaining <= 0:
            break
        print(
            Fore.CYAN + f"\r距离开始还有 {int(remaining)} 秒..." + Fore.RESET,
            end="",
            flush=True,
        )
        time.sleep(0.1)

    print("\r" + " " * 50 + "\r", end="")  # 清除倒计时行
    print(Fore.GREEN + "开始抢课！" + Fore.RESET)


def get_cookies() -> str:
    """获取新的登录 Cookie

    通过模拟登录过程获取有效的 Cookie。
    使用 .env 文件中配置的用户名和密码进行统一身份认证。

    Returns:
        str: 包含所有必要认证信息的 Cookie 字符串

    Raises:
        SystemExit: 当 .env 中未配置用户名或密码时退出程序
    """
    config = dotenv_values(".env")
    username = config.get("USERNAME")
    password = config.get("PASSWORD")
    headless = config.get("HEADLESS")
    headless = True if headless is None else headless.lower() == "true"
    path = config.get("PATH")
    if username is None or password is None:
        print(Fore.RED + "请在 .env 文件中填写用户名和密码。" + Fore.RESET)
        sys.exit(1)

    if path is None:
        print(Fore.RED + "请在 .env 文件中填写浏览器路径。" + Fore.RESET)
        sys.exit(1)

    co = ChromiumOptions().set_browser_path(path)
    co.headless(headless)
    print("正在获取Cookies...")
    browser = Chromium(co)
    tab = browser.latest_tab
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
    cookies = tab.cookies().as_str()
    print(Fore.GREEN + "Cookie已获取。" + Fore.RESET)
    browser.quit()
    return cookies


def get_time_info(headers: dict[str, str]) -> dict[str, str]:
    """获取当前及选课学年学期信息

    从教务系统获取当前的学年学期以及选课所属的学年学期信息。
    如果 Cookie 过期会自动重新获取。

    Args:
        headers (dict[str, str]): 包含 Cookie 的 HTTP 请求头

    Returns:
        dict[str, str]: 包含以下信息的字典:
            - current_academic_year: 当前学年，如 "2023-2024"
            - current_term: 当前学期，如 "2" 表示下学期
            - academic_year: 选课学年，如 "2023-2024"
            - term: 选课学期，如 "2"

    Raises:
        KeyError: 响应数据格式不符合预期时抛出
    """
    print(Fore.CYAN + "正在获取时间信息..." + Fore.RESET)
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
                print(Fore.GREEN + "时间信息已获取。" + Fore.RESET)
                return {
                    "current_academic_year": current_academic_year,
                    "current_term": current_term,
                    "academic_year": academic_year,
                    "term": term,
                }
            except KeyError:
                message = response_json["message"]
                print(Fore.RED + f"错误：{message}" + Fore.RESET)
        elif "text/html" in response.headers["Content-Type"]:
            print(Fore.YELLOW + "Cookie 已过期，尝试重新获取..." + Fore.RESET)
            headers["Cookie"] = get_cookies()
            return get_time_info(headers)
        else:
            print(Fore.RED + "响应内容不是有效的 JSON 格式" + Fore.RESET)
    else:
        print(Fore.RED + f"请求失败，状态码：{response.status_code}" + Fore.RESET)


def get_course_categories(
    time_info: dict[str, str], headers: dict[str, str]
) -> list[dict[str, str]]:
    """获取课程类别列表

    Args:
        time_info (dict[str, str]): 学年学期信息字典
        headers (dict[str, str]): HTTP 请求头字典

    Returns:
        list[dict[str, str]]: 课程类别列表，每个元素是包含课程类别信息的字典
    """
    print(Fore.CYAN + "正在获取课程类别..." + Fore.RESET)
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
                code = element["xkfsdm"]  # 获取课程类别代码
                name = element["xkfsmc"]  # 获取课程类别名称
                categories.append({"code": code, "name": name})

            print(Fore.GREEN + "课程类别已获取。" + Fore.RESET)
            return categories
        elif "text/html" in response.headers["Content-Type"]:
            print(Fore.YELLOW + "Cookie 已过期，尝试重新获取..." + Fore.RESET)
            headers["Cookie"] = get_cookies()
            return get_course_categories(time_info, headers)
        else:
            print(Fore.RED + "响应内容不是有效的 JSON 格式" + Fore.RESET)
    else:
        print(Fore.RED + f"请求失败，状态码：{response.status_code}" + Fore.RESET)
    return []


def get_coueses(
    category: dict[str, str],
    time_info: dict[str, str],
    headers: dict[str, str],
    keyword: str,
) -> list[dict[str, str]]:
    """根据类别和关键词搜索课程

    获取指定类别下符合关键词的可选课程列表。
    如果关键词为空字符串，则返回该类别下的所有课程。

    Args:
        category (dict[str, str]): 包含课程类别代码和名称的字典
        time_info (dict[str, str]): 学年学期信息字典
        headers (dict[str, str]): HTTP 请求头字典
        keyword (str): 搜索关键词，可以为空字符串

    Returns:
        list[dict[str, str]]: 课程列表，每个课程包含:
            - id (str): 课程唯一标识
            - name (str): 课程名称（包含体育项目名称）
            - information (str): 课程详细信息（包括上课时间、地点、教师等）
            - code (str): 课程类别代码
            - academic_year (str): 学年
            - term (str): 学期

    Raises:
        ValueError: 当服务器响应不是有效的 JSON 格式时抛出
    """
    if keyword == "":
        print(Fore.CYAN + f"正在获取`{category['name']}`类别下所有课程..." + Fore.RESET)
    else:
        print(
            Fore.CYAN
            + f"正在获取`{category['name']}`类别下关键词为`{keyword}`的课程..."
            + Fore.RESET
        )
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
                courses = []
                for course in elements:
                    soup = BeautifulSoup(course["kcxx"], "html.parser")
                    information = soup.get_text("\n")
                    courses.append(
                        {
                            "id": course["id"],
                            "name": course["kcmc"].strip() + course["tyxmmc"].strip(),
                            "information": information.strip(),
                            "code": category["code"],
                            "academic_year": time_info["academic_year"],
                            "term": time_info["term"],
                        }
                    )
                return courses
            except KeyError:
                message = response_json["message"]
                print(Fore.RED + f"错误：{message}" + Fore.RESET)
        except ValueError:
            print("响应内容不是有效的JSON格式")
    else:
        print(Fore.RED + f"请求失败，状态码：{response.status_code}" + Fore.RESET)
    return []


def add_course(course: dict[str, str], headers: dict[str, str]) -> bool:
    """将课程添加到选课列表

    尝试选择一门课程，如果 Cookie 过期会自动重新登录。
    选课结果会通过控制台输出反馈。

    Args:
        course (dict[str, str]): 课程信息字典
        headers (dict[str, str]): 包含 Cookie 的 HTTP 请求头

    Returns:
        bool: 选课成功返回 True，失败返回 False
    """
    name = course["name"]
    information = course["information"]
    print(Fore.CYAN + f"\n正在添加课程：{name}\n{information}" + Fore.RESET)
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
                print(Fore.GREEN + "选课成功" + Fore.RESET)
                return True
            else:
                print(Fore.RED + f"选课失败：{message}" + Fore.RESET)
        elif "text/html" in response.headers["Content-Type"]:
            print(Fore.YELLOW + "Cookie已过期，尝试重新获取..." + Fore.RESET)
            headers["Cookie"] = get_cookies()
            return add_course(course, headers)
        else:
            print(Fore.RED + "响应内容不是有效的JSON格式" + Fore.RESET)
    else:
        print(Fore.RED + f"请求失败，状态码：{response.status_code}" + Fore.RESET)
    return False
