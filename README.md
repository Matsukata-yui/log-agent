# Log Agent

基于 LLM 的安全日志分析 Agent。先由规则引擎提取异常特征，再由本地 Ollama 模型生成结构化安全报告。

## 快速开始

### 环境要求
- Ubuntu 22.04
- Python 3.10+
- 4GB+ 内存
- Ollama + qwen2.5:3b

### 安装

```bash
# 安装 Ollama 并拉模型
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:3b

# 安装项目依赖
git clone https://github.com/你的用户名/log-agent.git
cd log-agent
uv sync

