import sys
import time
from openai import OpenAI
from .tools import TOOL_REGISTRY
from .rules import ALL_RULES

def run_agent(log_path: str, model: str = "qwen2.5:3b") -> str:

    # ========== 阶段1：读文件 ==========
    print("[*] 正在读取日志文件...", end=" ", flush=True)
    t0 = time.time()
    read_func, _ = TOOL_REGISTRY["read_log_file"]
    log_content = read_func(path=log_path)
    lines_all = log_content.split("\n")
    total = len(lines_all)
    print(f"完成（{total} 行，{time.time()-t0:.1f}s）")

    # ========== 阶段2：规则扫描（带进度） ==========
    print("[*] 规则引擎扫描中...")
    anomalies = []
    tick_every = max(1, total // 20)  # 每 5% 更新一次进度

    for idx, line in enumerate(lines_all):
        line = line.strip()
        if not line:
            continue
        for rule in ALL_RULES:
            result = rule(line)
            if result:
                anomalies.append((line, result))
                break

        if (idx + 1) % tick_every == 0:
            pct = (idx + 1) * 100 // total
            bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
            sys.stdout.write(f"\r    [{bar}] {pct}%  已扫描 {idx+1}/{total} 行")
            sys.stdout.flush()

    sys.stdout.write(f"\r    [{'#'*20}] 100%  扫描完成，发现 {len(anomalies)} 条异常\n")
    sys.stdout.flush()

    if not anomalies:
        return "未检测到任何异常。"

    # 统计
    type_count = {}
    for _, desc in anomalies:
        cat = desc.split("→")[0].strip()
        type_count[cat] = type_count.get(cat, 0) + 1

    stats = "\n".join(f"- {k}: {v} 条" for k, v in type_count.items())
    anomaly_lines = "\n".join(
        f"{line[:120]}  →  {desc}" for line, desc in anomalies
    )

    # ========== 阶段3：LLM 报告生成 ==========
    print("[*] 正在调用 LLM 生成报告（可能需要 1~3 分钟）...", flush=True)
    t1 = time.time()

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        timeout=300,
    )

    prompt = f"""你是安全日志分析 Agent。规则引擎已做预筛选：常规运维命令（apt/mkdir/reboot/systemctl/vim/git 等）已从异常列表中剔除，你看到的都是需要关注的条目。

请生成 Markdown 报告：

日志总量: {total} 行
待关注异常: {len(anomalies)} 条
类型分布:
{stats}

明细（前 30 条）：
{chr(10).join(anomaly_lines.split(chr(10))[:30])}

报告结构：
## 分析概览（总行数、异常数、分布）
## 异常详情（按类型分组，标注时间与命令）
## 风险评估（高/中/低。注意：单个用户高频 sudo 若为安装软件等常规操作，不应定为高风险；关注非交互式提权、远程下载执行、权限滥用等真正异常）
## 建议措施（针对实际发现的问题，不说空话）

中文，只输出事实。"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    report = response.choices[0].message.content or ""
    print(f"    LLM 响应完成（{time.time()-t1:.1f}s）\n")

    if not report:
        return "LLM 无输出"

    # ========== 阶段4：写文件 ==========
    print("[*] 正在写入报告...", end=" ", flush=True)
    write_func, _ = TOOL_REGISTRY["write_report"]
    write_func(content=report)
    print("完成")

    return report
