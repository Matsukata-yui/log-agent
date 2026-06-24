"""命令行入口。用法: python cli.py --log /var/log/auth.log"""
import argparse
from src.log_agent.agent import run_agent

def main():
    parser = argparse.ArgumentParser(description="AI 日志分析 Agent (Ollama 本地版)")
    parser.add_argument("--log", required=True, help="日志文件路径")
    parser.add_argument("--model", default="qwen2.5:7b", help="Ollama 模型名")
    args = parser.parse_args()

    print(f"正在分析 {args.log} ...\n")
    report = run_agent(args.log, model=args.model)
    print(report)

if __name__ == "__main__":
    main()
