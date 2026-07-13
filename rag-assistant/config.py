"""P1 · 集中配置。

所有可调参数都放这里,改这一处即可,不用动业务逻辑。
环境变量 OLLAMA_BASE 可覆盖 Ollama 地址(默认本机)。
"""
import os

# Ollama 服务地址(本机默认即可;远程部署或改端口时改这里)
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")

# 模型名(必须在 Ollama 里先 pull 过)
LLM_MODEL = "qwen2.5:1.5b"        # 负责"读检索结果、生成答案"的对话模型(约 1GB;想更轻量用 qwen2.5:0.5b 约 0.4GB)
EMBED_MODEL = "nomic-embed-text"  # 负责"把文字变成向量"的 Embedding 模型

# 路径
DATA_DIR = "./data"      # 放原始文档的目录(PDF / Markdown / 文本)
STORAGE_DIR = "./storage"  # Chroma 向量库持久化目录(运行 ingest.py 后自动生成)
COLLECTION = "kb_docs"     # Chroma 集合名(≥3字符,否则 chroma 会报 InvalidArgumentError)

# 分块策略(直接决定检索质量,详见 ingest.py 注释)
CHUNK_SIZE = 512         # 每块约 512 token
CHUNK_OVERLAP = 64       # 相邻块重叠 64 token,保持上下文连续

# 检索
TOP_K = 4                # 每次问答取最相似的几个块送进模型
