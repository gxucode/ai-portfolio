# P1 本地知识库 RAG 助手 · 动手清单

> 学习方式：动手跑通 + 改代码，不依赖视频。  
> 每完成一步，把前面的 `[ ]` 改成 `[x]`。  
> 默认模型 `qwen2.5:1.5b`（约 1GB）；想更轻更快用 `qwen2.5:0.5b`（约 0.4GB）。

## 环境准备（本机 M4）

- [x] **第 1 步 · 装 Ollama**（助手已后台帮你跑，装好会提示）  
  `bash
      brew install ollama
      `
- [x] **第 2 步 · 启动 Ollama 服务**（终端里跑一次，保持后台）  
  `bash
      ollama serve &
      `
- [x] **第 3 步 · 拉取两个模型**（首次会下载）  
  `bash     # 默认（推荐，约 1GB）
      ollama pull qwen2.5:1.5b     # 想更轻更快（约 0.4GB）：把上面换成下面这行     # ollama pull qwen2.5:0.5b
      ollama pull nomic-embed-text
      `  
  \> 若用 0.5b，记得把 `config.py` 里的 `LLM_MODEL` 改成 `"qwen2.5:0.5b"`。

## 跑通 P1

- [x] **第 4 步 · 安装 Python 依赖**  
  `bash
      cd /Users/xiaoman/WorkBuddy/2026-07-11-09-40-50/rag-assistant
      pip install -r requirements.txt
      `
- [x] **第 5 步 · 建索引**（把 data/ 下的文档变成可检索的向量库，只需一次）  
  `bash
      python ingest.py
      `
- [x] **第 6 步 · 跑网页界面**  
  `bash
      streamlit run app.py
      `  
  然后浏览器打开 <http://localhost:8501>
- [ ] **第 7 步 · 验证效果**：在界面里问  
  \> “知识蒸馏里的暗知识是什么？”  
  看它是否**基于 sample.md 回答**，并在下方列出**引用来源**。  
  能答上来 + 有引用 = P1 跑通 ✅

## 吃透（跑通后再做，别跳）

- [ ] **改 config.py**：把 `CHUNK_SIZE` / `TOP_K` 调大调小，重新 `python ingest.py` + 刷新页面，  
  观察回答质量的变化（这是理解 RAG 检索的关键实验）
- [ ] **试更小模型**：把 `config.py` 的 `LLM_MODEL` 改成 `"qwen2.5:0.5b"`，  
  `ollama pull qwen2.5:0.5b` 后重跑，体会"模型小了回答会怎样变弱"
- [ ] **跑评估**：`python eval.py`，看 RAGAS 四项指标  
  （faithfulness 答案是否忠于资料 / answer_relevancy / context_precision / context_recall）
- [ ] **换你自己的资料**：把 `data/` 里的 `sample.md` 换成你的 PDF / Markdown / 笔记，重跑第 5、6 步

## 完成后衔接

- P1 跑通且能改参数、能换文档 → 进 **P2 多工具 Agent**（同一台 Mac，同款 Ollama）

---

卡住就看 `README.md`（含原理图 + 排错 + 模型大小选择）。不要去看视频，直接改代码、看结果。
