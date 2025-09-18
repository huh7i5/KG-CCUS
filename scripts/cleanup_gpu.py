#!/usr/bin/env python3
"""
智能GPU内存清理脚本
在启动新的模型之前清理GPU内存，避免冲突
"""

import os
import sys
import subprocess
import signal
import time
import re

def get_gpu_processes():
    """获取占用GPU的进程信息"""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ nvidia-smi 命令失败，可能没有安装NVIDIA驱动")
            return []

        output = result.stdout
        processes = []

        # 解析nvidia-smi输出，提取进程信息
        lines = output.split('\n')
        in_process_section = False

        for line in lines:
            if 'Processes:' in line:
                in_process_section = True
                continue

            if in_process_section and '|' in line:
                # 匹配进程行: |    0   N/A  N/A      PID      C   python3        Memory |
                match = re.search(r'\|\s+\d+\s+\S+\s+\S+\s+(\d+)\s+\S+\s+(\S+)\s+(\d+)MiB', line)
                if match:
                    pid = int(match.group(1))
                    process_name = match.group(2)
                    memory_mb = int(match.group(3))
                    processes.append({
                        'pid': pid,
                        'name': process_name,
                        'memory_mb': memory_mb
                    })

        return processes

    except Exception as e:
        print(f"❌ 获取GPU进程信息失败: {e}")
        return []

def is_safe_to_kill(pid, process_name):
    """判断进程是否可以安全终止"""
    try:
        # 检查进程是否存在
        os.kill(pid, 0)

        # 获取进程详细信息
        result = subprocess.run(['ps', '-p', str(pid), '-o', 'cmd='],
                              capture_output=True, text=True)

        if result.returncode != 0:
            return False, "进程不存在"

        cmd_line = result.stdout.strip()

        # 安全终止的条件
        safe_patterns = [
            'python3 main.py',          # 我们的主程序
            'python.*chatglm',          # ChatGLM相关
            'python.*torch',            # PyTorch相关
            'jupyter',                  # Jupyter进程（通常可以重启）
        ]

        # 不应该终止的进程
        unsafe_patterns = [
            'systemd',                  # 系统进程
            '/usr/bin',                 # 系统命令
            'nvidia-smi',               # NVIDIA工具
        ]

        # 检查是否为不安全进程
        for pattern in unsafe_patterns:
            if re.search(pattern, cmd_line, re.IGNORECASE):
                return False, f"系统关键进程: {pattern}"

        # 检查是否为可安全终止的进程
        for pattern in safe_patterns:
            if re.search(pattern, cmd_line, re.IGNORECASE):
                return True, f"匹配安全模式: {pattern}"

        return False, f"未知进程类型: {cmd_line[:50]}..."

    except ProcessLookupError:
        return False, "进程不存在"
    except PermissionError:
        return False, "权限不足"
    except Exception as e:
        return False, f"检查失败: {e}"

def kill_process_safely(pid, process_name):
    """安全地终止进程"""
    try:
        print(f"🔄 正在终止进程 {pid} ({process_name})...")

        # 首先尝试优雅终止 (SIGTERM)
        os.kill(pid, signal.SIGTERM)

        # 等待进程退出
        for i in range(5):
            time.sleep(1)
            try:
                os.kill(pid, 0)  # 检查进程是否还存在
            except ProcessLookupError:
                print(f"✅ 进程 {pid} 已优雅退出")
                return True

        # 如果还没退出，强制终止 (SIGKILL)
        print(f"⚠️  进程 {pid} 未响应SIGTERM，使用SIGKILL强制终止...")
        os.kill(pid, signal.SIGKILL)

        time.sleep(1)
        try:
            os.kill(pid, 0)
            print(f"❌ 进程 {pid} 仍在运行")
            return False
        except ProcessLookupError:
            print(f"✅ 进程 {pid} 已强制终止")
            return True

    except ProcessLookupError:
        print(f"✅ 进程 {pid} 已不存在")
        return True
    except PermissionError:
        print(f"❌ 权限不足，无法终止进程 {pid}")
        return False
    except Exception as e:
        print(f"❌ 终止进程 {pid} 失败: {e}")
        return False

def clear_gpu_cache():
    """清理GPU缓存"""
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            print("🧹 PyTorch GPU缓存已清理")
    except ImportError:
        print("ℹ️  PyTorch未安装，跳过GPU缓存清理")
    except Exception as e:
        print(f"⚠️  GPU缓存清理失败: {e}")

def main():
    """主函数"""
    print("🚀 开始GPU内存清理...")

    # 获取GPU进程列表
    gpu_processes = get_gpu_processes()

    if not gpu_processes:
        print("✅ 未发现占用GPU的进程")
        clear_gpu_cache()
        return True

    print(f"📋 发现 {len(gpu_processes)} 个GPU进程:")
    for proc in gpu_processes:
        print(f"  - PID {proc['pid']}: {proc['name']} ({proc['memory_mb']}MB)")

    # 分析和处理每个进程
    killed_count = 0
    total_freed_memory = 0

    for proc in gpu_processes:
        pid = proc['pid']
        name = proc['name']
        memory_mb = proc['memory_mb']

        # 检查是否可以安全终止
        can_kill, reason = is_safe_to_kill(pid, name)

        if can_kill:
            print(f"\n🎯 准备终止进程 {pid} ({name}) - {reason}")

            if kill_process_safely(pid, name):
                killed_count += 1
                total_freed_memory += memory_mb
                print(f"💾 释放了 {memory_mb}MB GPU内存")
            else:
                print(f"❌ 终止进程 {pid} 失败")
        else:
            print(f"\n⚠️  跳过进程 {pid} ({name}) - {reason}")

    # 最终清理GPU缓存
    clear_gpu_cache()

    # 等待一下让GPU状态稳定
    print("\n⏳ 等待GPU状态稳定...")
    time.sleep(2)

    print(f"\n📊 清理完成:")
    print(f"  - 终止了 {killed_count} 个进程")
    print(f"  - 释放了 {total_freed_memory}MB GPU内存")

    # 显示最终GPU状态
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            used, total = result.stdout.strip().split(', ')
            print(f"  - 当前GPU内存: {used}MB / {total}MB")
    except:
        pass

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 清理过程出错: {e}")
        sys.exit(1)