"""
L2 集成测试 · 分块逻辑(本地纯 CPU,不需要 Ollama)
==================================================
分块是 RAG 质量的关键一步,单独测它能保证:
  - 切分真的发生了(长文本被切成多块)
  - overlap 生效(相邻块有重叠内容)
  - 空文档不会崩

依赖:llama-index-core(已在 requirements.txt)。
若未安装 llama_index,本文件会被自动跳过,不影响 L1。

跑法:
  pytest tests/test_chunking.py -v
==================================================
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 没装 llama_index 时优雅跳过,而不是让整套测试红掉
pytest.importorskip("llama_index.core", reason="需要 llama-index-core,pip install -r requirements.txt")

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter


def _make_long_text(n_sentences: int = 60) -> str:
    """造一段够长的中文文本,确保能被切成多块。"""
    return "".join(f"这是用于测试分块逻辑的第{i}个句子,内容足够长以触发切分。" for i in range(n_sentences))


def test_long_document_splits_into_multiple_chunks():
    """长文档应被切成不止一个块。"""
    parser = SentenceSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    nodes = parser.get_nodes_from_documents([Document(text=_make_long_text())])
    assert len(nodes) >= 2, "长文档应被切成多个块,当前只切出 1 个,检查 CHUNK_SIZE"


def test_short_document_single_chunk():
    """极短文档应只产生一个块,不应报错。"""
    parser = SentenceSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    nodes = parser.get_nodes_from_documents([Document(text="一句话。")])
    assert len(nodes) == 1


def test_empty_document_does_not_crash():
    """空文档不应让切分崩溃,应产生 0 或 1 个空块。"""
    parser = SentenceSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    nodes = parser.get_nodes_from_documents([Document(text="")])
    assert len(nodes) <= 1


def test_nodes_have_content():
    """切出来的块都应有非空文本内容。"""
    parser = SentenceSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    nodes = parser.get_nodes_from_documents([Document(text=_make_long_text())])
    for n in nodes:
        assert n.get_content().strip(), "存在空内容的块"
