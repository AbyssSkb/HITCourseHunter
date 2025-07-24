import json
import os
import random
import sys
import time
from base64 import b64encode
from datetime import datetime

import requests
from colorama import Fore
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from dotenv import dotenv_values
from selectolax.parser import HTMLParser

MAX_RETRIES = 3
AES_CHARS = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"


def random_string(length: int) -> str:
    """生成指定长度的随机字符串

    该函数通过从 AES_CHARS 中随机选择字符来创建字符串。

    Args:
        length (int): 需要生成的随机字符串长度

    Returns:
        str: 指定长度的随机字符串
    """
    return "".join(random.choice(AES_CHARS) for _ in range(length))


def get_aes_string(data: str, key: str, iv: str) -> str:
    """使用 AES CBC 模式和 PKCS7 填充加密数据

    该函数对输入的明文数据使用 AES 算法进行加密，采用 CBC 工作模式和 PKCS7 填充方式，
    最后将加密结果编码为 Base64 字符串以便于传输和存储。

    Args:
        data (str): 要加密的明文数据。
        key (str): 加密密钥。
        iv (str): 初始化向量 (IV)。

    Returns:
        str: Base64 编码的密文。
    """
    key_bytes = key.encode("utf-8")
    iv_bytes = iv.encode("utf-8")
    data_bytes = data.encode("utf-8")

    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    padded_data = pad(data_bytes, AES.block_size, style="pkcs7")
    encrypted_bytes = cipher.encrypt(padded_data)

    return b64encode(encrypted_bytes).decode("utf-8")


def encrypt_password(password: str, salt: str) -> str:
    """使用 AES 加密密码

    该函数通过添加随机前缀、结合盐值和初始化向量来加密密码。
    主要用于确保密码在传输过程中的安全性。

    Args:
        password (str): 需要加密的密码明文
        salt (str): 用于加密的盐值

    Returns:
        str: 经过 Base64 编码的加密密码
    """
    prefix_random = random_string(64)
    combined_data = prefix_random + password
    iv = random_string(16)
    encrypted_result = get_aes_string(combined_data, salt, iv)
    return encrypted_result


class MaxRetriesExceededError(Exception):
    """当重试次数超过允许的最大次数时抛出"""

    def __init__(self, max_retries: int):
        super().__init__(f"重试次数超过最大限制：{max_retries}")


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


def validate_course_data(course: dict[str, str]) -> bool:
    """验证课程数据结构的完整性

    检查课程字典是否包含所有必需的字段。

    Args:
        course (dict[str, str]): 要验证的课程数据字典

    Returns:
        bool: 数据有效返回 True，否则返回 False
    """
    required_fields = ["id", "name", "information", "code", "academic_year", "term"]
    return all(field in course and course[field] is not None for field in required_fields)


def display_categories(categories: list[dict[str, str]]) -> None:
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

    print(Fore.GREEN + f"共找到 {len(courses)} 门课程。" + Fore.RESET)
    for course in courses:
        name = course["name"]
        information = course["information"]
        print(Fore.CYAN + f"\n课程名称：{name}\n{information}" + Fore.RESET)
        opt = input(Fore.WHITE + "是否选择该课程？(y/n/q) : " + Fore.RESET)
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

    filtered_config = {k: v for k, v in config.items() if v is not None}
    return filtered_config


def load_courses() -> list[dict[str, str]]:
    """加载待选课程列表

    从 courses.json 文件加载待选课程信息。

    Returns:
        list[dict[str, str]]: 待选课程列表

    Raises:
        FileNotFoundError: 当 courses.json 文件不存在时抛出
        ValueError: 当没有待选课程或课程数据不完整时抛出
    """
    try:
        with open("courses.json", "r") as f:
            courses = json.load(f)

        if len(courses) == 0:
            raise ValueError("没有要抢的课程")
        
        # Validate each course data structure
        invalid_courses = [i for i, course in enumerate(courses) if not validate_course_data(course)]
        if invalid_courses:
            raise ValueError(f"课程数据不完整，索引 {invalid_courses} 的课程缺少必需字段")
        
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
        # Use adaptive sleep - sleep longer when there's more time remaining
        sleep_time = min(1.0, max(0.1, remaining / 60))
        time.sleep(sleep_time)

    print("\r" + " " * 50 + "\r", end="")  # 清除倒计时行
    print(Fore.GREEN + "开始抢课！" + Fore.RESET)


def get_cookies() -> str:
    config = dotenv_values(".env")
    username = config.get("USERNAME")
    password = config.get("PASSWORD")
    if username is None or password is None:
        print(Fore.RED + "请在 .env 文件中填写用户名和密码。" + Fore.RESET)
        sys.exit(1)

    with requests.Session() as session:
        response = session.get(
            "https://ids.hit.edu.cn/authserver/login",
            params={"service": "http://jw.hitsz.edu.cn/casLogin"},
        )

        tree = HTMLParser(response.text)

        selector = "div#pwdLoginDiv"
        node = tree.css_first(selector)
        if node is None:
            raise ValueError(f"找不到匹配选择器 '{selector}' 的元素")

        event_id_selector = "input#_eventId"
        event_id_node = node.css_first(event_id_selector)
        if event_id_node is None:
            raise ValueError(f"找不到匹配选择器 '{event_id_selector}' 的元素")

        cllt_selector = "input#cllt"
        cllt_node = node.css_first(cllt_selector)
        if cllt_node is None:
            raise ValueError(f"找不到匹配选择器 '{cllt_selector}' 的元素")

        dllt_selector = "input#dllt"
        dllt_node = node.css_first(dllt_selector)
        if dllt_node is None:
            raise ValueError(f"找不到匹配选择器 '{dllt_selector}' 的元素")

        lt_selector = "input#lt"
        lt_node = node.css_first(lt_selector)
        if lt_node is None:
            raise ValueError(f"找不到匹配选择器 '{lt_selector}' 的元素")

        salt_selector = "input#pwdEncryptSalt"
        salt_node = node.css_first(salt_selector)
        if salt_node is None:
            raise ValueError(f"找不到匹配选择器 '{salt_selector}' 的元素")

        execution_selector = "input#execution"
        execution_node = node.css_first(execution_selector)
        if execution_node is None:
            raise ValueError(f"找不到匹配选择器 '{execution_selector}' 的元素")

        event_id = event_id_node.attributes["value"]
        cllt = cllt_node.attributes["value"]
        dllt = dllt_node.attributes["value"]
        lt = lt_node.attributes["value"]
        salt = salt_node.attributes["value"]
        if salt is None:
            raise ValueError("元素中没有 'value' 属性的值")

        execution = execution_node.attributes["value"]

        encrypted_password = encrypt_password(password, salt)
        session.post(
            "https://ids.hit.edu.cn/authserver/login",
            params={"service": "http://jw.hitsz.edu.cn/casLogin"},
            data={
                "username": username,
                "password": encrypted_password,
                "captcha": "",
                "_eventId": event_id,
                "cllt": cllt,
                "dllt": dllt,
                "lt": lt,
                "execution": execution,
            },
        )
        cookies = session.cookies.get_dict(domain="jw.hitsz.edu.cn")
        return f"route={cookies['route']}; JSESSIONID={cookies['JSESSIONID']}"


def get_time_info(headers: dict[str, str], retry_count: int = 0) -> dict[str, str]:
    """获取当前及选课学年学期信息

    从教务系统获取当前的学年学期以及选课所属的学年学期信息。
    如果 Cookie 过期会自动重新获取。

    Args:
        headers (dict[str, str]): 包含 Cookie 的 HTTP 请求头
        retry_count (int): 当前重试次数

    Returns:
        dict[str, str]: 包含以下信息的字典:
            - current_academic_year: 当前学年，如 "2023-2024"
            - current_term: 当前学期，如 "2" 表示下学期
            - academic_year: 选课学年，如 "2023-2024"
            - term: 选课学期，如 "2"

    Raises:
        KeyError: 响应数据格式不符合预期时抛出
        MaxRetriesExceededError: 当重试次数超过最大限制时抛出
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

            if retry_count >= MAX_RETRIES:
                raise MaxRetriesExceededError(MAX_RETRIES)

            headers["Cookie"] = get_cookies()
            return get_time_info(headers, retry_count + 1)
        else:
            print(Fore.RED + "响应内容不是有效的 JSON 格式" + Fore.RESET)
    else:
        print(Fore.RED + f"请求失败，状态码：{response.status_code}" + Fore.RESET)
    return {}


def get_course_categories(
    time_info: dict[str, str], headers: dict[str, str], retry_count: int = 0
) -> list[dict[str, str]]:
    """获取课程类别列表

    Args:
        time_info (dict[str, str]): 学年学期信息字典
        headers (dict[str, str]): HTTP 请求头字典
        retry_count (int): 当前重试次数

    Returns:
        list[dict[str, str]]: 课程类别列表，每个元素是包含课程类别信息的字典

    Raises:
        MaxRetriesExceededError: 当重试次数超过最大限制时抛出
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

            if retry_count >= MAX_RETRIES:
                raise MaxRetriesExceededError(MAX_RETRIES)

            headers["Cookie"] = get_cookies()
            return get_course_categories(time_info, headers, retry_count + 1)
        else:
            print(Fore.RED + "响应内容不是有效的 JSON 格式" + Fore.RESET)
    else:
        print(Fore.RED + f"请求失败，状态码：{response.status_code}" + Fore.RESET)
    return []


def get_courses(
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
                    tree = HTMLParser(course["kcxx"])
                    information = tree.text(separator="\n")
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
            print(Fore.RED + "响应内容不是有效的 JSON 格式" + Fore.RESET)
    else:
        print(Fore.RED + f"请求失败，状态码：{response.status_code}" + Fore.RESET)
    return []


def add_course(
    course: dict[str, str], headers: dict[str, str], retry_count: int = 0
) -> bool:
    """将课程添加到选课列表

    尝试选择一门课程，如果 Cookie 过期会自动重新登录。
    选课结果会通过控制台输出反馈。

    Args:
        course (dict[str, str]): 课程信息字典
        headers (dict[str, str]): 包含 Cookie 的 HTTP 请求头
        retry_count (int): 当前重试次数

    Returns:
        bool: 选课成功返回 True，失败返回 False

    Raises:
        MaxRetriesExceededError: 当重试次数超过最大限制时抛出
        ValueError: 当课程数据不完整时抛出
    """
    if not validate_course_data(course):
        raise ValueError("课程数据不完整，缺少必需字段")
    
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
            print(Fore.YELLOW + "Cookie 已过期，尝试重新获取..." + Fore.RESET)

            if retry_count >= MAX_RETRIES:
                raise MaxRetriesExceededError(MAX_RETRIES)

            headers["Cookie"] = get_cookies()
            return add_course(course, headers, retry_count + 1)
        else:
            print(Fore.RED + "响应内容不是有效的 JSON 格式" + Fore.RESET)
    else:
        print(Fore.RED + f"请求失败，状态码：{response.status_code}" + Fore.RESET)
    return False
