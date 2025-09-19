#!/usr/bin/env python3
"""
Simplified test server to debug the issue
"""

import sys
import os
sys.path.append('server')

from flask import Flask, Response, request
import json

app = Flask(__name__)

@app.route('/chat/', methods=['GET'])
def chat_get():
    return "Test Chat API is working!"

@app.route('/chat/', methods=['POST'])
def chat_test():
    try:
        request_data = json.loads(request.data)
        query = request_data.get('query', 'No query provided')

        # Simple test response
        result = {
            "history": [[query, f"Test response for: {query}"]],
            "updates": {
                "query": query,
                "response": f"Test response for: {query}"
            },
            "image": None,
            "graph": {},
            "wiki": {"title": "测试", "summary": "测试响应"},
            "entity_details": [],
            "suggestions": [],
            "conversation_summary": None
        }

        return Response(
            response=json.dumps(result, ensure_ascii=False).encode('utf8'),
            content_type='application/json',
            status=200
        )

    except Exception as e:
        return Response(
            response=json.dumps({"error": str(e)}, ensure_ascii=False).encode('utf8'),
            content_type='application/json',
            status=500
        )

if __name__ == '__main__':
    print("🧪 Starting test server on port 8000...")
    app.run(host='0.0.0.0', port=8000, debug=False)