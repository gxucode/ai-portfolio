# P1 RAG 助手 · 测试文档（TESTING.md）

> 目的：说明这个项目**怎么测、测什么、测出来算通过**。
> RAG 系统的测试和普通 CRUD 应用不同——它有两类完全不同的质量：
> **① 工程正确性**（代码逻辑对不对）和 **② 回答质量**（答得准不准）。
> 本项目对两者都有覆盖，且按「是否需要模型」分层，方便在无 GPU 的 CI 里也能跑一部分。

---

## 0. 测试全景（一张表看懂）

| 层级 | 测什么 | 需要 Ollama？ | 需要索引？ | 速度 | 文件 |
|------|--------|:---:|:---:|------|------|
| **L1 冒烟** | 配置/参数合法性 | 否 | 否 | 毫秒级 | `tests/test_config.py` |
| **L2 集成** | 分块逻辑（切分/重叠/边界） | 否 | 否 | 秒级 | `tests/test_chunking.py` |
| **L3 端到端** | 真实检索链路（提问→引用→答案） | ✅ | ✅ | 分钟级 | `tests/test_retrieval_e2e.py` |
| **Q 质量评估** | 回答忠实度/相关性/检索精召 | ✅ | ✅ | 分钟级 | `eval.py`（RAGAS） |

设计原则：**越底层越快、越无依赖**。改代码时先跑 L1+L2 秒级验证，提交前再跑 L3+Q。

---

## 1. 快速开始

```bash
cd /Users/xiaoman/WorkBuddy/2026-07-11-09-40-50/rag-assistant
pip install pytest                      # 仅测试需要

# 只跑无依赖的快测（L1+L2，秒级，改代码时高频跑）
pytest -m "not e2e" -v

# 跑全部（含 L3 端到端，需先 ollama serve + python ingest.py）
pytest -v
```

无 Ollama / 无索引时，L3 会**自动 skip 而非 fail**——这样在没有模型的环境里跑测试也是绿的，不会误报。

---

## 2. 三层工程测试详解

### L1 冒烟测试 · `tests/test_config.py`
防止改配置手滑。断言项：
- Chroma 集合名 ≥3 字符（**踩过的坑**：过短会 `InvalidArgumentError`）
- `CHUNK_OVERLAP < CHUNK_SIZE`（否则分块逻辑异常）
- overlap 占比落在推荐区间 5%~30%
- `TOP_K` 为正整数、模型名非空、`OLLAMA_BASE` 是合法 URL

### L2 集成测试 · `tests/test_chunking.py`
分块是 RAG 质量的关键，单独测它：
- 长文档能被切成多块
- 短文档只产生一块、不报错
- 空文档不崩溃
- 每个块都有非空内容

> 未装 `llama_index` 时本文件自动跳过，不拖累 L1。

### L3 端到端测试 · `tests/test_retrieval_e2e.py`（标记 `e2e`）
验证整条链路真的通：
- 真实提问**不返回 `Empty Response`**（**踩过的坑**：StorageContext 未绑定时数据只落内存）
- 回答**必附至少一个引用来源**（RAG 的核心价值）
- 检索块数不超过 `TOP_K`

---

## 3. 质量评估 · `eval.py`（RAGAS）

工程测试只能保证「代码没崩」，保证不了「答得好」。回答质量用 RAGAS 量化：

```bash
pip install ragas datasets
python eval.py
```

| 指标 | 含义 | 关注度 |
|------|------|--------|
| **faithfulness** | 答案是否完全基于检索内容、没胡编 | ⭐最重要 |
| answer_relevancy | 答案是否切题 | 高 |
| context_precision | 相关块是否排在前面 | 中 |
| context_recall | 该检索到的是否都检到了 | 中 |

**参考基线**（qwen2.5:1.5b + sample.md，仅供自比，非行业标准）：
faithfulness ≥ 0.80 视为健康；明显低于说明模型在「照资料答」上不稳，可换更大模型或收紧生成约束。

---

## 4. 人工验收清单（Demo / 面试前自查）

- [ ] `ollama serve` 在跑，`ollama list` 能看到两个模型
- [ ] `python ingest.py` 输出「索引构建完成」且 `./storage` 非空
- [ ] `streamlit run app.py`，浏览器问「知识蒸馏里的暗知识是什么？」
- [ ] 回答**基于 sample.md**，且下方**能展开引用来源**（含相似度分数）
- [ ] `pytest -m "not e2e"` 全绿
- [ ] （可选）`pytest -v` 端到端全绿 / `python eval.py` faithfulness ≥ 0.80

---

## 5. 已知边界 & 下一步（诚实版）

当前测试**没有覆盖**、也是 P1 有意留到后续的：
- **混合检索**：现在只有向量检索，未测 BM25 关键词召回补漏。
- **超时 / 兜底**：未测 Ollama 挂掉、超长文档、并发请求下的降级行为。

> 这些不是「不成熟」，而是分阶段：P1 的目标是跑通 + 可评估；
> 生产级健壮性（可观测、灰度）属于阶段③作品集打磨。把「边界」写清，
> 本身就是工程成熟度的信号——知道自己缺什么，比假装什么都有更专业。

## 6. CI 自动化（已接入 ✅）

已通过 GitHub Actions 做**每次提交自动回归**：

- 工作流：`.github/workflows/tests.yml`
- 触发：推送 / PR 改动 `rag-assistant/**` 时自动运行
- 环境：ubuntu-latest + Python 3.11，装 `requirements-tests.txt`（精简依赖，不含 torch/streamlit）
- 结果：L1 配置 + L2 分块**真跑通过**；L3 端到端因 CI 无 Ollama **自动 skip**（不报错、不误红）
- 状态徽章见 README 顶部 `tests` badge

> 设计要点：CI 里没有 GPU / Ollama，靠 L3 的 `skip` 机制保证「在任何机器上都能绿」，
> 这正是「懂工程分层」的信号，而不是把没法跑的测试硬塞进 CI 让它常红。
