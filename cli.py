"""命令行入口。用法: python cli.py --log /var/log/auth.log"""
import argparse
import time
from src.log_agent.agent import run_agent

def main():
    parser = argparse.ArgumentParser(description="AI 日志分析 Agent (Ollama 本地版)")
    parser.add_argument("--log", required=True, help="日志文件路径")
    parser.add_argument("--model", default="qwen2.5:3b", help="Ollama 模型名")
    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"  日志分析 Agent")
    print(f"  目标: {args.log}")
    print(f"  模型: {args.model}")
    print(f"{'='*50}\n")

    t_start = time.time()
    report = run_agent(args.log, model=args.model)

    print(f"\n{'='*50}")
    print(f"  总耗时: {time.time() - t_start:.1f}s")
    print(f"{'='*50}\n")

    print(report)

if __name__ == "__main__":
    main()
