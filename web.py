#!/usr/bin/env python3
"""
Quick launcher for HITCourseHunter Web UI
"""

import sys
import os

def main():
    """Launch the web interface directly"""
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from app import main as run_web_app
        print("🎯 HITCourseHunter Web UI")
        print("正在启动Web界面...")
        print("请在浏览器中打开: http://localhost:5000")
        print("按 Ctrl+C 停止服务器")
        print()
        run_web_app()
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装依赖: pip install flask")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 再见!")
        sys.exit(0)

if __name__ == "__main__":
    main()