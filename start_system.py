#!/usr/bin/env python3
"""
ChatKG 系统启动脚本
自动检查和准备知识图谱数据，然后启动服务
"""

import os
import sys
import subprocess
import json

def check_knowledge_graph():
    """检查知识图谱数据是否就绪"""
    print("🔍 Checking knowledge graph data...")

    data_json_path = "data/data.json"
    if os.path.exists(data_json_path):
        try:
            with open(data_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                nodes = len(data.get('nodes', []))
                links = len(data.get('links', []))
                sents = len(data.get('sents', []))
                print(f"✅ Knowledge graph ready: {nodes} nodes, {links} links, {sents} sentences")
                return True
        except Exception as e:
            print(f"❌ Error reading data.json: {e}")

    print("📚 Knowledge graph not found, converting from SPN4RE format...")
    return convert_knowledge_graph()

def convert_knowledge_graph():
    """转换知识图谱格式"""
    try:
        from server.app.utils.kg_converter import convert_latest_kg_to_frontend
        result = convert_latest_kg_to_frontend()
        if result:
            print("✅ Knowledge graph conversion completed!")
            return True
        else:
            print("❌ Knowledge graph conversion failed!")
            return False
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False

def start_backend():
    """启动后端服务"""
    print("\n🚀 Starting backend server...")

    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.join(os.getcwd(), 'server')

    try:
        # 启动Flask应用
        os.chdir('server')
        subprocess.run([
            sys.executable, '-c',
            'from app import apps; apps.run(host="0.0.0.0", port=5000, debug=True)'
        ], env=env)
    except KeyboardInterrupt:
        print("\n⏹️  Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

def start_frontend():
    """启动前端服务"""
    print("\n🎨 To start frontend, run the following commands in another terminal:")
    print("cd chat-kg")
    print("npm install")
    print("npm run dev")

def main():
    """主函数"""
    print("=" * 60)
    print("🤖 ChatKG - Knowledge Graph Chat System")
    print("=" * 60)

    # 检查知识图谱
    if not check_knowledge_graph():
        print("❌ Failed to prepare knowledge graph data")
        return

    # 显示前端启动说明
    start_frontend()

    # 启动后端
    start_backend()

if __name__ == "__main__":
    main()