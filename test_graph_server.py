#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的测试服务器，只提供图形API
"""

import json
import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources=r'/*')

@app.route('/graph/', methods=['GET'])
def graph():
    # 尝试加载CCUS知识图谱数据，如果不存在则使用原始数据
    ccus_data_path = 'data/ccus_data.json'
    fallback_data_path = 'data/data.json'

    if os.path.exists(ccus_data_path):
        with open(ccus_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        message = 'CCUS Knowledge Graph Loaded!'
    else:
        with open(fallback_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        message = 'Fallback Data Loaded!'

    return jsonify({
        'data': data,
        'message': message
    })

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Test Graph Server Running!"})

if __name__ == '__main__':
    print("🚀 Starting test graph server...")
    app.run(host='0.0.0.0', port=8002, debug=False)