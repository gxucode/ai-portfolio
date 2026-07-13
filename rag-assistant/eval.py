"""
P1 · 评估 eval.py(可选进阶)
==================================================
用 RAGAS 框架量化 RAG 系统的质量,而不是"凭感觉好不好"。

四个常用指标:
  - faithfulness(忠实度)   :答案是否完全基于检索到的内容,没胡编(最重要)
  - answer_relevancy(相关性):答案是否切题、有用
  - context_precision(精度):检索到的块里,相关的排得靠前吗
  - context_recall(召回)   :该检索到的内容,是否都检到了

前置: pip install ragas datasets
然后把下面的 TEST_QUESTIONS 换成你自己的问题,运行: python eval.py
==================================================
"""
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

import config

Settings.llm = Ollama(model=config.LLM_MODEL, base_url=config.OLLAMA_BASE)
Settings.embed_model = OllamaEmbedding(model_name=config.EMBED_MODEL, base_url=config.OLLAMA_BASE)


def answer_and_contexts(question: str):
    """跑一次问答,返回 (答案, 检索到的文本块列表)。"""
    store = ChromaVectorStore(
        chroma_collection=chromadb.PersistentClient(path=config.STORAGE_DIR)
        .get_collection(config.COLLECTION)
    )
    engine = VectorStoreIndex.from_vector_store(store).as_query_engine(
        similarity_top_k=config.TOP_K, response_mode="compact"
    )
    r = engine.query(question)
    return r.response, [n.get_content() for n in r.source_nodes]


# ↓↓↓ 换成你真正关心的问题 ↓↓↓
TEST_QUESTIONS = [
    "知识蒸馏里的暗知识是什么?",
    "温度参数 T 在蒸馏里起什么作用?",
    "大模型时代的蒸馏主要有哪几种玩法?",
]

questions, answers, contexts = [], [], []
for q in TEST_QUESTIONS:
    a, c = answer_and_contexts(q)
    questions.append(q)
    answers.append(a)
    contexts.append(c)

data = Dataset.from_dict({
    "question": questions,
    "answer": answers,
    "contexts": contexts,
})
result = evaluate(
    data,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
)
print(result)
