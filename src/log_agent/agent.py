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
        f"{line}  →  {desc}" for line, desc in anomalies
    ) if anomalies else "未检测到已知异常特征"

    prompt = f"""你是一个安全日志分析 Agent。请基于以下日志和规则引擎扫描结果生成 Markdown 报告。

日志：
{log_content[:2000]}

扫描结果：
{anomaly_lines}

输出格式：## 分析概览 / ## 异常详情 / ## 风险评估 / ## 建议措施。中文。"""

    print(f"[调试] prompt长度: {len(prompt)} 字符")

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    msg = response.choices[0].message
    print(f"[调试] finish_reason: {response.choices[0].finish_reason}")
    print(f"[调试] content长度: {len(msg.content or '')}")

    report = msg.content or ""

    if not report:
        return "模型未返回任何内容，请检查 Ollama 是否正常运行。"

    write_func, _ = TOOL_REGISTRY["write_report"]
    write_func(content=report)

    return report
