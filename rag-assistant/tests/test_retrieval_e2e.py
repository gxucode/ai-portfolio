"""
L3 端到端测试 · 真实检索链路(需要 Ollama + 已建索引)
==================================================
这一层验证"从提问到检索到答案"整条链路真的通。
【前置】:
  1) Ollama 在跑,且已 pull qwen2.5:1.5b + nomic-embed-text
  2) 已跑过 python ingest.py(./storage 里有向量库)

若前置不满足,测试会被自动 skip(而非 fail),便于在无模型的 CI 里安全运行。

跑法:
  pytest tests/test_retrieval_e2e.py -v -m e2e
==================================================
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

pytestmark = pytest.mark.e2e  # 用标记隔离,默认可 -m "not e2e" 跳过


def _storage_ready() -> bool:
    return os.path.isdir(config.STORAGE_DIR) and bool(os.listdir(config.STORAGE_DIR))


@pytest.fixture(scope="module")
def query_engine():
    """构造真实查询引擎;缺依赖或缺索引则 skip。"""
    if not _storage_ready():
        pytest.skip("未检测到向量库,请先运行 python ingest.py")
    pytest.importorskip("chromadb")
    pytest.importorskip("llama_index.vector_stores.chroma")

    import chromadb
    from llama_index.core import Settings, VectorStoreIndex
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.llms.ollama import Ollama
    from llama_index.vector_stores.chroma import ChromaVectorStore

    Settings.llm = Ollama(model=config.LLM_MODEL, base_url=config.OLLAMA_BASE)
    Settings.embed_model = OllamaEmbedding(model_name=config.EMBED_MODEL, base_url=config.OLLAMA_BASE)

    try:
        col = chromadb.PersistentClient(path=config.STORAGE_DIR).get_collection(config.COLLECTION)
    except Exception as e:  # 集合不存在等
        pytest.skip(f"无法打开向量库集合: {e}")

    store = ChromaVectorStore(chroma_collection=col)
    return VectorStoreIndex.from_vector_store(store).as_query_engine(similarity_top_k=config.TOP_K)


def test_query_returns_non_empty(query_engine):
    """核心断言:真实提问不应返回 Empty Response(踩过的坑)。"""
    r = query_engine.query("知识蒸馏里的暗知识是什么?")
    assert r.response and "Empty Response" not in str(r.response)


def test_query_has_source_citations(query_engine):
    """RAG 的价值在于带引用:回答必须附至少一个来源块。"""
    r = query_engine.query("知识蒸馏里的暗知识是什么?")
    assert len(r.source_nodes) >= 1, "回答未附任何引用来源,RAG 检索可能失效"


def test_retrieval_respects_top_k(query_engine):
    """检索到的块数不应超过配置的 TOP_K。"""
    r = query_engine.query("温度参数 T 在蒸馏里起什么作用?")
    assert len(r.source_nodes) <= config.TOP_K
