"""
P1 · 问答界面 app.py
==================================================
Streamlit 网页:提问 → 检索 → 带引用回答。

对应 RAG 的【在线问答】阶段,五步:
  用户提问 → 问题向量化 → Chroma 检索 Top-K 相似块 → 拼进 Prompt → LLM 生成答案 → 展示(附引用)

运行: streamlit run app.py   (需先跑过 ingest.py 建好库)
==================================================
"""
import chromadb
import streamlit as st
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

import config

# 绑定本地模型
Settings.llm = Ollama(model=config.LLM_MODEL, base_url=config.OLLAMA_BASE)
Settings.embed_model = OllamaEmbedding(model_name=config.EMBED_MODEL, base_url=config.OLLAMA_BASE)


@st.cache_resource
def get_engine(top_k: int):
    """构造查询引擎。用 @st.cache_resource 缓存,避免每次提问都重连向量库。"""
    # 直接读已建好的向量库,跳过重新向量化,启动快
    store = ChromaVectorStore(
        chroma_collection=chromadb.PersistentClient(path=config.STORAGE_DIR)
        .get_collection(config.COLLECTION)
    )
    return VectorStoreIndex.from_vector_store(store).as_query_engine(similarity_top_k=top_k)


st.set_page_config(page_title="本地知识库问答")
st.title("本地知识库问答 (P1 详细版 RAG)")
st.caption("模型与数据全在本地 · 基于 ./data 文档回答,并附引用来源")

# 侧边栏:可调检索块数。Top-K 越大参考越多,但可能引入噪声
top_k = st.sidebar.slider("检索块数 Top-K", min_value=1, max_value=8, value=config.TOP_K)
st.sidebar.markdown(
    "Top-K 越大,送进模型的参考上下文越多;太小容易漏信息,太大容易混入无关内容。"
)

q = st.text_input("问点什么:")
if q:
    with st.spinner("正在检索并生成答案..."):
        r = get_engine(top_k).query(q)

    st.subheader("回答")
    st.write(r.response)

    # 引用来源:把每个检索到的块展开,方便核对答案是否真的来自文档
    st.divider()
    st.subheader(f"引用来源({len(r.source_nodes)} 块)")
    for i, n in enumerate(r.source_nodes, 1):
        score = getattr(n, "score", None)
        head = f"#{i}  相似度 {score:.3f}" if score is not None else f"#{i}"
        with st.expander(f"{head} · {n.metadata.get('file_path', '未知来源')}"):
            st.write(n.get_content())
