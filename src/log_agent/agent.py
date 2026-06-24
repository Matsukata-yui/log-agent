from openai import OpenAI
from .tools import TOOL_REGISTRY
from .rules import ALL_RULES

def run_agent(log_path: str, model: str = "qwen2.5:3b") -> str:
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        timeout=120,
    )

    read_func, _ = TOOL_REGISTRY["read_log_file"]
    log_content = read_func(path=log_path)

    anomalies = []
    for line in log_content.split("\n"):
        line = line.strip()
        if not line:
            continue
        for rule in ALL_RULES:
            result = rule(line)
            if result:
                anomalies.append((line, result))
                break

    anomaly_lines = "\n".join(
        f"{line[:120]}  →  {desc}" for line, desc in anomalies
    ) if anomalies else "未检测到已知异常特征"

    total_lines = len(log_content.splitlines())
    total_anomalies = len(anomalies)

    type_count = {}
    for _, desc in anomalies:
        cat = desc.split("→")[0].strip()
        type_count[cat] = type_count.get(cat, 0) + 1

    stats = "\n".join(f"- {k}: {v} 条" for k, v in type_count.items())

    prompt = f"""你是安全日志分析 Agent。规则引擎已做预筛选：常规运维命令（apt/mkd/reboot/systemctl/vim/git 等）已从异常列表中剔除，你看到的都是需要关注的条目。

请生成 Markdown 报告：

日志总量: {total_lines} 行
待关注异常: {total_anomalies} 条
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

    if not report:
        return "模型无输出"

    write_func, _ = TOOL_REGISTRY["write_report"]
    write_func(content=report)

    return report
