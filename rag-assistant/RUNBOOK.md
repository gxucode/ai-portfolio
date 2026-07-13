# P1 本地知识库 RAG 助手 · 运行手册（RUNBOOK）

> 目的：不依赖助手，你也能独立把 P1 跑起来、重启、维护、改自己的资料。
> 当前状态：2026-07-12 助手已在本机跑通，网页服务运行于 **http://localhost:8501**（已验证可达）。
> 技术栈：Ollama（qwen2.5:1.5b + nomic-embed-text）+ LlamaIndex + Chroma（本地持久化）+ Streamlit。

---

## 0. 已经帮你准备好的（无需重做）

| 项 | 状态 |
|----|------|
| Ollama 安装并运行 | ✅ `brew services start ollama` 已起 |
| 已拉模型 | ✅ `qwen2.5:1.5b`、`nomic-embed-text` |
| Python 依赖 | ✅ 装在 `py312` 环境（requirements.txt） |
| 向量索引 | ✅ `./storage` 已建，含 2 个块（来自 `data/sample.md`） |
| 网页服务 | ✅ http://localhost:8501 已在后台运行 |

> 只有**机器重启**或**手动关掉 streamlit** 后，才需要按下面第 1 步重启。

---

## 1. 启动 / 重启网页

```bash
# 1) 确保 Ollama 在跑（机器重启后通常要这步）
brew services start ollama        # 或：ollama serve &

# 2) 启动网页（在你装了依赖的 python 里跑）
cd /Users/xiaoman/WorkBuddy/2026-07-11-09-40-50/rag-assistant
/Users/xiaoman/miniconda3/envs/py312/bin/python -m streamlit run app.py --server.port 8501

# 3) 浏览器打开 http://localhost:8501
```

> 助手用的环境是 `py312`（conda）。你也可以用自己装好依赖的 python，效果一样。

---

## 2. 验证是否跑通

在网页输入框问：

> 知识蒸馏里的暗知识是什么？

应得到**基于 `data/sample.md` 的真实回答**，并在下方列出**引用来源**（点开可看原文片段和相似度分数）。出现这个画面 = P1 跑通 ✅

---

## 3. 换成你自己的资料

```bash
# 把你的文件（PDF / Markdown / 纯文本）放进 data/
cp 你的资料.pdf data/

# 重建索引（ingest.py 会自动清空旧库再重建，不会重复追加）
cd /Users/xiaoman/WorkBuddy/2026-07-11-09-40-50/rag-assistant
python ingest.py

# 刷新网页即可，无需重启 streamlit
```

注意：`data/` 下**所有**文件都会被纳入检索；删掉 `sample.md` 不影响已建索引，只是它不再被纳入下次的重建。

---

## 4. 调参（只改 config.py 一处）

| 参数 | 作用 | 怎么调 |
|------|------|--------|
| `CHUNK_SIZE` | 每块大小 | 文档句子长→768，短→256 |
| `CHUNK_OVERLAP` | 块间重叠 | 取 `CHUNK_SIZE` 的 10%~20% |
| `TOP_K` | 每次取几块 | 网页侧边栏滑块实时调；答案需多资料→调大 |
| `LLM_MODEL` | 生成模型 | 想更轻：`qwen2.5:0.5b`（改完先 `ollama pull qwen2.5:0.5b`） |

- 改 `CHUNK_SIZE` / `CHUNK_OVERLAP` → **必须重跑 `python ingest.py`** 重建索引。
- 只调 `TOP_K`（侧边栏滑块）→ **无需重建**，实时生效。

---

## 5. 量化评估质量（可选）

```bash
pip install ragas datasets
python eval.py
```

输出 4 个 RAGAS 指标：`faithfulness`（答案是否忠于资料，最重要）、`answer_relevancy`、`context_precision`、`context_recall`。

---

## 6. 常见问题

- **提问返回 `Empty Response`**：索引是空的。先重跑 `python ingest.py`。若仍空，检查 `config.py` 里 `COLLECTION` 是否 ≥3 字符、且 `ingest.py` 是否用 `StorageContext.from_defaults(vector_store=store)` 写库（这俩坑已修，照现有代码即可）。
- **连不上 Ollama**：`ollama serve &` 或 `brew services start ollama`。
- **端口 8501 被占用**：启动命令加 `--server.port 8502` 换端口，浏览器对应改端口。
- **首次回答很慢**：模型冷加载，之后明显变快，正常。

---

## 7. 下一步

P1 跑通后 → **P2 多工具 Agent**（同一台 Mac，同款 Ollama，无需新算力）。随时让助手把 P2 脚手架铺好，你照这份 RUNBOOK 同样的"代跑 + 文档"节奏推进即可。

---
*本手册基于 2026-07-12 实际跑通的版本编写；此前踩的两个坑（Chroma 集合名 ≥3 字符、LlamaIndex 新版须用 `StorageContext` 写库）均已修复，照做不会再踩。*
