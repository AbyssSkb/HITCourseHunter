#!/usr/bin/env python3
"""
Web UI for HITCourseHunter - A user-friendly interface for course selection
"""

import json
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.serving import run_simple
import colorama
from colorama import Fore

from tools import (
    MaxRetriesExceededError,
    get_headers,
    get_time_info,
    get_course_categories,
    get_courses,
    load_config,
    load_existing_courses,
    save_results,
)

colorama.init()  # 初始化 colorama

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages

@app.route('/')
def index():
    """主页 - 显示欢迎信息和导航"""
    return render_template('index.html')

@app.route('/courses')
def course_selection():
    """课程选择页面"""
    try:
        # 加载已选课程
        selected_courses = load_existing_courses()
        
        # For demo purposes, show a mock interface if no credentials
        if not os.path.exists('.env') or not os.path.getsize('.env'):
            flash("请先在设置页面配置用户名和密码", "warning")
            return render_template('course_selection.html', 
                                 categories=[], 
                                 selected_courses=selected_courses,
                                 time_info={})
        
        try:
            # 加载配置
            config = load_config()
            headers = get_headers(config["COOKIES"])
            
            # 获取时间信息
            time_info = get_time_info(headers)
            if not time_info:
                flash("获取时间信息失败，请检查网络连接和登录凭据", "warning")
                return render_template('course_selection.html', 
                                     categories=[], 
                                     selected_courses=selected_courses,
                                     time_info={})
            
            # 获取课程类别
            categories = get_course_categories(time_info, headers)
            if not categories:
                flash("获取课程类别失败", "warning")
                categories = []
            
            return render_template('course_selection.html', 
                                 categories=categories, 
                                 selected_courses=selected_courses,
                                 time_info=time_info)
        
        except Exception as auth_error:
            flash(f"认证失败: {str(auth_error)}", "warning")
            return render_template('course_selection.html', 
                                 categories=[], 
                                 selected_courses=selected_courses,
                                 time_info={})
    
    except Exception as e:
        flash(f"系统错误: {str(e)}", "error")
        return render_template('error.html', message=str(e))

@app.route('/api/courses/<category_code>')
def get_courses_api(category_code):
    """API: 获取指定类别的课程列表"""
    try:
        config = load_config()
        headers = get_headers(config["COOKIES"])
        time_info = get_time_info(headers)
        
        # 找到对应的类别
        categories = get_course_categories(time_info, headers)
        category = next((cat for cat in categories if cat['code'] == category_code), None)
        
        if not category:
            return jsonify({"error": "课程类别不存在"}), 404
        
        keyword = request.args.get('keyword', '')
        courses = get_courses(category, time_info, headers, keyword)
        
        return jsonify({"courses": courses, "category": category})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/courses/select', methods=['POST'])
def select_course():
    """API: 选择课程"""
    try:
        course_data = request.json
        selected_courses = load_existing_courses()
        
        # 检查课程是否已选择
        if any(course['id'] == course_data['id'] for course in selected_courses):
            return jsonify({"error": "课程已在选课列表中"}), 400
        
        # 添加到选课列表
        selected_courses.append(course_data)
        
        # 保存
        config = load_config()
        headers = get_headers(config["COOKIES"])
        save_results(config, headers, selected_courses)
        
        return jsonify({"message": "课程已添加到选课列表", "selected_courses": selected_courses})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/courses/remove', methods=['POST'])
def remove_course():
    """API: 从选课列表中移除课程"""
    try:
        course_id = request.json.get('course_id')
        selected_courses = load_existing_courses()
        
        # 移除课程
        selected_courses = [course for course in selected_courses if course['id'] != course_id]
        
        # 保存
        config = load_config()
        headers = get_headers(config["COOKIES"])
        save_results(config, headers, selected_courses)
        
        return jsonify({"message": "课程已从选课列表中移除", "selected_courses": selected_courses})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/selected')
def selected_courses():
    """查看已选课程页面"""
    try:
        courses = load_existing_courses()
        return render_template('selected_courses.html', courses=courses)
    except Exception as e:
        flash(f"加载已选课程失败: {str(e)}", "error")
        return render_template('error.html', message=str(e))

@app.route('/config')
def config_page():
    """配置页面"""
    try:
        config = {}
        if os.path.exists('.env'):
            # Load config without trying to authenticate
            from dotenv import dotenv_values
            config = dotenv_values('.env')
            config = {k: v for k, v in config.items() if v is not None}
        return render_template('config.html', config=config)
    except Exception as e:
        flash(f"加载配置失败: {str(e)}", "error")
        return render_template('error.html', message=str(e))

@app.route('/api/config', methods=['POST'])
def save_config():
    """API: 保存配置"""
    try:
        config_data = request.json
        
        # 写入 .env 文件
        with open('.env', 'w') as f:
            for key, value in config_data.items():
                f.write(f'{key}="{value}"\n')
        
        return jsonify({"message": "配置已保存"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/courses/selected-count')
def get_selected_count():
    """API: 获取已选课程数量"""
    try:
        courses = load_existing_courses()
        return jsonify({"count": len(courses)})
    except Exception as e:
        return jsonify({"count": 0, "error": str(e)})

@app.route('/api/test-connection')
def test_connection():
    """API: 测试连接"""
    try:
        config = load_config()
        headers = get_headers(config["COOKIES"])
        time_info = get_time_info(headers)
        
        if time_info:
            return jsonify({"message": "连接成功", "time_info": time_info})
        else:
            return jsonify({"error": "无法获取时间信息"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    """启动 Web 服务器"""
    print(Fore.GREEN + "🎯 HITCourseHunter Web UI" + Fore.RESET)
    print(Fore.CYAN + "启动 Web 服务器..." + Fore.RESET)
    print(Fore.YELLOW + "请在浏览器中打开: http://localhost:5000" + Fore.RESET)
    
    try:
        run_simple('localhost', 5000, app, use_reloader=True, use_debugger=True)
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n正在退出..." + Fore.RESET)

if __name__ == "__main__":
    main()