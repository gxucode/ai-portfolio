"""
P1 · 建索引 ingest.py
==================================================
把 ./data 下的文档变成"可语义检索"的本地向量库。

对应 RAG 的【离线建库】阶段,四步:
  ① 加载文档  →  ② 切分(分块)  →  ③ 向量化(Embedding)  →  ④ 写入 Chroma 持久化库

只需运行一次;之后文档有变动,重跑本脚本即可(会自动重建集合,不会重复追加)。
前置:Ollama 已启动,且已拉取 qwen2.5:3b 与 nomic-embed-text。
==================================================
"""
import os
import sys

import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

import config

# ---------- 绑定本地模型(全局设置) ----------
# 之后 LlamaIndex 所有的检索/生成都走本地 Ollama;
# 在 M4 上 torch 自动走 MPS 加速,不吃独立显卡显存。
Settings.llm = Ollama(model=config.LLM_MODEL, base_url=config.OLLAMA_BASE)
Settings.embed_model = OllamaEmbedding(model_name=config.EMBED_MODEL, base_url=config.OLLAMA_BASE)


def build_index():
    # ---------- ① 加载文档 ----------
    print(f"[1/4] 读取文档目录: {config.DATA_DIR}")
    if not os.path.isdir(config.DATA_DIR) or not os.listdir(config.DATA_DIR):
        print("  ✗ 没找到任何文档,请先往 ./data 放 PDF / Markdown / 文本文件")
        sys.exit(1)
    raw_docs = SimpleDirectoryReader(config.DATA_DIR).load_data()
    print(f"  ✓ 读到 {len(raw_docs)} 个源文件")

    # ---------- ② 切分(分块)——RAG 质量的关键一步 ----------
    # 为什么切块?向量库是按"块"检索的:
    #   块太大 → 检索不精准、塞进上下文浪费 token;
    #   块太小 → 切断语义、丢上下文。
    # SentenceSplitter 按"句子边界"切,比按固定字数硬切更自然;
    # overlap 让相邻块有重叠,避免一句话被切断后前后接不上。
    print(f"[2/4] 切分文档 (chunk_size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP})")
    parser = SentenceSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    nodes = parser.get_nodes_from_documents(raw_docs)
    print(f"  ✓ 切成 {len(nodes)} 个块(node)")

    # ---------- ③+④ 向量化并写入 Chroma ----------
    print("[3/4] 向量化并写入本地向量库 ...")
    client = chromadb.PersistentClient(path=config.STORAGE_DIR)
    # 重跑时先删旧集合,保证干净(否则会追加重复内容)
    if config.COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(config.COLLECTION)
    store = ChromaVectorStore(chroma_collection=client.get_or_create_collection(config.COLLECTION))

    # 必须用 StorageContext 显式绑定 vector_store,节点才会真正写入 Chroma 持久库;
    # 仅传 vector_store= 参数在新版 LlamaIndex 下不生效(数据只落内存,查询会 Empty Response)
    storage_context = StorageContext.from_defaults(vector_store=store)
    VectorStoreIndex(nodes, storage_context=storage_context, show_progress=True)
    print(f"[4/4] ✓ 索引构建完成,向量库已存到 {config.STORAGE_DIR}")


if __name__ == "__main__":
    build_index()
