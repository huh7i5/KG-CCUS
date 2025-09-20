import os
from app import apps

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from app.utils.chat_glm import start_model


if __name__ == '__main__':
    import socket

    print("Starting model...")
    start_model()
    apps.secret_key = os.urandom(24)

    # 查找可用端口
    def find_free_port(start_port=5000):
        for port in range(start_port, start_port + 100):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('', port))
                    return port
                except OSError:
                    continue
        return None

    port = find_free_port(5000)
    if port:
        print(f"🚀 Starting server on port {port}")
        apps.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    else:
        print("❌ No available ports found")

