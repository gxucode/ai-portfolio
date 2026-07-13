# 学习资源清单(对齐路线:RAG → Agent → 微调 → 部署)

> 给本机 M4/16G + 免费 Colab 的学习者。优先免费、官方、可动手的课程。
> 原则:先看官方文档和 star 高的 GitHub,少看营销号。

## 一、你 P1 技术栈的官方文档(最权威,优先看)
- LlamaIndex 文档:https://docs.llama-index.ai
- Chroma 向量库:https://docs.trychroma.com
- Ollama(含模型库):https://ollama.com  /  https://ollama.com/library
- Streamlit:https://docs.streamlit.io
- Hugging Face:https://huggingface.co/docs

## 二、免费系统课程(按学习顺序)

### 应用层 / RAG
- DeepLearning.AI《Chat with Your Data》——RAG 最干净入门,约 1h,免费
  https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/
- freeCodeCamp《Learn RAG From Scratch》(Lance Martin,从原理讲,约 2.5h)——在 freeCodeCamp 的 YouTube 搜 "RAG from scratch Lance Martin"
- DeepLearning.AI《Building Agentic RAG with LlamaIndex》——免费 2h,正对你 P1 技术栈
- DataWhale《LLM-Universe》——中文最强 RAG 实战教程,含完整代码
  https://github.com/datawhalechina/llm-universe

### Agent(对应 P2)
- Hugging Face《AI Agents Course》——免费 ~25h,从 0 到 1,带 Colab 练习 + 证书
  https://huggingface.co/learn/agents-course
- LangChain Academy《Intro to LangGraph》——免费,状态机式 Agent,正对 P2
  https://academy.langchain.com/courses/intro-to-langgraph
- DeepLearning.AI《Agentic Design Patterns》——Andrew Ng 讲 4 种 Agent 模式
- Microsoft《AI Agents for Beginners》——免费开源课程
  https://github.com/microsoft/ai-agents-for-beginners
- Anthropic《Building MCP Servers》——MCP 协议标准教程
  https://academy.anthropic.com

### 微调 / 部署(对应阶段二)
- Hugging Face《LLM Course》——免费,微调 + 部署,有证书
  https://huggingface.co/learn/llm-course
- DeepLearning.AI《Finetuning Large Language Models》——LoRA/QLoRA 入门
- PEFT / LoRA 官方指南:https://huggingface.co/docs/peft/conceptual_guides/lora

## 三、中文视频 / 社区(适合入门与跟练)
- B站 搜索:"RAG 全链路教程"、"AI Agent 开发 从0到1"、"LangChain 教程"
  - RAG 全链路示例:https://www.bilibili.com/video/BV1KZdhBgEmb
  - Agent 开发示例:https://www.bilibili.com/video/BV1iUwkzqEz4
- 掘金《AI Agent 应用开发 10 周路线》(含每日任务,就业级)
  https://juejin.cn/post/7658132883367379007
- 知乎 搜索:"大模型 RAG 从 0 到 1 实战"
- CSDN 博客清单(谨慎筛选,避开标题党):搜索 "2026 大模型开发 博客清单"

## 四、搜索关键词(去哪搜)
- 中文平台(知乎 / B站 / 掘金 / 微信公众号):
  "RAG 实战"、"AI Agent 开发"、"大模型 微调 LoRA"、"LangGraph 教程"、"Vector Database 选型"
- 全球平台(YouTube / GitHub):
  "RAG from scratch langchain"、"LangGraph tutorial"、"Hugging Face agents course"、
  GitHub 搜 "awesome-llm"、"llm-course"、"genai-agents"

## 五、新手避坑
1. 别一上来啃 Transformer 数学公式——先跑通一个本地模型再说。
2. 别盲目追大模型参数——M4/16G 先把 0.5B~3B 跑熟。
3. 别只看教程不写代码——每个教程都要自己敲一遍、改一遍。
4. 优先官方文档 + GitHub star 高的项目,少看营销号。
5. 评估很重要——RAG 跑通后看 DeepLearning.AI 的 RAG 评估短课(RAG triad:上下文相关 / 有据 / 答案相关)。

## 六、推荐学习顺序(对齐你的项目路线)
- P1(RAG):LlamaIndex 文档 + DataWhale LLM-Universe + DeepLearning.AI Chat with Your Data
  → 把本仓库 rag-assistant 跑通、改 config.py 体会分块/检索
- P2(Agent):Hugging Face Agents Course + LangChain Academy LangGraph
- 阶段二(微调):Hugging Face LLM Course + DeepLearning.AI Finetuning + Colab 免费 T4 动手
- 阶段三(作品集):把前三步合成一个可演示的垂直领域项目
