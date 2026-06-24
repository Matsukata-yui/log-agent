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
    """检测提权操作，排除正常运维命令"""
    if not re.search(r"sudo:.*COMMAND=", line):
        if re.search(r"su:.*session opened", line):
            return "用户切换 (su) → 会话已打开"
        return None

    cmd = re.search(r"COMMAND=(.+)", line)
    if not cmd:
        return None

    command = cmd.group(1).strip()

    # 白名单：正常的运维操作，不报警
    WHITELIST = [
        r"^/usr/bin/apt",
        r"^/usr/bin/mkdir",
        r"^/usr/sbin/reboot",
        r"^/usr/bin/su$",
        r"^/usr/bin/systemctl",
        r"^/usr/bin/journalctl",
        r"^/usr/bin/nano",
        r"^/usr/bin/vim",
        r"^/usr/bin/cat",
        r"^/usr/bin/ls",
        r"^/usr/bin/cp",
        r"^/usr/bin/mv",
        r"^/usr/bin/rm",
        r"^/usr/bin/chown",
        r"^/usr/bin/chmod",
        r"^/usr/bin/pip",
        r"^/usr/bin/python",
        r"^/usr/bin/git",
        r"^/usr/bin/curl",
        r"^/usr/bin/wget",
    ]

    for pat in WHITELIST:
        if re.match(pat, command):
            return None  # 正常运维，不放行到异常列表

    # 危险提权特征
    DANGER = [
        (r"chmod\s+777", "chmod 777 权限滥用"),
        (r"(wget|curl)\s+\S+\s*\|?\s*(sh|bash)", "远程脚本下载并执行"),
        (r"useradd|adduser", "新增用户"),
        (r"passwd", "修改密码"),
        (r"(iptables|ufw)\s+.*disable", "关闭防火墙"),
    ]

    for pat, desc in DANGER:
        if re.search(pat, command):
            return f"可疑提权行为 → {desc} ({command[:60]})"

    return f"sudo 提权执行 → {command[:60]}"  # 灰名单，不确定

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
