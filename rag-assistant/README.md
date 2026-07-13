# P1 · 本地知识库 RAG 助手(详细版脚手架)

![rag-assistant tests](https://github.com/gxucode/ai-portfolio/actions/workflows/tests.yml/badge.svg)

一个完全跑在你本机(M4 Mac)的检索增强(RAG)问答应用:把文档丢进去,问问题,它基于文档回答并附引用来源。不调任何云端 API,模型和数据都在本地。

## 它到底在做什么(原理一分钟)

普通大模型"记不住"你的私有文档。RAG 的解法是:先把文档切块、向量化存进向量库;你提问时,先把问题也向量化,去库里找出最相关的几块,再把这些块和问题一起塞给模型,让模型"照着资料回答"。

```
你的文档  ──切块──> 向量化 ──> Chroma 向量库(./storage)
                                      │
你的问题  ──向量化──> 检索 Top-K 相关块 ─┘
                                      │
                          拼成 Prompt ─> 本地 LLM ─> 带引用的回答
```

所以 RAG = 检索(找资料) + 生成(照资料答)。数据从不离开你的电脑。

## 目录结构

```
rag-assistant/
├── config.py        # 集中配置:模型名、路径、分块/检索参数
├── ingest.py        # 建索引(离线):文档→切块→向量化→Chroma
├── app.py           # 问答网页(在线):提问→检索→带引用回答
├── eval.py          # 可选:用 RAGAS 量化评估质量
├── requirements.txt # Python 依赖
├── data/            # 放你的文档(已含 sample.md 示例)
├── storage/         # 向量库持久化(跑 ingest.py 后生成)
└── README.md        # 本文件
```

## 难度自评(诚实版)

| 环节 | 难度 | 说明 |
|------|------|------|
| 装 Ollama + 拉模型 | 易 | 两行命令,模型几百 MB~几 GB |
| 装 Python 依赖 | 易 | `pip install -r requirements.txt` |
| 读/改代码 | 中 | 已写详细注释,照着读能懂原理 |
| 跑通第一个问答 | 易 | `python ingest.py` + `streamlit run app.py` |
| 调效果(分块/检索/评估) | 中 | 进阶可玩,不影响先跑起来 |

结论:对会一点 Python、能在终端敲命令的人,**从零到看到网页问答约 20~40 分钟**。唯一可能卡住新手的是"环境装没装对",代码逻辑本身是被 LlamaIndex / Chroma / Streamlit 高度封装的标准动作。

## 一、前置(只做一次)

```bash
# 1. 装 Ollama(本地模型运行时)
brew install ollama
ollama serve &            # 后台启动,Ollama 默认地址 http://localhost:11434

# 2. 拉两个本地模型
ollama pull qwen2.5:1.5b       # 中文问答模型(约 1GB,小而够用)
ollama pull nomic-embed-text  # 向量化模型(把文字变成向量)
```

> 模型大小怎么选:
> - **想更轻量 / 最快**:`ollama pull qwen2.5:0.5b`(约 0.4GB),再把 config.py 里 `LLM_MODEL` 改成 `"qwen2.5:0.5b"`。适合纯验证流程、内存极紧。
> - **想要更强**:`ollama pull qwen2.5:7b`,再把 `LLM_MODEL` 改掉(16GB 内存下 7B 也能跑,但偏紧)。
> 本项目默认 `1.5b`,是速度与质量在 M4/16G 上的平衡点。

## 二、运行(四步)

```bash
cd rag-assistant
pip install -r requirements.txt     # 1. 装依赖
python ingest.py                    # 2. 建索引(把 ./data 变成向量库,跑一次)
streamlit run app.py                # 3. 启动网页
# 4. 浏览器打开 http://localhost:8501
```

打开后直接问,例如:"知识蒸馏里的暗知识是什么?"——它会基于 data/sample.md 回答,并在下方列出引用来源(可展开看具体文本和相似度分数)。

## 三、换成你自己的资料

把你的 PDF / Markdown / 文本丢进 `./data/`,删掉或保留 sample.md 都行,然后重跑 `python ingest.py` 重建索引即可。

## 四、调优(改 config.py)

| 参数 | 作用 | 怎么调 |
|------|------|--------|
| CHUNK_SIZE | 每块大小 | 文档句子长就调大(如 768),短就调小(如 256) |
| CHUNK_OVERLAP | 块间重叠 | 一般取 CHUNK_SIZE 的 10%~20% |
| TOP_K | 每次取几块 | 答案需要多资料就调大;太大会引入噪声 |
| LLM_MODEL | 生成模型 | 想要更强换 3b/7b;想要更快换 0.5b |

## 四点五、测试(pytest,建议每次改代码后跑)

本项目带三层测试,详见 **TESTING.md**:
- L1 冒烟(`tests/test_config.py`):配置/参数合法性,无需模型,毫秒级
- L2 集成(`tests/test_chunking.py`):分块逻辑,无需模型,秒级
- L3 端到端(`tests/test_retrieval_e2e.py`):真实检索链路,需 Ollama+索引

```bash
pip install pytest
pytest -m "not e2e" -v     # 无依赖快测(改代码时高频跑)
pytest -v                  # 全部(含端到端,需先 ingest)
```

## 五、评估(可选,跑 eval.py)

凭感觉判断 RAG 好坏不靠谱,用 RAGAS 量化:

```bash
pip install ragas datasets
# 把 eval.py 里的 TEST_QUESTIONS 换成你关心的问题,然后:
python eval.py
```

会输出四个指标:faithfulness(答案是否忠于资料,最重要)、answer_relevancy(是否切题)、context_precision(检索精度)、context_recall(检索召回)。

## 常见问题

- **`connection refused` / 连不上 Ollama**:Ollama 没启动,先 `ollama serve &`。
- **首次回答很慢**:模型在冷加载,之后会快很多。
- **`module not found`**:没在 rag-assistant 目录装依赖,确认 `pip install -r requirements.txt` 已跑。
- **换成更大模型后卡顿**:16GB 内存跑 7B 已偏紧,可换回 1.5b 或用量化版。

## 下一步

跑通 P1 后,阶段一还有 P2(多工具 Agent),以及阶段二的 Colab 微调。每一步都可以继续照这个"脚手架"模式推进。
