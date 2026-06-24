"""异常检测规则。每条规则函数输入日志行，返回异常描述或 None。"""
import re

def detect_bruteforce(line: str) -> str | None:
    patterns = [
        r"Failed password for .+ from (\S+)",
        r"authentication failure.*rhost=(\S+)",
        r"Invalid user \S+ from (\S+)",
    ]
    for pat in patterns:
        m = re.search(pat, line, re.IGNORECASE)
        if m:
            return f"暴力破解尝试 → 来源 IP: {m.group(1)}"
    return None

def detect_privilege_escalation(line: str) -> str | None:
    if re.search(r"sudo:.*COMMAND=", line):
        cmd = re.search(r"COMMAND=(.+)", line)
        return f"sudo 提权执行 → {cmd.group(1) if cmd else '未知命令'}"
    if re.search(r"su:.*session opened", line):
        return "用户切换 (su) → 会话已打开"
    return None

def detect_web_attack(line: str) -> str | None:
    patterns = {
        r"(?i)(union\s+select)": "SQL 注入尝试",
        r"(?i)(<script|onerror=|onload=)": "XSS 攻击尝试",
        r"(?i)(\.\./|\.\.\\){2,}": "目录遍历攻击",
        r"(?i)(wget\s+|curl\s+|cmd=|system\()": "命令注入尝试",
        r"(?i)(/wp-admin|/wp-login|xmlrpc\.php)": "WordPress 扫描",
    }
    for pat, desc in patterns.items():
        if re.search(pat, line):
            return desc
    return None

def detect_scanning(line: str) -> str | None:
    if re.search(r"Did not receive identification string from", line):
        return "可疑连接探测（未完成 SSH 握手）"
    if re.search(r"Connection closed by .+ \[preauth\]", line):
        return "预认证阶段连接关闭（可能为扫描）"
    return None

ALL_RULES = [
    detect_bruteforce,
    detect_privilege_escalation,
    detect_web_attack,
    detect_scanning,
]
