"""
L1 冒烟测试 · 配置与参数合法性
==================================================
这一层【不依赖 Ollama、不依赖模型、不联网】,毫秒级跑完。
作用:防止改配置时手滑引入低级错误(回归测试)。

跑法:
  cd rag-assistant
  pytest tests/test_config.py -v
==================================================
"""
import os
import sys

# 让测试能 import 到项目根的 config.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


def test_collection_name_valid():
    """Chroma 集合名必须 >=3 字符,否则运行时 InvalidArgumentError(踩过的坑)。"""
    assert isinstance(config.COLLECTION, str)
    assert len(config.COLLECTION) >= 3, "Chroma 集合名过短会在建库时报错"


def test_chunk_params_reasonable():
    """分块参数要合法:块大小为正,重叠必须小于块大小,否则切分逻辑异常。"""
    assert config.CHUNK_SIZE > 0
    assert config.CHUNK_OVERLAP >= 0
    assert config.CHUNK_OVERLAP < config.CHUNK_SIZE, "overlap 必须小于 chunk_size"


def test_overlap_within_recommended_range():
    """经验值:重叠取块大小的 5%~30% 较健康,超出给出明确失败信息。"""
    ratio = config.CHUNK_OVERLAP / config.CHUNK_SIZE
    assert 0.0 <= ratio <= 0.30, f"overlap 占比 {ratio:.0%} 偏离推荐区间 5%~30%"


def test_top_k_positive():
    """检索块数必须为正整数。"""
    assert isinstance(config.TOP_K, int)
    assert config.TOP_K >= 1


def test_model_names_present():
    """生成模型与向量模型名都不能为空(否则 Ollama 会连不上)。"""
    assert config.LLM_MODEL and isinstance(config.LLM_MODEL, str)
    assert config.EMBED_MODEL and isinstance(config.EMBED_MODEL, str)


def test_ollama_base_is_url():
    """Ollama 地址应是 http(s) 开头的 URL。"""
    assert config.OLLAMA_BASE.startswith("http"), "OLLAMA_BASE 必须是 http(s):// 开头"
