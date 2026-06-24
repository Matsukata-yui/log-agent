"""Agent 可调用的工具函数。"""
from pathlib import Path

def read_log_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return f"错误：文件 {path} 不存在"
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    if len(lines) > 5000:
        lines = lines[-5000:]
        return f"文件过大，已截取最后 5000 行：\n" + "".join(lines)
    return "".join(lines)

def write_report(content: str) -> str:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    out_path = output_dir / "report.md"
    out_path.write_text(content, encoding="utf-8")
    return f"报告已写入 {out_path.resolve()}"

TOOL_REGISTRY = {
    "read_log_file": (read_log_file, "读取指定路径的日志文件内容"),
    "write_report":   (write_report, "将分析报告写入 output/report.md"),
}
